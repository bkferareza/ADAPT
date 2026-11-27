"""Structural contract conformance; synthetic approval never governs real work.

Agent-guided scaffold acceptance is executed and recorded separately.
"""
import importlib.util
from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fixtures import FRAMEWORK, fresh_instance

spec = importlib.util.spec_from_file_location("bootstrap_case", FRAMEWORK / "VALIDATION/bootstrap_case.py")
case = importlib.util.module_from_spec(spec)
spec.loader.exec_module(case)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "ADAPT"
        fresh_instance(self.root)
        self.basis = case.inputs(self.root)

    def reject(self, reason):
        before = case.snapshot(self.root)
        with self.assertRaisesRegex(case.Stop, reason):
            case.fresh(self.root, self.basis)
        self.assertEqual(before, case.snapshot(self.root), "Conformance checking must not mutate")

    def test_fresh_canonical_eligible_and_readonly(self):
        before = case.snapshot(self.root)
        self.assertEqual(case.fresh(self.root, self.basis), "PASS_INITIAL_BASIS")
        self.assertEqual(before, case.snapshot(self.root))

    def test_missing_approval(self):
        (self.root / case.APPROVAL).unlink()
        self.reject("MISSING_APPROVAL")

    def test_mismatched_document_approval(self):
        data = json.loads(case.read(self.root, case.APPROVAL))
        data["document"] = "wrong.txt"
        case.write(self.root, case.APPROVAL, json.dumps(data))
        self.basis["approval_sha256"] = case.sha(self.root / case.APPROVAL)
        self.reject("APPROVAL_SCOPE")

    def test_gate1_required(self):
        data = json.loads(case.read(self.root, case.APPROVAL))
        data["gate"] = 2
        case.write(self.root, case.APPROVAL, json.dumps(data))
        self.basis["approval_sha256"] = case.sha(self.root / case.APPROVAL)
        self.reject("GATE_1")

    def test_changed_approval_binding(self):
        (self.root / case.APPROVAL).write_bytes((self.root / case.APPROVAL).read_bytes() + b"\n")
        self.reject("BINDING_CHANGED")

    def test_changed_request_binding(self):
        case.append(self.root, case.REQUEST, "changed scope")
        self.reject("BINDING_CHANGED")

    def test_missing_source(self):
        (self.root / case.SOURCE).unlink()
        self.reject("SOURCE_MISSING")

    def test_altered_source(self):
        case.append(self.root, case.SOURCE, "changed")
        self.reject("SOURCE_HASH")

    def test_incomplete_source(self):
        self.basis["source_complete"] = False
        self.reject("SOURCE_INCOMPLETE")

    def test_unreadable_source(self):
        original = Path.read_bytes
        def blocked(path):
            if path == self.root / case.SOURCE:
                raise PermissionError("Synthetic fixture unreadable")
            return original(path)
        with patch.object(Path, "read_bytes", blocked):
            with self.assertRaisesRegex(case.Stop, "SOURCE_UNREADABLE"):
                case.fresh(self.root, self.basis)

    def test_unauthorized_writer(self):
        self.basis["writer"] = "Backend Workcell"
        self.reject("WRITER")

    def test_adjacent_director_action(self):
        self.basis["action"] = "Director consolidate cycle"
        self.reject("ADJACENT_ACTION")

    def test_product_mutation(self):
        self.basis["allowed_writes"] = [*case.WRITES, "src/product.py"]
        self.reject("MUTATION_BOUNDARY")

    def test_unauthorized_adjacent_register_mutation(self):
        self.basis["allowed_writes"] = [*case.WRITES, "02_DIRECTOR_LANE/ACCEPTED_WORK_REGISTER.md"]
        self.reject("MUTATION_BOUNDARY")

    def test_existing_promotion(self):
        case.append(self.root, case.LOG, "\n| SOURCE_TRUTH_V0.1 | prior.txt | ACTIVE |\n")
        self.reject("PROMOTION_HISTORY")

    def test_archived_promotion_survives_reset(self):
        case.write(self.root, "06_HANDOFFS/ARCHIVE/history.md", "| SOURCE_TRUTH_V0.1 | old.txt | SUPERSEDED |\n")
        case.set_state(self.root, SourceTruthVersion="NONE", CurrentPhase="INITIALIZED")
        self.basis["state"] = case.state(self.root)
        self.reject("PROMOTION_HISTORY")

    def test_partial_write_process_exit(self):
        code = "import pathlib,sys; p=pathlib.Path(sys.argv[1]); p.write_bytes(p.read_bytes()+b'\\nBOOTSTRAP_ATTEMPT: interrupted test\\n'); raise SystemExit(97)"
        result = subprocess.run([sys.executable, "-B", "-c", code, str(self.root / case.DEC)], capture_output=True)
        self.assertEqual(result.returncode, 97)
        self.assertEqual(case.state(self.root)["CurrentPhase"], "INITIALIZED")
        self.reject("RECORDED_ATTEMPT")

    def test_repeated_attempt_even_after_state_reset(self):
        case.append(self.root, case.INTAKE, "\nBOOTSTRAP_ATTEMPT: partial\n")
        case.set_state(self.root, SourceTruthVersion="NONE", CurrentPhase="INITIALIZED")
        self.basis["state"] = case.state(self.root)
        self.reject("RECORDED_ATTEMPT")

    def test_invalid_handoff_workcell_binding(self):
        case.set_state(self.root, ActiveHandoff="HO-9999", ActiveWorkcell="NONE")
        self.basis["state"] = case.state(self.root)
        self.reject("ACTIVE_BINDING")

    def test_active_handoff_artifact(self):
        case.write(self.root, "06_HANDOFFS/ACTIVE/HO-9999.md", "STATUS: ACTIVE\n")
        self.reject("ACTIVE_ARTIFACT")

    def test_loading_is_not_fresh_eligibility(self):
        case.set_state(self.root, CurrentPhase="SOURCE_TRUTH_LOADING")
        self.basis["state"] = case.state(self.root)
        self.reject("INITIAL_STATE")

    def test_uncertain_history(self):
        self.basis["history_complete"] = False
        self.reject("HISTORY_UNCERTAIN")

    def test_contract_changed(self):
        case.append(self.root, "00_FRAMEWORK/SOURCE_AUTHORITY_POLICY.md", "\nchanged\n")
        self.reject("CONTRACT_CHANGED")

    def test_ordinary_promotion_without_context(self):
        with self.assertRaisesRegex(case.Stop, "ORDINARY_CONTEXT_MISSING"):
            case.ordinary(self.root, None)

    def test_schema_command_and_stop_inventory_preserved(self):
        command = case.read(self.root, "15_COMMANDS_AND_DRIVERS/COMMAND_REGISTRY.md")
        schema = case.read(self.root, "15_COMMANDS_AND_DRIVERS/CONTROL_PLANE_SCHEMA.md")
        stop = case.read(self.root, "15_COMMANDS_AND_DRIVERS/STOP_RULES.md")
        self.assertEqual(len(re.findall(r"^\| \d+ \|", command, re.M)), 18)
        self.assertEqual(len(re.findall(r"^### \w+\s*$", schema, re.M)), 21)
        self.assertEqual(len(re.findall(r"^### Stop Rule \d+", stop, re.M)), 15)
        self.assertIn("no-override", case.read(self.root, "07_GUARDRAILS/CONTEXT_GUARDRAIL.md"))

    def test_invalid_steward_handoff_stops_before_write(self):
        case.set_state(self.root, SourceTruthVersion=case.VERSION, CurrentAuthority="Context Steward", CurrentPhase="SOURCE_TRUTH_READY", ExecutionReadiness="NEEDS_CONTEXT")
        case.write(self.root, case.HO, "STATUS: ACTIVE\nHANDOFF_ID: HO-0001\nFROM_LANE: Director Lane\nTO_WORKCELL / TO_LANE: Backend Workcell\nSOURCE_TRUTH_VERSION: " + case.VERSION + "\n")
        before = case.snapshot(self.root)
        with self.assertRaisesRegex(case.Stop, "STEWARD_HANDOFF_BINDING"):
            case.steward_request(self.root, self.basis)
        self.assertEqual(before, case.snapshot(self.root))

    def test_steward_cannot_use_workcell_bound_handoff(self):
        case.set_state(self.root, SourceTruthVersion=case.VERSION, CurrentAuthority="Context Steward", CurrentPhase="SOURCE_TRUTH_READY", ActiveHandoff="HO-9999")
        with self.assertRaisesRegex(case.Stop, "STEWARD_BINDING"):
            case.steward_request(self.root, self.basis)

    def test_mode_a_candidate_comparison_counts_include_discovery(self):
        case.extract(self.root, promoted=False)
        case.put_row(self.root, case.REGISTERS[1], "BI-002", ["BI-002", "Discovery", "Existing Python file", "NONE", "Discovery", "LOW", "DRAFT", "OBSERVED_EVIDENCE; CANDIDATE_TRUTH"])
        case.extract(self.root, promoted=True)
        self.assertIn("REQ/BI/AC=1/2/1", case.read(self.root, case.REGISTERS[0]))
        self.assertIn("OBSERVED_EVIDENCE; CANDIDATE_TRUTH", case.read(self.root, case.REGISTERS[1]))


