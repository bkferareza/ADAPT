"""Structural contract conformance; synthetic approval never governs real work.

Agent-guided scaffold acceptance is executed and recorded separately.
"""
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
