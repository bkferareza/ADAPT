"""Checklist D: two separately authorized synthetic actions on one filesystem.

Retains all fixtures/evidence below the fixed acceptance root. This test harness
is not a production dispatcher. Only fault injection uses mocks; all plans,
reviews, validations, mutations and audits are the existing implementations.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

from fixtures import FRAMEWORK
import test_recovery_execution as existing
import test_recovery_assembly as assembly_tests
import test_recovery_preflight as preflight_tests
import test_recovery_supervised as human_tests

execution = existing.execution
sr, rt, pre = execution.structural, execution.runtime, execution.pre
EVIDENCE = rt.ACCEPTANCE_ROOT.parent


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class Scenario:
    """Acceptance fixture only. Operation 2 must be explicitly invoked by a test."""

    def __init__(self):
        rt.ACCEPTANCE_ROOT.mkdir(parents=True, exist_ok=True)
        self.base = Path(tempfile.mkdtemp(prefix="d-", dir=rt.ACCEPTANCE_ROOT)).resolve()
        self.f = preflight_tests.PreflightTests()
        # Reuse the real builder on this one instance; retain it as evidence.
        with patch.object(preflight_tests.tempfile, "TemporaryDirectory", return_value=
                          SimpleNamespace(name=str(self.base), cleanup=lambda: None)):
            self.f.setUp()
        self.root = self.f.root
        self.human = human_tests.SupervisedTests()
        self.human.setUp()
        self.f.change(pre.op.CP, lambda t: t.replace("BLK-901", "BLK-001").replace(
            "| ExecutionReadiness | NEEDS_PLANNING |", "| ExecutionReadiness | BLOCKED |"))
        path = self.root / pre.BLOCKERS
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        row = next(line for line in lines if line.startswith("| BLK-901 |"))
        path.write_text("".join(line for line in lines if line != row) + "\n" +
                        row.replace("BLK-901", "BLK-001"), encoding="utf-8")
        (self.root / "attempt-history.json").write_bytes(
            b'{"retry_limit":3,"attempts":3,"exhausted":true,"handoff":"HO-007"}\n')
        self.stale = "10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-090.md"
        (self.root / self.stale).write_text(
            "CONTEXT_PACK_ID: CP-090\nSTATUS: STALE\nHistorical ordinary context; unusable.\n",
            encoding="utf-8")
        self.f.change(pre.INDEX, lambda t: t +
            "\n| CP-090 | CONTEXT_STEWARD | HO-007 | SOURCE_TRUTH_V1.0 | S | 2026-10-18 | STALE | Exhausted ordinary assembly |\n")
        self.f.change(pre.STALE, lambda t: t +
            "\n| SC-090 | CP-090 | Ordinary context | Exhausted retries | Director | 2026-10-18 | HIGH | OPEN | Preserve |\n")
        self.pending = "06_HANDOFFS/ACTIVE/HO-007.md"
        (self.root / self.pending).write_text(
            "HANDOFF_ID: HO-007\nSTATUS: ACTIVE\nSynthetic pending handoff; must not be consumed.\n",
            encoding="utf-8")
        failure = deepcopy(self.f.records["failure"])
        failure.update(blockers={"BLK-001": "OPEN"}, state=pre.op.state(self.root))
        self.f.evidence("failure", failure)
        self.initial = self.snapshot("initial")
        self.history = rt._snapshot(self.base / "evidence")
        self.op1 = self.op2 = None

    def snapshot(self, name):
        try:
            pre.op.prompt_next(self.root)
            ordinary = {"refused": False}
        except pre.op.Problem as error:
            ordinary = {"refused": True, "code": error.code, "message": str(error)}
        result = {"root": str(self.root), "hashes": rt._snapshot(self.root),
                  "state": pre.op.state(self.root), "doctor": pre.op.doctor(self.root),
                  "ordinary": ordinary}
        save(self.base / (name + ".json"), result)
        return result

    def authorize(self, envelope):
        prepared = execution.review.prepare_review(envelope)
        config, approval = deepcopy(self.human.config), deepcopy(self.human.response)
        request = envelope["request"]
        config.update(target=deepcopy(request["target"]), workcell=request["workcell"],
                      executor=request["executor"], required_gates=list(request["gates"]))
        approval["binding"] = prepared["authorization_binding"]
        approval["audit_reference"] = request["audit_reference"]
        for item in approval["approvals"]:
            item["approval_reference"] = request["operation_reference"] + ":" + item["role"]
        authorization = {"maintenance_scope": config, "human_authorization": approval}
        external = Path(envelope["evidence_root"])
        save(external / "review.json", prepared)
        (external / "review.txt").write_text(prepared["text"], encoding="utf-8")
        save(external / "authorization.json" if envelope["kind"] == "STRUCTURAL" else
             external / "reviewed-authorization.json", authorization)
        save(external / "review-validation.json",
             execution.review.validate_review(envelope, authorization))
        save(external / "envelope.json", envelope)
        return authorization, {"mode": "SYNTHETIC_TEST_ONLY",
                               "binding": deepcopy(approval["binding"])}

    def request(self, operation):
        request = deepcopy(self.human.packet)
        request.update(target={"root": str(self.root), "identity": "Fixture"},
                       task="SYNTHETIC-D-" + operation,
                       operation_reference="SYNTHETIC-D-" + operation + "-" + uuid.uuid4().hex,
                       audit_reference="SYNTHETIC-D-AUDIT-" + operation)
        return request

    def prepare_structural(self):
        external = self.base / "operation-1"
        external.mkdir()
        scope = {"governance": "HUMAN_SUPERVISED", "human": "synthetic-maintainer",
                 "target": str(self.root), "path": pre.BLOCKERS, "operation": sr.OPERATION,
                 "blocker": "BLK-001", "before_sha256": self.initial["hashes"][pre.BLOCKERS]}
        proposed = sr.plan(self.root, scope)
        request = self.request("STRUCTURAL")
        request.update(writes=[{"path": pre.BLOCKERS, "operation": "set_fields",
                                "fields": ["placement"], "before_sha256": proposed["before_sha256"]}],
                       inputs=[{"path": p, "sha256": h, "verified_at": self.human.checked}
                               for p, h in proposed["baseline"].items()],
                       ids={"blocker": "BLK-001"},
                       completion={"expected": "Relocate exact eleven values; preserve OPEN; return to both humans; STOP"})
        proof = b"SYNTHETIC ONLY: prearranged structural review; separate Director and Maintainer declarations.\n"
        (external / "synthetic.txt").write_bytes(proof)
        request["evidence"] = {"synthetic": {"path": "synthetic.txt", "sha256": pre.digest(proof)}}
        self.plan1 = {"kind": "STRUCTURAL", "proposed": proposed, "request": request,
                      "evidence_root": str(external)}
        self.auth1, self.context1 = self.authorize(self.plan1)

    def structural(self):
        self.prepare_structural()
        self.op1 = execution.execute_reviewed(self.plan1, self.auth1, self.context1)
        save(self.base / "operation-1-result.json", self.op1)
        self.between = self.snapshot("between")
        # End of this invocation. Nothing prepares or invokes Operation 2 here.
        return self.op1

    def prepare_context(self):
        # Harness transition gate: even an interruption after replacement cannot
        # silently become permission to prepare a second recovery operation.
        if not self.op1 or self.op1["status"] != "SYNTHETIC_REVIEWED_EXECUTION_VALIDATED":
            raise ValueError("STRUCTURAL_STOP_REQUIRES_VALIDATED_COMPLETION")
        # The completed audit describes the state at STOP, before a later human
        # may change source truth. Preserve that evidence; the new plan below
        # independently hashes/authorizes the current canonical bytes.
        audit = self.op1["audit"]
        if (audit["status"] != "SYNTHETIC_REPAIR_VALIDATED" or
                json.loads(Path(self.op1["outcome"]).read_bytes()) != self.op1 or
                pre.digest(Path(self.op1["journal"]).read_bytes()) != self.op1["journal_sha256"] or
                pre.digest((self.root / pre.BLOCKERS).read_bytes()) != self.plan1["proposed"]["after_sha256"]):
            raise ValueError("STRUCTURAL_AUDIT_REQUIRES_REAUTHORIZE")
        save(self.base / "structural-transition-audit.json", audit)
        self.f.external = self.base / ("operation-2-" + uuid.uuid4().hex)
        self.f.external.mkdir()
        self.f.packet = deepcopy(self.f.packet)
        self.f.packet.update(task="SYNTHETIC-D-CONTEXT", ids={
            "CP": "CP-091", "SC": "SC-091", "CD": "CD-001", "HO": "HO-008"})
        a = assembly_tests.AssemblyTests()
        a.fixture, a.root, a.external, a.packet = self.f, self.root, self.f.external, self.f.packet
        a.bind()  # Re-read repaired bytes and rebuild all existing context evidence.
        failure = deepcopy(self.f.records["failure"])
        failure["blockers"] = {"BLK-001": "OPEN"}
        self.f.evidence("failure", failure)
        request = self.request("CONTEXT")
        for key in ("target", "purpose", "task", "executor", "writes", "inputs", "evidence", "ids", "completion"):
            request[key] = deepcopy(a.packet[key])
        request["gates"] = {key: "APPROVED" for key in self.f.records["authorization"]["gates"]}
        self.plan2 = {"kind": "CONTEXT", "proposed": a.stage(), "packet": deepcopy(a.packet),
                      "request": request, "evidence_root": str(a.external)}
        self.auth2, self.context2 = self.authorize(self.plan2)
        return self.plan2

    def context(self):
        self.op2 = execution.execute_reviewed(self.plan2, self.auth2, self.context2)
        save(self.base / "operation-2-result.json", self.op2)
        self.final = self.snapshot("final")
        return self.op2


class EndToEndTests(unittest.TestCase):
    def setUp(self):
        self.s = Scenario()

    def repaired(self):
        result = self.s.structural()
        self.assertEqual("SYNTHETIC_REVIEWED_EXECUTION_VALIDATED", result["status"], result)
        self.assertEqual("STOP", result["action"])
        self.assertFalse(hasattr(self.s, "plan2"))
        return result

    def prepared(self):
        self.repaired()
        self.s.prepare_context()

    def refused(self, plan=None, auth=None, context=None):
        s = self.s
        before = rt._snapshot(s.root)
        result = execution.execute_reviewed(s.plan2 if plan is None else plan,
            s.auth2 if auth is None else auth, s.context2 if context is None else context)
        self.assertEqual("REFUSED", result["status"], result)
        self.assertEqual("STOP", result["action"])
        self.assertEqual(before, rt._snapshot(s.root))
        save(s.base / ("refusal-" + uuid.uuid4().hex + ".json"), result)
        return result

    def completed(self):
        self.prepared()
        result = self.s.context()
        self.assertEqual("SYNTHETIC_REVIEWED_EXECUTION_VALIDATED", result["status"], result)
        return result

    def test_D01_continuous_instance(self):
        result = self.completed()
        s = self.s
        self.assertEqual(s.initial["root"], s.between["root"])
        self.assertEqual(s.initial["root"], s.final["root"])
        initial, between, final = [r["hashes"] for r in (s.initial, s.between, s.final)]
        self.assertEqual({pre.BLOCKERS}, {p for p in between if between[p] != initial.get(p)})
        expected = {w["path"] for w in s.plan2["proposed"]["write_set"]}
        self.assertEqual(expected, {p for p in final if final[p] != between.get(p)})
        self.assertEqual(set(initial) | expected, set(final))
        fields = s.plan1["proposed"]["fields"]
        self.assertEqual(11, len(fields))
        self.assertEqual(fields, sr._repair((s.root / pre.BLOCKERS).read_bytes(), "BLK-001")[1])
        self.assertEqual(("HIGH", "OPEN"), (fields[1], fields[8]))
        for write in s.plan2["proposed"]["write_set"]:
            self.assertEqual(write["proposed_final_sha256"], final[write["path"]])
        for name in (s.stale, s.pending, s.f.source, "attempt-history.json"):
            self.assertEqual(initial[name], final[name])
        self.assertEqual(s.history, rt._snapshot(s.base / "evidence"))
        self.assertTrue((s.root / pre.STALE).read_bytes().startswith(bytes.fromhex(next(
            w["before_image_hex"] for w in s.plan2["proposed"]["write_set"] if w["path"] == pre.STALE))))
        self.assertEqual(7, result["audit"]["completed_operations"])
        self.assertEqual(result["final_hashes"], result["audit"]["final_hashes"])
        self.assertFalse(result["writer"]["validation"]["ordinary_context_activation"])
        self.assertEqual("ARCHIVED", pre.op.table(pre.op.text(s.root, pre.INDEX), "Index", ["Status"])[-1]["Status"])
        for state in (s.between, s.final):
            self.assertFalse(any(d["status"] in {"FAIL", "UNVERIFIED"} for d in state["doctor"]["diagnostics"]))
        self.assertTrue(any(d["status"] == "FAIL" for d in s.initial["doctor"]["diagnostics"]))
        inventory = [{"path": p, "before": initial.get(p, "ABSENT"),
                      "between": between.get(p, "ABSENT"), "after": final.get(p, "ABSENT")}
                     for p in sorted(set(initial) | set(final)) if initial.get(p) != final.get(p)]
        save(s.base / "mutation-inventory.json", inventory)
        save(EVIDENCE / "continuous-instance.json", {"scenario": str(s.base),
            "findings": ["STRUCTURAL_INTEGRITY_RECOVERED", "RECOVERY_CONTEXT_ASSEMBLED",
                         "ORDINARY_EXECUTION_STILL_BLOCKED"], "production_authority": False})

    def test_D02_stale_operation1_hashes_refuse(self):
        self.prepared()
        s = self.s
        for packet in (s.plan2["packet"], s.plan2["request"]):
            next(i for i in packet["inputs"] if i["path"] == pre.BLOCKERS)["sha256"] = s.initial["hashes"][pre.BLOCKERS]
        check = pre.validate(s.root, Path(s.plan2["evidence_root"]), s.plan2["packet"])
        self.assertEqual("INVALID_PREFLIGHT", check["status"])
        self.assertEqual("HASH", check["findings"][-1]["id"])
        save(s.base / "stale-hash-preflight.json", check)
        self.refused()

    def test_D03_separate_authorization_required(self):
        self.prepared()
        self.refused(auth={})
        self.refused(auth=self.s.auth1, context=self.s.context1)

    def test_D04_expired_or_changed_approval_refuses(self):
        self.prepared()
        original = deepcopy(self.s.auth2)
        self.s.auth2["human_authorization"]["expires_at"] = self.s.human.start
        self.refused()
        self.s.auth2 = original
        self.s.auth2["human_authorization"]["binding"]["ids"]["review"]["review_sha256"] = "0" * 64
        self.refused()

    def test_D05_canonical_change_requires_independent_regeneration(self):
        self.prepared()
        s = self.s
        source = s.root / s.f.source
        original = source.read_bytes()
        source.write_bytes(original + b"Changed canonical truth\n")
        self.refused()
        old_auth, old_context = deepcopy(s.auth2), deepcopy(s.context2)
        s.prepare_context()
        self.refused(auth=old_auth, context=old_context)
        self.assertEqual(pre.digest(source.read_bytes()), next(i["sha256"] for i in
            s.plan2["packet"]["inputs"] if i["path"] == s.f.source))
        self.assertEqual("SYNTHETIC_REVIEWED_EXECUTION_VALIDATED", s.context()["status"])

    def test_D06_interrupted_structural_never_chains(self):
        s = self.s
        def interrupt(event):
            if event == "after_replace":
                raise ValueError("Synthetic interruption after replacement")
        with patch.object(sr, "_checkpoint", side_effect=interrupt):
            result = s.structural()
        self.assertEqual("INTERRUPTED", result["status"], result)
        before = rt._snapshot(s.root)
        with self.assertRaisesRegex(ValueError, "STRUCTURAL_STOP"):
            s.prepare_context()
        self.assertEqual(before, rt._snapshot(s.root))
        self.assertFalse(hasattr(s, "plan2"))
        audit = sr.audit(s.root, Path(s.plan1["evidence_root"]))
        self.assertEqual("INTERRUPTED", audit["status"])
        save(s.base / "interrupted-structural-audit.json", audit)

    def test_D07_interrupted_context_never_resumes(self):
        self.prepared()
        def interrupt(event, sequence):
            if event == "after_mutation" and sequence == 1:
                raise ValueError("Synthetic context interruption")
        with patch.object(rt, "_checkpoint", side_effect=interrupt):
            result = self.s.context()
        self.assertEqual("INTERRUPTED", result["status"], result)
        journal = Path(self.s.plan2["evidence_root"]) / self.s.plan2["proposed"]["journal"]["path"]
        before = journal.read_bytes()
        self.refused()
        self.assertEqual(before, journal.read_bytes())
        audit = rt.audit(self.s.root, journal, self.s.plan2["proposed"])
        self.assertNotEqual("SYNTHETIC_EXECUTION_VALIDATED", audit["status"])
        save(self.s.base / "interrupted-context-audit.json", audit)

    def test_D08_reference_cannot_authorize_both(self):
        self.prepared()
        s = self.s
        s.plan2["request"]["operation_reference"] = s.plan1["request"]["operation_reference"]
        s.auth2, s.context2 = s.authorize(s.plan2)
        self.assertIn("CONSUMED_OR_CONFLICTING_REFERENCE", self.refused()["findings"])

    def test_D09_blocker_and_retries_preserved(self):
        self.completed()
        s = self.s
        self.assertEqual(s.initial["hashes"]["attempt-history.json"], s.final["hashes"]["attempt-history.json"])
        self.assertEqual(s.between["hashes"][pre.BLOCKERS], s.final["hashes"][pre.BLOCKERS])
        self.assertEqual(s.history, rt._snapshot(s.base / "evidence"))

    def test_D10_ordinary_execution_stays_blocked(self):
        self.completed()
        s = self.s
        for snapshot in (s.initial, s.between, s.final):
            self.assertTrue(snapshot["ordinary"]["refused"])
            self.assertEqual("YES", snapshot["state"]["Blocked"])
            self.assertEqual("BLOCKED", snapshot["state"]["ExecutionReadiness"])
        for key, value in s.initial["state"].items():
            if key not in {"LastAction", "LastContextDelta", "Notes"}:
                self.assertEqual(value, s.final["state"][key], key)

    def test_D11_actual_ADAPT_DEV_refused(self):
        self.prepared()
        target = FRAMEWORK.parent / "ADAPT-DEV/ADAPT"
        for plan in (self.s.plan1, self.s.plan2):
            changed = deepcopy(plan)
            changed["request"]["target"]["root"] = str(target)
            self.refused(plan=changed)
        for checker in (sr._checked, lambda p: rt._checked(p, rt.SYNTHETIC_ROOT)):
            with self.assertRaises(pre.Refusal):
                checker(target)

    def test_D12_no_production_or_adoption_authority(self):
        self.completed()
        for result in (self.s.op1, self.s.op2):
            self.assertFalse(result["operational_authority"])
            self.assertEqual("UNAUTHORIZED", result["real_execution"])
            self.assertEqual("STOP", result["action"])
        self.refused(context={"mode": "PRODUCTION", "binding": self.s.context2["binding"]})

    def test_shared_boundary_preserves_alias_and_escape_refusals(self):
        for checker in (sr._checked, lambda p: rt._checked(p, rt.SYNTHETIC_ROOT)):
            for path in (rt.ACCEPTANCE_ROOT, rt.ACCEPTANCE_ROOT.parent / "outside",
                         self.s.root / ".." / "escape"):
                with self.assertRaises(pre.Refusal):
                    checker(path)
        target = self.s.base / "alias.txt"
        os.link(self.s.root / self.s.f.source, target)
        try:
            for checker in (sr._checked, lambda p: rt._checked(p, rt.SYNTHETIC_ROOT)):
                with self.assertRaises(pre.Refusal):
                    checker(target)
        finally:
            target.unlink()
        # Exercise a real Windows reparse point at the new shared boundary.
        if os.name == "nt":
            import subprocess
            junction = self.s.base / "junction"
            created = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(self.s.root)],
                                     capture_output=True, text=True)
            self.assertEqual(0, created.returncode, created.stderr)
            try:
                for checker in (sr._checked, lambda p: rt._checked(p, rt.SYNTHETIC_ROOT)):
                    with self.assertRaises(pre.Refusal):
                        checker(junction)
            finally:
                os.rmdir(junction)


if __name__ == "__main__":
    unittest.main()
