"""Real isolated file/hash checks; synthetic authority never approves real work."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from fixtures import FRAMEWORK, fresh_instance, framework_version

spec = importlib.util.spec_from_file_location("preflight", FRAMEWORK / "VALIDATION/recovery_preflight.py")
pre = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pre)


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "instance"
        self.external = self.base / "evidence"
        self.external.mkdir()
        fresh_instance(self.root)
        self.change(pre.DIRECTOR, lambda s: s.replace("{{DIRECTOR_IDENTITY}}", "Synthetic Director"))
        self.change(pre.op.CP, lambda s: s.replace("| Blocked | NO |", "| Blocked | YES |")
                    .replace("| ActiveBlockers | NONE |", "| ActiveBlockers | BLK-901 |")
                    .replace("| SourceTruthVersion | NONE |", "| SourceTruthVersion | SOURCE_TRUTH_V1.0 |"))
        self.change(pre.BLOCKERS, lambda s: s.replace("## Severity Values", "| BLK-901 | HIGH | Synthetic | Fixture failure | BI-901 | Test | 2026-10-18 | Director | OPEN | NONE | NONE |\n\n## Severity Values"))
        self.source = "01_SOURCE_TRUTH/SYNTHETIC.md"
        (self.root / self.source).write_text("Synthetic source, no real adoption.\n", encoding="utf-8")
        self.change(pre.VERSION_LOG, lambda s: s.replace("## Document Types", f"| SOURCE_TRUTH_V1.0 | {self.source} | Requirements Document | Synthetic Director | 2026-10-18 | Fixture | NONE | ACTIVE |\n\n## Document Types"))
        self.packet = {"target": {"root": str(self.root), "identity": "Fixture"},
                       "purpose": pre.PURPOSE, "task": "synthetic bounded assembly",
                       "executor": "Synthetic Operator", "inputs": [], "evidence": {},
                       "ids": {k: k + "-001" for k in ("CP", "CD", "HO", "SC")},
                       "writes": [], "failure_reason": "Synthetic exhausted context assembly",
                       "freshness": "STALE_ORDINARY_INVALID_RECOVERY_EVIDENCE_ONLY",
                       "completion": dict(pre.COMPLETION, return_to=["Synthetic Director", "Synthetic Maintainer"],
                                          journal="outputs/journal.jsonl", manifest="outputs/manifest.json",
                                          return_destination="outputs/return.json")}
        self.records = {}
        self.refresh_inputs()
        self.plan()
        self.authorize()

    def change(self, ref, fn):
        path = self.root / ref
        path.write_text(fn(path.read_text(encoding="utf-8")), encoding="utf-8")

    def refresh_inputs(self):
        refs = pre.REQUIRED | {self.source}
        for folder in ("10_CONTEXT_ECONOMY", "06_HANDOFFS"):
            refs |= {p.relative_to(self.root).as_posix() for p in (self.root / folder).rglob("*") if p.is_file()}
        self.packet["inputs"] = [{"path": ref, "sha256": pre.digest((self.root / ref).read_bytes()),
                                  "class": "CURRENT_CANONICAL", "reason": "Synthetic prerequisite",
                                  "verified_at": "2026-10-18T06:00:00+00:00"} for ref in sorted(refs)]

    def plan(self):
        ids = self.packet["ids"]
        writes = []
        for folder, kind in (("10_CONTEXT_ECONOMY/CONTEXT_PACKS", "CP"),
                             ("10_CONTEXT_ECONOMY/CONTEXT_DELTAS", "CD"), ("06_HANDOFFS/ACTIVE", "HO")):
            writes.append({"path": f"{folder}/{ids[kind]}.md", "operation": "create", "fields": ["document"],
                           "before_sha256": "ABSENT", "before": None,
                           "after": {"document": "STAGED_AT_WRITER_TIME"}})
        values = pre.op.state(self.root)
        for ref, operation, after in (
            (pre.INDEX, "append_row", {"row": {"id": ids["CP"], "during": "STALE", "final": "ARCHIVED",
                "handoff": "NONE", "source": values["SourceTruthVersion"],
                "notes": "RECOVERY ONLY; NO ORDINARY EXECUTION AUTHORITY"}}),
            (pre.STALE, "append_open_row", {"row": {"id": ids["SC"], "status": "OPEN", "pack": ids["CP"]}}),
            (pre.op.CP, "set_fields", {"LastContextDelta": ids["CD"], "LastAction": "Synthetic recovery assembly",
                                     "Notes": values["Notes"] + "\nSynthetic recovery only"})):
            writes.append({"path": ref, "operation": operation, "fields": list(after), "after": after,
                           "before_sha256": pre.digest((self.root / ref).read_bytes()),
                           "before": {k: values[k] for k in after} if ref == pre.op.CP else
                           (self.root / ref).read_bytes().decode("utf-8-sig")})
        self.packet["writes"] = writes

    def evidence(self, name, record):
        self.records[name] = copy.deepcopy(record)
        ref = name + ".json"
        data = json.dumps(record, sort_keys=True).encode("utf-8")
        (self.external / ref).write_bytes(data)
        self.packet["evidence"][name] = {"path": ref, "sha256": pre.digest(data)}

    def authorize(self):
        p = self.packet
        binding = {key: p[key] for key in ("target", "purpose", "task", "executor", "writes", "ids", "completion")}
        for name in ("release", "adoption"):
            self.evidence(name, {"synthetic": True, "target": p["target"], "version": framework_version(),
                                 "effective": True, "maintainer": "Synthetic Maintainer"})
        self.evidence("installation", {"format": "synthetic-v1", "synthetic": True, "target": p["target"],
            "version": framework_version(), "capabilities": ["rule14-entry", "purpose-b-assembly"],
            "effective": True, "maintainer": "Synthetic Maintainer",
            "release": p["evidence"]["release"], "adoption": p["evidence"]["adoption"],
            "contracts": {r: pre.digest((self.root / r).read_bytes()) for r in
                          (pre.GOVERNANCE, pre.op.SCHEMA, "15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md")}})
        for name, role, human in (("maintainer", "Human Framework Maintainer", "Synthetic Maintainer"),
                                  ("director", "Human Director", "Synthetic Director"),
                                  ("authorization", "Bound Authorization", "Synthetic Maintainer")):
            self.evidence(name, {"synthetic": True, "role": role, "human": human, "binding": binding,
                "inputs": p["inputs"], "original_input": True, "gates": {"all_applicable": "SYNTHETIC_APPROVED"},
                "maintainer": "Synthetic Maintainer", "director": "Synthetic Director", "executor": p["executor"],
                "capacity": "recovery Context Steward", "canonical_assembly_approved": True})
        self.evidence("designation", {"synthetic": True, "target": p["target"], "human": "Synthetic Director",
                                      "role": "Human Director", "original_input": True})
        for i in range(3):
            self.evidence("attempt" + str(i), {"synthetic": True, "raw_diagnostic": "Synthetic failure " + str(i)})
        self.evidence("failure", {"target": p["target"], "state": pre.op.state(self.root),
            "ordinary_context_unavailable": p["failure_reason"], "retry_limit": 3,
            "attempts": [{"result": "FAILED", "evidence": "attempt" + str(i)} for i in range(3)],
            "blockers": {"BLK-901": "OPEN"}})

    def check(self, expected="INVALID_PREFLIGHT", code=None):
        result = pre.validate(self.root, self.external, self.packet)
        self.assertEqual(expected, result["status"], result)
        self.assertFalse(result["operational_authority"])
        if code:
            self.assertEqual(code, result["findings"][-1]["id"], result)
        return result

    def test_valid_synthetic_purpose_b(self):
        self.check("VALID_SYNTHETIC_PREFLIGHT")

    def test_missing_maintainer_authority(self):
        del self.packet["evidence"]["maintainer"]
        self.check(code="AUTHORITY")

    def test_missing_director_provenance(self):
        del self.packet["evidence"]["designation"]
        self.check(code="DIRECTOR")

    def test_wrong_instance(self):
        self.packet["target"]["identity"] = "Wrong"
        self.check(code="TARGET")

    def test_source_changed(self):
        self.change(self.source, lambda s: s + "Changed bytes")
        self.check(code="HASH")

    def test_unpermitted_path_and_fields(self):
        for field, value in (("path", pre.BLOCKERS), ("operation", "execute"), ("fields", ["Blocked"])):
            with self.subTest(field=field):
                original = copy.deepcopy(self.packet)
                self.packet["writes"][-1][field] = value
                self.authorize()
                self.check()
                self.packet = original

    def test_issued_ids_in_archive_and_duplicate_definitions(self):
        archive = self.root / "06_HANDOFFS/ARCHIVE"
        archive.mkdir(exist_ok=True)
        (archive / "HO-001.md").write_text("HANDOFF_ID: HO-001\n", encoding="utf-8")
        self.refresh_inputs()
        self.authorize()
        self.check(code="IDS")
        (archive / "other.md").write_text("HANDOFF_ID: HO-001\n", encoding="utf-8")
        self.refresh_inputs()
        self.authorize()
        self.check(code="IDS")

    def test_retry_exhaustion_preserved(self):
        before = (self.root / pre.BLOCKERS).read_bytes()
        self.check("VALID_SYNTHETIC_PREFLIGHT")
        self.assertEqual(before, (self.root / pre.BLOCKERS).read_bytes())
        record = self.records["failure"]
        record["attempts"].pop()
        self.evidence("failure", record)
        self.check(code="RETRIES")

    def test_fw0005_even_with_claimed_adoption_fails(self):
        self.change(pre.GOVERNANCE, lambda s: s.replace("VERSION: " + framework_version(), "VERSION: ADAPT-FW-0005"))
        self.check("UNSUPPORTED_CAPABILITY", "CAPABILITY")

    def test_read_only_api_and_cli_success_and_refusal(self):
        def snapshot():
            return {p.relative_to(self.base).as_posix(): pre.digest(p.read_bytes())
                    for p in self.base.rglob("*") if p.is_file()}
        for valid in (True, False):
            if not valid:
                self.packet["purpose"] = "UNSUPPORTED"
            (self.external / "packet.json").write_text(json.dumps(self.packet), encoding="utf-8")
            before = snapshot()
            self.check("VALID_SYNTHETIC_PREFLIGHT" if valid else "INVALID_PREFLIGHT")
            run = subprocess.run([sys.executable, "-B", str(FRAMEWORK / "VALIDATION/recovery_preflight.py"),
                "--instance", str(self.root), "--evidence-root", str(self.external), "--packet", "packet.json"],
                capture_output=True, text=True)
            self.assertEqual(0 if valid else 1, run.returncode, run.stderr + run.stdout)
            self.assertEqual("VALID_SYNTHETIC_PREFLIGHT" if valid else "INVALID_PREFLIGHT",
                             json.loads(run.stdout)["status"])
            self.assertEqual(before, snapshot())

    def test_missing_adoption_and_real_records_unsupported(self):
        del self.packet["evidence"]["adoption"]
        self.check("UNSUPPORTED_CAPABILITY", "CAPABILITY")
        self.authorize()
        record = self.records["installation"]
        record["synthetic"] = False
        self.evidence("installation", record)
        self.check("UNSUPPORTED_CAPABILITY", "CAPABILITY")

    def test_before_image_mismatch(self):
        self.packet["writes"][-1]["before"]["LastAction"] = "wrong"
        self.authorize()
        self.check(code="BEFORE")

    def test_hash_is_not_human_authentication(self):
        record = self.records["maintainer"]
        record["original_input"] = False
        self.evidence("maintainer", record)
        self.check(code="AUTHORITY")

    def test_completion_and_freshness_fail_closed(self):
        self.packet["completion"]["index_final"] = "ACTIVE"
        self.authorize()
        self.check(code="COMPLETION")
        self.packet["completion"]["index_final"] = "ARCHIVED"
        self.packet["freshness"] = "OVERRIDE"
        self.authorize()
        self.check(code="FRESHNESS")

    def test_path_traversal_and_aliases(self):
        self.packet["inputs"][0]["path"] = "../escape"
        self.check(code="PATH")
        self.refresh_inputs()
        self.packet["inputs"].append(copy.deepcopy(self.packet["inputs"][0]))
        self.check(code="ALIAS")

    def test_duplicate_json_keys(self):
        with self.assertRaises(pre.Refusal):
            pre.load_json('{"synthetic":true,"synthetic":false}')

    def test_duplicate_context_index_history(self):
        self.change(pre.INDEX, lambda s: s + "\n| CP-001 | historical |\n| CP-001 | conflicting |\n")
        self.refresh_inputs()
        self.plan()
        self.authorize()
        self.check(code="IDS")

    def test_original_evidence_changed(self):
        path = self.external / self.packet["evidence"]["director"]["path"]
        path.write_bytes(path.read_bytes() + b" ")
        self.check(code="HASH")


if __name__ == "__main__":
    unittest.main()
