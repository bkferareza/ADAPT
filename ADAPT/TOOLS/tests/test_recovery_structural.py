"""SC-05 isolated synthetic acceptance; retained artifacts are not real authority."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fixtures import FRAMEWORK, fresh_instance

spec = importlib.util.spec_from_file_location("structural", FRAMEWORK / "VALIDATION/recovery_structural.py")
sr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sr)


class StructuralTests(unittest.TestCase):
    def setUp(self):
        sr.SYNTHETIC_ROOT.mkdir(parents=True, exist_ok=True)
        # Retained evidence/fixtures, including interrupted locks; never resume.
        self.base = Path(tempfile.mkdtemp(prefix="sr-", dir=sr.SYNTHETIC_ROOT)).resolve()
        self.root, self.external = self.base / "instance", self.base / "evidence"
        self.external.mkdir()
        fresh_instance(self.root)
        self.path = self.root / sr.pre.BLOCKERS
        historical = sr.runtime.WORKSPACE / ".adapt-local/maintenance/blk-001-recovery-step-1"
        self.original = (historical / "original.bin").read_bytes()
        self.row = (historical / "original-row.bin").read_bytes().rstrip(b"\r\n")
        self.values = json.loads((historical / "verification.json").read_bytes())["original_fields"]
        self.path.write_bytes(self.original)
        cp = self.root / sr.op.CP
        text = cp.read_text(encoding="utf-8").replace("| Blocked | NO |", "| Blocked | YES |")
        text = text.replace("| ActiveBlockers | NONE |", "| ActiveBlockers | BLK-001 |")
        text = text.replace("| ExecutionReadiness | NEEDS_PLANNING |", "| ExecutionReadiness | BLOCKED |")
        cp.write_text(text, encoding="utf-8")
        (self.root / "attempt-history.json").write_text('{"attempts":2,"exhausted":true}')
        self.scope = {"governance": "HUMAN_SUPERVISED", "human": "Synthetic Human Maintainer",
                      "target": str(self.root), "path": sr.pre.BLOCKERS, "operation": sr.OPERATION,
                      "blocker": "BLK-001", "before_sha256": sr.pre.digest(self.original)}

    def plan(self, data=None):
        if data is not None:
            self.path.write_bytes(data)
            self.scope["before_sha256"] = sr.pre.digest(data)
        return sr.plan(self.root, self.scope)

    def execute(self, proposed=None):
        return sr.execute(self.root, self.external, self.scope, proposed or self.plan())

    def success(self, proposed=None):
        result = self.execute(proposed)
        self.assertEqual("SYNTHETIC_REPAIR_VALIDATED", result["status"], result)
        self.assertFalse(result["operational_authority"])
        self.assertEqual("SYNTHETIC_REPAIR_VALIDATED", sr.audit(self.root, self.external)["status"])
        return result

    def test_SR01_original_failure_without_ordinary_context(self):
        self.assertNotIn("BLK-001", [r["BLK-ID"] for r in sr.op.table(
            self.original.decode("utf-8-sig"), "Blockers", sr.COLUMNS)])
        diagnostic = next(d for d in sr.op.doctor(self.root)["diagnostics"] if d["id"] == "CP-C10")
        self.assertEqual("FAIL", diagnostic["status"])
        self.assertFalse(any((self.root / "10_CONTEXT_ECONOMY/CONTEXT_PACKS").iterdir()))
        self.success()

    def test_SR02_exact_relocation(self):
        proposed = self.plan()
        self.success(proposed)
        self.assertEqual(bytes.fromhex(proposed["after_image_hex"]), self.path.read_bytes())
        self.assertEqual(1, self.path.read_bytes().count(self.row))
        self.assertLess(self.path.read_bytes().index(self.row), self.path.read_bytes().index(b"## Notes"))

    def test_SR03_all_eleven_values_and_raw_row(self):
        proposed = self.plan()
        self.assertEqual(self.values, proposed["fields"])
        self.success(proposed)
        rows = sr.op.table(self.path.read_text(encoding="utf-8"), "Blockers", sr.COLUMNS)
        self.assertEqual(self.values, [rows[0][c] for c in sr.COLUMNS])
        self.assertIn(self.row, self.path.read_bytes())

    def test_SR04_unrelated_rows_and_markdown(self):
        unrelated = b"| BLK-002 | LOW | Other | Preserve | BI-002 | Test | 2026-10-20 | Director | DEFERRED | NONE | NONE |\n"
        data = self.original.replace(b"## Severity Values", unrelated + b"\n## Severity Values")
        data += b"\nAn unrelated Notes paragraph with BLK-001 reference.\n"
        proposed = self.plan(data)
        self.success(proposed)
        # Deleting only the moved line from both images proves every other byte.
        before = data.splitlines(keepends=True)
        after = self.path.read_bytes().splitlines(keepends=True)
        self.assertEqual([x for x in before if x.rstrip(b"\r\n") != self.row],
                         [x for x in after if x.rstrip(b"\r\n") != self.row])
        self.assertIn(unrelated, self.path.read_bytes())

    def test_SR05_LF(self):
        self.success(self.plan(self.original.replace(b"\r\n", b"\n")))
        self.assertNotIn(b"\r", self.path.read_bytes())

    def test_SR05_CRLF(self):
        data = self.original.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        self.success(self.plan(data))
        self.assertEqual(data.count(b"\r\n"), self.path.read_bytes().count(b"\r\n"))
        self.assertNotIn(b"\n", self.path.read_bytes().replace(b"\r\n", b""))

    def test_SR06_duplicate_and_ambiguous(self):
        for data in (self.original + b"\n" + self.row + b"\n",
                     self.original.replace(b"## Severity Values", self.row + b"\n\n## Severity Values"),
                     self.original + b"\n## Blockers\n",
                     self.original.replace(b"## Notes", b"## Other")):
            with self.subTest(data=sr.pre.digest(data)), self.assertRaises(ValueError):
                self.plan(data)

    def test_SR07_malformed_incomplete_semantically_inconsistent(self):
        for row in (self.row.replace(b"| HIGH |", b"| |"), self.row.rsplit(b"|", 2)[0] + b"|",
                    self.row.replace(b"| OPEN |", b"| UNKNOWN |"),
                    self.row.replace(b"| NONE | NONE |", b"| Resolved yesterday | NONE |"),
                    self.row.replace(b"2026-10-16T23:14:28.303174+08:00", b"not-a-date")):
            with self.subTest(row=row), self.assertRaises(ValueError):
                self.plan(self.original.replace(self.row, row))

    def test_SR08_changed_before_hash(self):
        proposed = self.plan()
        self.path.write_bytes(self.original + b"\nchanged\n")
        before = sr._snapshot(self.root)
        self.assertEqual("REFUSED", self.execute(proposed)["status"])
        self.assertEqual(before, sr._snapshot(self.root))

    def test_SR09_unauthorized_paths_and_scope(self):
        proposed = self.plan()
        for key, value in (("path", "../outside"), ("path", sr.op.CP),
                           ("target", str(FRAMEWORK)), ("governance", "AUTONOMOUS"),
                           ("human", "NONE"), ("operation", "WRITE_MARKDOWN")):
            scope = dict(self.scope, **{key: value})
            self.assertEqual("REFUSED", sr.execute(self.root, self.external, scope, proposed)["status"])
        modified = copy.deepcopy(proposed)
        modified["after_image_hex"] += "00"
        self.assertEqual("REFUSED", self.execute(modified)["status"])
        self.assertEqual(self.original, self.path.read_bytes())

    def test_SR10_interrupted_intent(self):
        proposed = self.plan()
        with patch.object(sr, "_checkpoint", side_effect=OSError("synthetic interruption")):
            self.assertEqual("INTERRUPTED", self.execute(proposed)["status"])
        self.assertEqual(self.original, self.path.read_bytes())
        self.assertEqual("INTERRUPTED", sr.audit(self.root, self.external)["status"])
        self.assertEqual("REFUSED", self.execute(proposed)["status"])

    def test_SR10_partial_replacement_detected(self):
        proposed = self.plan()
        def partial(event):
            if event == "after_replace":
                self.path.write_bytes(b"partial")
        with patch.object(sr, "_checkpoint", side_effect=partial):
            self.assertEqual("INTERRUPTED", self.execute(proposed)["status"])
        self.assertEqual("INTERRUPTED", sr.audit(self.root, self.external)["status"])
        self.assertTrue((self.external / "plan.json").is_file())
        self.assertEqual("REFUSED", self.execute(proposed)["status"])

    def test_SR10_after_replace_without_completion(self):
        def crash(event):
            if event == "after_replace":
                raise OSError("uncertain completion")
        with patch.object(sr, "_checkpoint", side_effect=crash):
            self.assertEqual("INTERRUPTED", self.execute()["status"])
        self.assertEqual("INTERRUPTED", sr.audit(self.root, self.external)["status"])
        # Even valid final bytes cannot turn uncertain completion into a resume.
        self.scope["before_sha256"] = sr.pre.digest(self.path.read_bytes())
        self.assertEqual("REFUSED", self.execute()["status"])

    def test_SR11_register_doctor_validation(self):
        self.success()
        findings = sr.op.doctor(self.root)["diagnostics"]
        self.assertEqual("PASS", next(d["status"] for d in findings if d["id"] == "CP-C10"))
        self.assertEqual(11, len(sr.op.table(self.path.read_text(encoding="utf-8"), "Blockers", sr.COLUMNS)[0]))

    def test_SR12_governance_state_preserved(self):
        baseline, state = sr._snapshot(self.root), sr.op.state(self.root)
        self.success()
        after = sr._snapshot(self.root)
        self.assertEqual({sr.pre.BLOCKERS}, {p for p in baseline if after[p] != baseline[p]})
        self.assertEqual(set(baseline), set(after))
        self.assertEqual(state, sr.op.state(self.root))
        self.assertEqual(("YES", "BLK-001", "BLOCKED"),
                         tuple(state[k] for k in ("Blocked", "ActiveBlockers", "ExecutionReadiness")))
        row = sr.op.table(self.path.read_text(encoding="utf-8"), "Blockers", sr.COLUMNS)[0]
        self.assertEqual(("HIGH", "OPEN"), (row["Severity"], row["Status"]))

    def test_SR13_valid_register_no_mutation(self):
        repaired = bytes.fromhex(self.plan()["after_image_hex"])
        proposed = self.plan(repaired)
        before = sr._snapshot(self.root)
        self.assertEqual("NO_REPAIR_REQUIRED", self.execute(proposed)["status"])
        self.assertEqual(before, sr._snapshot(self.root))
        self.assertEqual([], list(self.external.iterdir()))

    def test_SR14_actual_ADAPT_DEV_refused(self):
        actual = sr.runtime.WORKSPACE / "ADAPT-DEV/ADAPT"
        path = actual / sr.pre.BLOCKERS
        before = path.read_bytes()
        scope = dict(self.scope, target=str(actual), before_sha256=sr.pre.digest(before))
        self.assertEqual("REFUSED", sr.execute(actual, self.external, scope, {})["status"])
        with self.assertRaises(ValueError):
            sr.plan(actual, scope)
        self.assertEqual(before, path.read_bytes())

    def test_changed_preconditions_before_replacement(self):
        proposed = self.plan()
        def change(event):
            if event == "before_replace":
                self.path.write_bytes(self.original + b"\nconcurrent change")
        with patch.object(sr, "_checkpoint", side_effect=change):
            self.assertEqual("INTERRUPTED", self.execute(proposed)["status"])
        self.assertTrue(self.path.read_bytes().endswith(b"concurrent change"))

    def test_exclusive_owner_and_changed_journal(self):
        proposed = self.plan()
        def second(event):
            if event == "after_intent":
                other = self.base / "other-evidence"
                other.mkdir()
                self.assertEqual("REFUSED", sr.execute(self.root, other, self.scope, proposed)["status"])
                (self.external / "journal.jsonl").write_bytes(b"truncated")
        with patch.object(sr, "_checkpoint", side_effect=second):
            self.assertEqual("INTERRUPTED", self.execute(proposed)["status"])
        self.assertEqual(self.original, self.path.read_bytes())
        self.assertEqual("INTERRUPTED", sr.audit(self.root, self.external)["status"])

    def test_runtime_synthetic_boundary_unchanged(self):
        # The original runtime writer must reject this different synthetic root,
        # framework and protected instance before inspecting any ordinary plan.
        with patch.object(sr.runtime.assembly, "validate_plan", side_effect=AssertionError("must not inspect")):
            for root in (self.root, FRAMEWORK, sr.runtime.WORKSPACE / "ADAPT-DEV/ADAPT"):
                result = sr.runtime.execute(root, self.external, {}, {})
                self.assertEqual("REFUSED", result["status"])
        self.assertEqual(self.original, self.path.read_bytes())

    def test_runtime_path_safety_hardlink_and_noncanonical_path(self):
        with self.assertRaises(ValueError):
            sr.plan(self.root / ".." / "instance", self.scope)
        os.link(self.path, self.external / "register-alias")
        with self.assertRaises(ValueError):
            self.plan()
        self.assertEqual("REFUSED", sr.execute(self.root, self.external, self.scope, {})["status"])


if __name__ == "__main__":
    unittest.main()
