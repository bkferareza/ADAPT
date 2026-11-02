"""Real filesystem experiments; approval declarations are synthetic test data."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import uuid

from fixtures import FRAMEWORK
import test_recovery_plan_review as reviewed
import test_recovery_runtime as runtime_tests

spec = importlib.util.spec_from_file_location(
    "execution", FRAMEWORK / "VALIDATION/recovery_execution.py")
execution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(execution)


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.f = reviewed.PlanReviewTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        control = self.f.root / execution.runtime.op.CP
        text = control.read_text(encoding="utf-8").replace("| Blocked | NO |", "| Blocked | YES |")
        text = text.replace("| ActiveBlockers | NONE |", "| ActiveBlockers | BLK-900 |")
        text = text.replace("| ExecutionReadiness | NEEDS_PLANNING |", "| ExecutionReadiness | BLOCKED |")
        control.write_text(text, encoding="utf-8")
        (self.f.root / "attempt-history.json").write_bytes(b'{"attempts":2,"exhausted":true}')
        self.f.plan["proposed"] = execution.structural.plan(self.f.root, self.f.scope)
        self.f.plan["request"]["inputs"] = [
            {"path": path, "sha256": digest, "verified_at": self.f.human.checked}
            for path, digest in self.f.plan["proposed"]["baseline"].items()]
        self.f.plan["request"]["operation_reference"] = "SYNTHETIC-RE-" + uuid.uuid4().hex
        self.f.authorize()
        self.bind()

    def bind(self):
        self.plan, self.authorization = self.f.plan, self.f.authorization
        self.context = {"mode": "SYNTHETIC_TEST_ONLY",
                        "binding": deepcopy(self.authorization["human_authorization"]["binding"])}
        self.root = Path(self.plan["request"]["target"]["root"])
        self.external = Path(self.plan["evidence_root"])

    def context_plan(self):
        fixture = runtime_tests.RuntimeTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        request = deepcopy(self.f.human.packet)
        for key in ("target", "purpose", "task", "executor", "writes", "inputs",
                    "evidence", "ids", "completion"):
            request[key] = deepcopy(fixture.packet[key])
        request["operation_reference"] = "SYNTHETIC-RE-" + uuid.uuid4().hex
        request["gates"] = {key: "APPROVED" for key in
                            fixture.f.fixture.records["authorization"]["gates"]}
        self.f.plan = {"kind": "CONTEXT", "proposed": fixture.plan, "request": request,
                       "packet": deepcopy(fixture.packet), "evidence_root": str(fixture.external)}
        self.f.authorize()
        self.f.authorization["maintenance_scope"].update(
            workcell=request["workcell"], executor=request["executor"],
            required_gates=list(request["gates"]))
        self.bind()
        return fixture

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def run_action(self):
        result = execution.execute_reviewed(self.plan, self.authorization, self.context)
        self.assertEqual("STOP", result["action"])
        self.assertFalse(result["operational_authority"])
        self.assertEqual("UNAUTHORIZED", result["real_execution"])
        return result

    def success(self):
        before = deepcopy((self.plan, self.authorization, self.context))
        result = self.run_action()
        self.assertEqual("SYNTHETIC_REVIEWED_EXECUTION_VALIDATED", result["status"], result)
        self.assertEqual(before, (self.plan, self.authorization, self.context))
        self.assertEqual(result, json.loads(Path(result["outcome"]).read_bytes()))
        claim = json.loads(Path(result["claim"]).read_bytes())
        self.assertEqual(self.plan, claim["plan"])
        self.assertEqual(result["review_sha256"], claim["review_sha256"])
        self.assertEqual(result["journal_sha256"],
                         execution.pre.digest(Path(result["journal"]).read_bytes()))
        return result

    def refusal(self):
        before = self.snapshot()
        result = self.run_action()
        self.assertEqual("REFUSED", result["status"], result)
        self.assertEqual(before, self.snapshot())
        return result

    def test_RE01_reviewed_structural_executes(self):
        self.assertEqual("SYNTHETIC_REPAIR_VALIDATED", self.success()["writer"]["status"])
        self.assertTrue((self.root.parent / (self.root.name + ".structural.lock")).exists())

    def test_RE02_reviewed_context_executes(self):
        self.context_plan()
        self.assertEqual(7, self.success()["audit"]["completed_operations"])

    def test_RE03_missing_authorization(self):
        for value in (None, {}, {"approved": True}):
            self.authorization = value
            self.refusal()

    def test_RE04_modified_plan_fingerprint(self):
        self.plan["proposed"]["plan_sha256"] = "0" * 64
        self.refusal()

    def test_RE05_modified_review_fingerprint(self):
        self.authorization["human_authorization"]["binding"]["ids"]["review"]["review_sha256"] = "0" * 64
        self.refusal()

    def test_RE06_wrong_target_operation_task_actor_and_reference(self):
        original = deepcopy(self.context)
        for key, value in (("target", {"root": str(self.external), "identity": "WRONG"}),
                           ("operation_reference", "OTHER"), ("task", "OTHER"),
                           ("executor", "OTHER")):
            self.context = deepcopy(original)
            self.context["binding"][key] = value
            self.refusal()
        self.context = original
        self.plan["proposed"]["scope"]["operation"] = "OTHER"
        self.refusal()

    def test_RE07_changed_source_before_image_evidence_and_occupied_path(self):
        self.f.path.write_bytes(self.f.path.read_bytes() + b"changed")
        self.refusal()
        fixture = self.context_plan()
        path = self.root / fixture.f.fixture.source
        original = path.read_bytes()
        path.write_bytes(original + b"changed")
        self.refusal()
        path.write_bytes(original)
        created = next(w for w in self.plan["proposed"]["write_set"] if w["operation"] == "create")
        occupied = self.root / created["path"]
        occupied.write_bytes(b"occupied")
        self.refusal()
        occupied.unlink()
        evidence = self.external / next(iter(self.plan["request"]["evidence"].values()))["path"]
        evidence.write_bytes(evidence.read_bytes() + b"changed")
        self.refusal()

    def test_RE08_unapproved_scope(self):
        self.plan["request"]["writes"][0]["fields"] = ["Status"]
        self.refusal()

    def test_RE09_expired_withdrawn(self):
        auth = self.authorization["human_authorization"]
        end = auth["expires_at"]
        auth["expires_at"] = self.f.human.start
        self.refusal()
        auth["expires_at"] = end
        auth["withdrawn"] = True
        self.refusal()

    def test_RE10_reference_is_single_use_across_targets_and_kinds(self):
        reference = self.plan["request"]["operation_reference"]
        result = self.success()
        self.refusal()
        self.context_plan()
        self.plan["request"]["operation_reference"] = reference
        self.f.authorize()
        self.f.authorization["maintenance_scope"].update(
            workcell=self.plan["request"]["workcell"], executor=self.plan["request"]["executor"],
            required_gates=list(self.plan["request"]["gates"]))
        self.bind()
        refused = self.refusal()
        self.assertIn("CONSUMED_OR_CONFLICTING_REFERENCE", refused["findings"])
        self.assertTrue(Path(result["claim"]).exists())

    def test_RE11_interrupted_operations_never_continue(self):
        def interrupt(event):
            if event == "after_intent":
                raise ValueError("synthetic interruption")
        with patch.object(execution.structural, "_checkpoint", side_effect=interrupt):
            result = self.run_action()
        self.assertEqual("INTERRUPTED", result["status"], result)
        self.assertEqual("INTERRUPTED", result["writer"]["status"])
        journal = self.external / "journal.jsonl"
        before = journal.read_bytes()
        self.refusal()
        self.assertEqual(before, journal.read_bytes())
        self.assertTrue(Path(result["claim"]).exists())
        self.context_plan()
        def interrupt_context(event, sequence):
            if event == "after_mutation" and sequence == 1:
                raise ValueError("synthetic interruption")
        with patch.object(execution.runtime, "_checkpoint", side_effect=interrupt_context):
            result = self.run_action()
        self.assertEqual("INTERRUPTED", result["status"], result)
        self.refusal()

    def test_RE12_structural_preserves_governance_and_exact_row(self):
        before = self.snapshot()
        fields = deepcopy(self.plan["proposed"]["fields"])
        self.success()
        after = self.snapshot()
        self.assertEqual({execution.pre.BLOCKERS}, {p for p in after if before.get(p) != after[p]})
        data = after[execution.pre.BLOCKERS]
        self.assertEqual(bytes.fromhex(self.plan["proposed"]["after_image_hex"]), data)
        self.assertEqual(fields, execution.structural._repair(data, "BLK-900")[1])
        self.assertEqual("OPEN", fields[8])
        self.assertEqual("YES", execution.runtime.op.state(self.root)["Blocked"])

    def test_RE13_context_relationships_and_preserved_stale_records(self):
        self.context_plan()
        before = self.snapshot()
        result = self.success()
        plan, op, pre = self.plan["proposed"], execution.runtime.op, execution.pre
        docs = {kind: next(w for w in plan["write_set"] if Path(w["path"]).stem == plan["ids"][kind])
                for kind in ("CP", "CD", "HO")}
        texts = {kind: (self.root / write["path"]).read_text(encoding="utf-8-sig")
                 for kind, write in docs.items()}
        self.assertEqual(plan["ids"]["CP"], op.headers(texts["CD"], ["PRECEDING_CONTEXT_PACK_ID"])["PRECEDING_CONTEXT_PACK_ID"])
        self.assertEqual(plan["ids"]["CP"], op.headers(texts["HO"], ["CONTEXT_PACK_REFERENCE"])["CONTEXT_PACK_REFERENCE"])
        self.assertIn(plan["ids"]["CD"], op.section(texts["HO"], "Context Delta Reference"))
        self.assertTrue((self.root / pre.STALE).read_bytes().startswith(before[pre.STALE]))
        self.assertFalse(result["writer"]["validation"]["ordinary_context_activation"])
        self.assertEqual("ARCHIVED", op.table(op.text(self.root, pre.INDEX), "Index", ["Status"])[-1]["Status"])
        self.assertEqual(before[pre.BLOCKERS], (self.root / pre.BLOCKERS).read_bytes())

    def test_RE14_final_filesystem_hashes_match_approved_artifacts(self):
        self.context_plan()
        result = self.success()
        for write in self.plan["proposed"]["write_set"]:
            actual = (self.root / write["path"]).read_bytes()
            self.assertEqual(write["proposed_final_sha256"], execution.pre.digest(actual))
            self.assertEqual(bytes.fromhex(write["after_image_hex"]), actual)
        self.assertEqual(result["final_hashes"], result["audit"]["final_hashes"])

    def test_RE15_actual_ADAPT_DEV_rejected_before_review(self):
        self.plan["request"]["target"]["root"] = str(FRAMEWORK.parent / "ADAPT-DEV/ADAPT")
        with patch.object(execution.review, "validate_review", side_effect=AssertionError("must not reach")) as validator:
            self.refusal()
            validator.assert_not_called()

    def test_RE16_synthetic_cannot_enable_production(self):
        for mode in ("PRODUCTION", "HUMAN_SUPERVISED", None):
            self.context["mode"] = mode
            self.refusal()
        self.context["mode"] = "SYNTHETIC_TEST_ONLY"
        self.authorization["human_authorization"]["synthetic"] = False
        self.refusal()
        self.authorization["human_authorization"]["synthetic"] = True
        self.plan["request"]["target"]["root"] = str(FRAMEWORK)
        self.refusal()

    def test_RE17_exactly_one_writer_dispatched(self):
        with patch.object(execution.runtime, "execute", side_effect=AssertionError("no chaining")):
            self.success()
        self.context_plan()
        with patch.object(execution.structural, "execute", side_effect=AssertionError("no chaining")):
            self.success()

    def test_RE18_existing_ownership_and_journal_protections(self):
        owner = self.root.parent / (self.root.name + ".structural.lock")
        owner.write_bytes(b"prior interruption")
        self.refusal()
        self.assertEqual(b"prior interruption", owner.read_bytes())
        self.context_plan()
        journal = self.external / self.plan["proposed"]["journal"]["path"]
        journal.parent.mkdir(parents=True, exist_ok=True)
        journal.write_bytes(b"prior interruption")
        self.refusal()
        self.assertEqual(b"prior interruption", journal.read_bytes())

    def test_claim_without_outcome_and_conflicting_identity_refuse(self):
        key = execution.pre.digest(self.plan["request"]["operation_reference"].encode())
        claims = execution.EVIDENCE_ROOT / "references"
        claims.mkdir(parents=True, exist_ok=True)
        path = claims / (key + ".claim.json")
        path.write_bytes(b"partial claim")
        result = self.refusal()
        self.assertIn("CONSUMED_OR_CONFLICTING_REFERENCE", result["findings"])
        self.assertEqual(b"partial claim", path.read_bytes())

    def test_independent_audit_failure_cannot_report_success(self):
        with patch.object(execution.structural, "audit", return_value={"status": "INTERRUPTED"}):
            result = self.run_action()
        self.assertEqual("INTERRUPTED", result["status"])
        self.assertEqual("SYNTHETIC_REPAIR_VALIDATED", result["writer"]["status"])
        self.assertEqual(result, json.loads(Path(result["outcome"]).read_bytes()))

    def test_reference_consumed_before_dispatch_and_expiry_rechecked(self):
        validate = execution.review.validate_review
        calls = []
        def expire(plan, authorization):
            calls.append(True)
            if len(calls) == 2:
                return {"valid": False}
            return validate(plan, authorization)
        before = self.snapshot()
        with patch.object(execution.review, "validate_review", side_effect=expire), \
             patch.object(execution.structural, "execute") as writer:
            result = self.run_action()
            writer.assert_not_called()
        self.assertEqual("INTERRUPTED", result["status"])
        self.assertEqual(before, self.snapshot())
        self.refusal()

    def test_second_invocation_after_claim_cannot_dispatch(self):
        persist = execution.runtime._persist_new
        second = []
        def competing(path, data):
            persist(path, data)
            if path.name.endswith(".claim.json"):
                second.append(self.run_action())
        with patch.object(execution.runtime, "_persist_new", side_effect=competing):
            self.success()
        self.assertEqual(1, len(second))
        self.assertEqual("REFUSED", second[0]["status"])
        self.assertIn("CONSUMED_OR_CONFLICTING_REFERENCE", second[0]["findings"])

    def test_structural_LF_preserved(self):
        self.f.path.write_bytes(self.f.path.read_bytes().replace(b"\r\n", b"\n"))
        self.f.scope["before_sha256"] = execution.pre.digest(self.f.path.read_bytes())
        self.plan["proposed"] = execution.structural.plan(self.root, self.f.scope)
        self.plan["request"]["writes"][0]["before_sha256"] = self.plan["proposed"]["before_sha256"]
        for item in self.plan["request"]["inputs"]:
            item["sha256"] = self.plan["proposed"]["baseline"][item["path"]]
        self.f.authorize()
        self.bind()
        self.success()
        self.assertNotIn(b"\r", self.f.path.read_bytes())


if __name__ == "__main__":
    unittest.main()