class PostRegistrationConformanceTests(unittest.TestCase):
    """Seeded states only: no reconciliation writer or actual platform approvals."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "ADAPT"
        fresh_instance(self.root)
        self.basis = case.inputs(self.root)
        case.write(self.root, case.PRESERVED, case.read(self.root, case.SOURCE))
        case.extract(self.root, promoted=True)
        case.put_row(self.root, case.LOG, case.VERSION,
                     [case.VERSION, case.PRESERVED, "Requirements Document", "Director Lane",
                      case.DATE, case.ER + "; SYNTHETIC-GATE1-001", "NONE", "ACTIVE"])
        self.denied_intake = ("| INT-001 | " + case.DATE + " | SYNTHETIC-GATE1-001 | Promote " +
                              case.SOURCE + " as " + case.VERSION +
                              " | SOURCE_TRUTH | Director Lane | BLOCKED | "
                              "BOOTSTRAP_ATTEMPT: BT-001; permission denied at completion; attempt 1 |")
        self.denied_decision = ("| DEC-001 | BOOTSTRAP_ATTEMPT: BT-001 | " + case.DATE +
                                " | Original completion write DENIED; correction not yet used |")
        case.append(self.root, case.INTAKE, "\n" + self.denied_intake + "\n")
        case.append(self.root, case.DEC, "\n" + self.denied_decision + "\n")
        case.write(self.root, case.CD, "# CD-0001\nCONTEXT_DELTA_ID: CD-0001\n" +
                   case.VERSION + "; BT-001; synthetic promotion delta; no implementation.\n")
        case.write(self.root, case.HO, case.handoff(
            self.root, "HO-0001", "Context Steward", case.ER, case.CD, "NONE",
            "Synthetic registration/extraction complete; completion disposition outstanding.",
            "Assemble first ordinary pack for promotion review only after verified completion."))
        case.set_state(self.root, SourceTruthVersion=case.VERSION, CurrentPhase="SOURCE_TRUTH_READY",
                       ExecutionReadiness="NEEDS_CONTEXT", CurrentAuthority="Context Steward",
                       LastContextDelta="CD-0001", NextExpectedAction="Await verified completion")
        self.record = {
            "synthetic_fixture_only": True, "attempt": "BT-001",
            "bindings": {"source": case.SOURCE, "source_sha256": self.basis["source_sha256"],
                         "approval_sha256": self.basis["approval_sha256"],
                         "request_sha256": self.basis["request_sha256"],
                         "version": case.VERSION, "scope": "first promotion"},
            "denied_history": {case.INTAKE: self.denied_intake, case.DEC: self.denied_decision},
            "handoff_creation": {"synthetic_fixture_only": True, "platform_outcome": "ALLOWED",
                                 "original_response_reference": "SYNTHETIC-LAWFUL-HO-001",
                                 "handoff_sha256": case.sha(self.root / case.HO)},
            "evidence": {ref: case.sha(self.root / ref)
                         for ref in [case.LOG, case.CD, *case.REGISTERS, *case.CONTRACTS]},
            "recovery_ledger": "NO_INTERRUPTED_CLAIM"}
        self.save_record()
        self.auth = self.authorization()

    def save_record(self):
        case.write(self.root, case.ER, json.dumps(self.record, indent=2) + "\n")

    def authorization(self):
        # Declarations stand in for a reviewed fixture, never real-world permission.
        return {"synthetic_fixture_only": True, "approved": True, "withdrawn": False,
                "capacities": ["Human Framework Maintainer", "Human Director"],
                "response_reference": "SYNTHETIC-EXACT-RECOVERY-001",
                "binding": case.reconciliation_binding(self.root, self.basis),
                "platform": {"synthetic_fixture_only": True, "outcome": "ALLOWED",
                             "response_reference": "SYNTHETIC-PLATFORM-001"}}

    def check(self, authorization=None, **kwargs):
        before = case.snapshot(self.root)
        try:
            if kwargs.get("for_steward"):
                return case.steward_request(
                    self.root, self.basis,
                    reconciliation_authorization=self.auth if authorization is None else authorization,
                    reconciliation_validation=kwargs.get("validation"))
            return case.reconciliation_conformance(
                self.root, self.basis, self.auth if authorization is None else authorization, **kwargs)
        finally:
            self.assertEqual(before, case.snapshot(self.root), "Oracle must never mutate fixture bytes")

    def refuse(self, reason, **kwargs):
        with self.assertRaisesRegex(case.Stop, reason):
            self.check(**kwargs)

    def fixture_history(self, *states):
        # Directly seed observed lifecycle records; this does not run reconciliation.
        for state in states:
            case.append(self.root, case.DEC, 'SYNTHETIC_CORRECTION: ' +
                        json.dumps({"attempt": "BT-001", "state": state}) + "\n")

    def completed_fixture(self):
        self.fixture_history("RESERVED", "VALIDATED", "COMPLETE")
        auth = self.authorization()
        auth["steward_platform"] = deepcopy(auth["platform"])
        validation = {"synthetic_fixture_only": True, "attempt": "BT-001", "result": "PASS",
                      "reviewer": "Synthetic independent reviewer", "final_hashes": case.snapshot(self.root)}
        return auth, validation

    def test_valid_same_attempt_is_readonly_and_creates_no_duplicates(self):
        result = self.check()
        self.assertEqual("SYNTHETIC_SAME_ATTEMPT_ELIGIBLE", result["status"])
        self.assertFalse(result["operational_authority"])
        self.assertFalse(result["automatic_resume"])
        self.assertEqual("STOP", result["action"])
        self.assertEqual(1, len(re.findall(r'^\| SOURCE_TRUTH_V\d', case.real_rows(self.root / case.LOG), re.M)))
        self.assertEqual([self.root / case.HO], list((self.root / "06_HANDOFFS").rglob("HO-*.md")))
        self.assertIn(self.denied_intake, case.read(self.root, case.INTAKE))
        self.assertIn(self.denied_decision, case.read(self.root, case.DEC))

    def test_missing_or_withdrawn_approval_stops(self):
        for change, reason in [({"approved": False}, "RECOVERY_APPROVAL_MISSING"),
                               ({"withdrawn": True}, "RECOVERY_AUTHORITY_WITHDRAWN"),
                               ({"capacities": ["Human Director"]}, "RECOVERY_GOVERNANCE")]:
            with self.subTest(change=change):
                self.refuse(reason, authorization=dict(self.auth, **change))
        self.refuse("RECOVERY_APPROVAL_MISSING", authorization={})

    def test_unverified_or_denied_platform_permission_stops(self):
        for platform in ({}, dict(self.auth["platform"], outcome="UNVERIFIED"),
                         dict(self.auth["platform"], outcome="DENIED")):
            with self.subTest(platform=platform):
                self.refuse("RECOVERY_PLATFORM_UNVERIFIED", authorization=dict(self.auth, platform=platform))

    def test_exact_plan_cannot_expand_scope_or_change_target(self):
        for field, value in [("target", str(self.root.parent)), ("attempt", "BT-999"),
                             ("writes", [{"path": "src/product.py", "operation": "write"}]),
                             ("executor", "Backend Workcell")]:
            with self.subTest(field=field):
                auth = deepcopy(self.auth)
                auth["binding"][field] = value
                self.refuse("RECOVERY_PLAN_BINDING", authorization=auth)

    def test_denied_handoff_without_lawful_creation_provenance_stops(self):
        self.record["handoff_creation"]["platform_outcome"] = "DENIED"
        self.record["handoff_creation"].pop("original_response_reference")
        self.save_record()
        self.auth = self.authorization()  # New approval cannot legalize the old write.
        self.refuse("RECOVERY_HANDOFF_AUTHORITY")

    def test_changed_source_hash_stops(self):
        case.append(self.root, case.SOURCE, "changed")
        self.refuse("RECOVERY_SOURCE_HASH")

    def test_changed_approval_or_scope_stops(self):
        self.record["bindings"]["scope"] = "implementation"
        self.save_record()
        self.refuse("RECOVERY_BINDING")
        self.record["bindings"]["scope"] = "first promotion"
        self.save_record()
        case.append(self.root, case.APPROVAL, "\n")
        self.refuse("RECOVERY_APPROVAL_BINDING")

    def test_conflicting_attempt_identity_stops(self):
        self.record["attempt"] = "BT-002"
        self.save_record()
        self.refuse("RECOVERY_ATTEMPT")

    def test_consumed_handoff_stops_without_consuming_again(self):
        (self.root / case.CONSUMED).parent.mkdir(parents=True, exist_ok=True)
        (self.root / case.HO).rename(self.root / case.CONSUMED)
        self.refuse("RECOVERY_HANDOFF")

    def test_mismatched_or_duplicate_handoff_stops(self):
        original = case.read(self.root, case.HO)
        case.write(self.root, case.HO, original.replace("Context Steward", "Backend Workcell"))
        self.refuse("RECOVERY_HANDOFF_BINDING")
        case.write(self.root, case.HO, original)
        case.write(self.root, "06_HANDOFFS/ACTIVE/HO-0009.md", original)
        self.refuse("RECOVERY_HANDOFF_CONFLICT")

    def test_missing_required_evidence_stops(self):
        (self.root / case.CD).unlink()
        self.refuse("RECOVERY_EVIDENCE_MISSING")

    def test_changed_extraction_evidence_stops(self):
        case.append(self.root, case.REGISTERS[0], "unexplained extraction change")
        self.refuse("RECOVERY_ARTIFACT_HASH")

    def test_denied_history_cannot_be_rewritten_as_completed(self):
        case.write(self.root, case.INTAKE, case.read(self.root, case.INTAKE).replace("BLOCKED", "COMPLETE"))
        self.refuse("RECOVERY_DENIAL_HISTORY")

    def test_interrupted_recovery_ledger_claim_stops(self):
        self.record["recovery_ledger"] = "INTERRUPTED"
        self.save_record()
        self.refuse("RECOVERY_LEDGER_INTERRUPTED")

    def test_completed_reconciliation_cannot_repeat(self):
        self.completed_fixture()
        self.auth = self.authorization()
        self.refuse("RECOVERY_CORRECTION_USED")

    def test_correction_allowance_cannot_be_reset_by_claim_or_plane(self):
        self.fixture_history("RESERVED")
        self.record["remaining_corrections"] = 1  # Not an authority over durable history.
        self.save_record()
        case.set_state(self.root, LastAction="Reset claimed", CurrentPhase="SOURCE_TRUTH_READY")
        self.auth = self.authorization()
        self.refuse("RECOVERY_CORRECTION_USED")

    def test_partial_interruption_has_no_automatic_retry(self):
        self.fixture_history("RESERVED", "INTERRUPTED")
        case.append(self.root, case.ER, "\n")  # Seed a partial completion output, not a writer call.
        self.auth = self.authorization()
        for _ in range(2):
            self.refuse("RECOVERY_CORRECTION_USED")
        self.refuse("RECOVERY_COMPLETION_REQUIRED", for_steward=True)

    def test_steward_requires_verified_reconciliation(self):
        self.refuse("RECOVERY_COMPLETION_REQUIRED", for_steward=True)
        auth, validation = self.completed_fixture()
        before = case.snapshot(self.root)
        with self.assertRaisesRegex(case.Stop, "RECOVERY_APPROVAL_MISSING"):
            case.steward_request(self.root, self.basis)
        self.assertEqual(before, case.snapshot(self.root))
        self.refuse("RECOVERY_VALIDATION_REQUIRED", authorization=auth, for_steward=True)
        invalid = dict(validation, final_hashes={})
        self.refuse("RECOVERY_VALIDATION_REQUIRED", authorization=auth,
                    for_steward=True, validation=invalid)

    def test_steward_requires_own_current_execution_permission(self):
        auth, validation = self.completed_fixture()
        auth.pop("steward_platform")
        self.refuse("STEWARD_PLATFORM_UNVERIFIED", authorization=auth,
                    for_steward=True, validation=validation)

    def test_completed_fixture_admission_does_not_consume_or_execute(self):
        auth, validation = self.completed_fixture()
        result = self.check(authorization=auth, for_steward=True, validation=validation)
        self.assertEqual("SYNTHETIC_STEWARD_ADMISSION", result["status"])
        self.assertFalse(result["operational_authority"])
        self.assertEqual("STOP", result["action"])
        self.assertTrue((self.root / case.HO).is_file())
        self.assertFalse((self.root / case.CONSUMED).exists())
        self.assertFalse((self.root / case.PACK).exists())
        self.assertFalse((self.root / case.DELIVERY).exists())
        values = case.state(self.root)
        self.assertEqual("NEEDS_CONTEXT", values["ExecutionReadiness"])
        self.assertEqual("NONE", values["ActiveWorkcell"])
        self.assertEqual("NONE", values["ActiveHandoff"])
        self.assertIn(self.denied_intake, case.read(self.root, case.INTAKE))

    def test_ready_or_implementation_lane_is_out_of_bounds(self):
        for field, value in [("ExecutionReadiness", "READY"), ("ActiveWorkcell", "WC-001")]:
            with self.subTest(field=field):
                previous = case.state(self.root)[field]
                case.set_state(self.root, **{field: value})
                self.auth = self.authorization()
                self.refuse("RECOVERY_STATE_BOUNDARY")
                case.set_state(self.root, **{field: previous})

    def test_contract_references_and_unavailable_runtime_boundaries(self):
        title = "Post-Registration Completion Reconciliation"
        policy = " ".join(case.read(self.root, "00_FRAMEWORK/SOURCE_AUTHORITY_POLICY.md").split())
        for clause in [title, "existing one-correction allowance", "STOP before mutation",
                       "legitimate platform approval flow", "retroactively authorize a denied write",
                       "interrupted recovery-ledger claim", "Independently validate",
                       "No new source version", "Steward cannot repair"]:
            self.assertIn(clause, policy)
        for ref in ["00_FRAMEWORK/GOVERNANCE_RULES.md",
                    "15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_DIRECTOR.md",
                    "15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_CONTEXT_STEWARD.md"]:
            text = " ".join(case.read(self.root, ref).split())
            self.assertIn(title, text)
            self.assertIn("STOP", text)
            self.assertIn("Assisted Permissions", text)
        # These clauses are contract coverage, not execution/permission tests.
        self.assertIn("recheck current hashes", policy.lower())
        self.assertIn("never automatic retry", policy)


if __name__ == "__main__":
    unittest.main()
