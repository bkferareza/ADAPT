"""Synthetic approval declarations only; these fixtures are never human authority."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from fixtures import FRAMEWORK, fresh_instance
import test_recovery_assembly as context_tests
import test_recovery_supervised as human_tests

spec = importlib.util.spec_from_file_location(
    "plan_review", FRAMEWORK / "VALIDATION/recovery_plan_review.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
sr = review._load("recovery_structural")


class PlanReviewTests(unittest.TestCase):
    def setUp(self):
        sr.SYNTHETIC_ROOT.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="review-", dir=sr.SYNTHETIC_ROOT)
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root, self.external = self.base / "instance", self.base / "evidence"
        fresh_instance(self.root)
        self.external.mkdir()
        self.human = human_tests.SupervisedTests()
        self.human.setUp()
        self.path = self.root / sr.pre.BLOCKERS
        columns = "| " + " | ".join(sr.COLUMNS) + " |\r\n"
        row = "| BLK-900 | HIGH | Synthetic | Misplaced row | BI-900 | Test | 2026-10-20 | Director | OPEN | NONE | NONE |\r\n"
        self.path.write_bytes(("# Synthetic blockers\r\n\r\n## Blockers\r\n\r\n" + columns +
                               "| " + " | ".join(["---"] * 11) + " |\r\n\r\n## Notes\r\n\r\n" + row).encode())
        self.scope = {"governance": "HUMAN_SUPERVISED", "human": "synthetic-maintainer",
                      "target": str(self.root), "path": sr.pre.BLOCKERS,
                      "operation": sr.OPERATION, "blocker": "BLK-900",
                      "before_sha256": sr.pre.digest(self.path.read_bytes())}
        proposed = sr.plan(self.root, self.scope)
        request = deepcopy(self.human.packet)
        request.update(target={"root": str(self.root), "identity": "SYNTHETIC-REVIEW"},
                       task="SYNTHETIC-STRUCTURAL-ATTEMPT-1",
                       writes=[{"path": sr.pre.BLOCKERS, "operation": "set_fields",
                                "fields": ["placement"], "before_sha256": proposed["before_sha256"]}],
                       inputs=[{"path": path, "sha256": digest, "verified_at": self.human.checked}
                               for path, digest in proposed["baseline"].items()],
                       ids={"blocker": "BLK-900"},
                       completion={"expected": "Placement only; preserve OPEN; return to both humans and STOP"})
        evidence = b"Synthetic evidence only; not an actual approval.\n"
        (self.external / "synthetic.txt").write_bytes(evidence)
        request["evidence"] = {"synthetic": {"path": "synthetic.txt", "sha256": sr.pre.digest(evidence)}}
        self.plan = {"kind": "STRUCTURAL", "proposed": proposed, "request": request,
                     "evidence_root": str(self.external)}
        self.authorize()

    def authorize(self):
        prepared = review.prepare_review(self.plan)
        config, approval = deepcopy(self.human.config), deepcopy(self.human.response)
        config.update(target=deepcopy(self.plan["request"]["target"]))
        approval["binding"] = prepared["authorization_binding"]
        self.authorization = {"maintenance_scope": config, "human_authorization": approval}
        return prepared

    def context(self):
        fixture = context_tests.AssemblyTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        request = deepcopy(self.human.packet)
        for key in ("target", "purpose", "task", "executor", "writes", "inputs",
                    "evidence", "ids", "completion"):
            request[key] = deepcopy(fixture.packet[key])
        request["gates"] = {key: "APPROVED" for key in
                            fixture.fixture.records["authorization"]["gates"]}
        self.plan = {"kind": "CONTEXT", "proposed": fixture.stage(), "request": request,
                     "packet": deepcopy(fixture.packet), "evidence_root": str(fixture.external)}
        prepared = review.prepare_review(self.plan)
        self.authorize()
        config = self.authorization["maintenance_scope"]
        config.update(workcell=request["workcell"], executor=request["executor"],
                      required_gates=list(request["gates"]))
        return fixture, prepared

    def valid(self):
        result = review.validate_review(self.plan, self.authorization)
        self.assertEqual("REVIEW_EVIDENCE_VALID", result["status"], result)
        self.assertTrue(result["valid"])
        self.assertFalse(result["operational_authority"])
        self.assertEqual("STOP", result["action"])
        return result

    def refused(self):
        result = review.validate_review(self.plan, self.authorization)
        self.assertEqual("REVIEW_REFUSED", result["status"], result)
        self.assertFalse(result["valid"])
        self.assertFalse(result["operational_authority"])
        self.assertEqual("STOP", result["action"])
        return result

    def test_PR01_valid_synthetic_structural_review(self):
        result = self.valid()
        self.assertEqual("SYNTHETIC_VALID", result["supervised"]["human_authorization_evidence"])
        package = review.prepare_review(self.plan)
        for field in ("target", "purpose", "problem", "files", "operations", "expected_state",
                      "completion", "unchanged_governance", "risks_and_stop_conditions", "plan_sha256"):
            self.assertTrue(package[field])

    def test_PR02_valid_synthetic_context_review(self):
        fixture, prepared = self.context()
        self.valid()
        self.assertEqual(6, len(prepared["files"]))
        self.assertEqual(7, len(prepared["operations"]))
        self.assertIn("STALE", prepared["text"])
        self.assertEqual(fixture.stage()["plan_sha256"], prepared["plan_sha256"])

    def test_PR03_missing_human_authorization_and_self_approval(self):
        saved = self.authorization
        for value in (None, {}, {"approved": True}):
            self.authorization = value
            self.refused()
        self.plan["human_authorization"] = saved
        self.authorization = None
        self.refused()

    def test_PR04_missing_director_capacity(self):
        self.authorization["human_authorization"]["approvals"] = [a for a in
            self.authorization["human_authorization"]["approvals"] if a["role"] != "Human Director"]
        self.refused()

    def test_PR05_missing_maintainer_capacity(self):
        self.authorization["human_authorization"]["approvals"] = [a for a in
            self.authorization["human_authorization"]["approvals"] if a["role"] != "Human Framework Maintainer"]
        self.refused()

    def test_PR06_same_human_two_explicit_capacities(self):
        config = self.authorization["maintenance_scope"]
        for role in config["authorities"]:
            config["authorities"][role] = "same-synthetic-human"
        approvals = self.authorization["human_authorization"]["approvals"]
        for approval in approvals:
            approval["human"] = "same-synthetic-human"
        self.valid()
        approvals[1]["approval_reference"] = approvals[0]["approval_reference"]
        self.refused()

    def test_PR07_changed_plan_fingerprint_and_artifact_bytes(self):
        original = deepcopy(self.plan)
        self.plan["proposed"]["plan_sha256"] = "0" * 64
        self.refused()
        self.plan = deepcopy(original)
        self.plan["proposed"]["after_image_hex"] += "20"
        self.refused()
        body = {k: v for k, v in self.plan["proposed"].items() if k != "plan_sha256"}
        self.plan["proposed"]["plan_sha256"] = review.assembly.fingerprint(body)
        self.refused()

    def test_PR08_changed_mutation_scope(self):
        original = deepcopy(self.plan)
        for key, value in (("path", "other.md"), ("operation", "append_row"),
                           ("fields", ["Status"])):
            self.plan = deepcopy(original)
            self.plan["request"]["writes"][0][key] = value
            self.refused()
        self.plan = deepcopy(original)
        self.plan["request"]["writes"] *= 2
        self.refused()

    def test_PR09_changed_source_and_before_hashes(self):
        original = deepcopy(self.plan)
        self.plan["request"]["inputs"][0]["sha256"] = "0" * 64
        self.refused()
        self.plan = deepcopy(original)
        self.plan["request"]["writes"][0]["before_sha256"] = "0" * 64
        self.refused()
        self.plan = deepcopy(original)
        self.path.write_bytes(self.path.read_bytes() + b"changed\n")
        self.refused()
        fixture, _ = self.context()
        source = fixture.root / fixture.fixture.source
        source.write_bytes(source.read_bytes() + b"changed\n")
        self.refused()

    def test_PR10_wrong_target_instance(self):
        self.plan["request"]["target"]["identity"] = "WRONG"
        self.refused()
        self.plan["request"]["target"]["root"] = str(self.external)
        self.refused()

    def test_PR11_expired_or_withdrawn_authorization(self):
        approval = self.authorization["human_authorization"]
        expiry = approval["expires_at"]
        approval["expires_at"] = self.human.start
        self.refused()
        approval["expires_at"] = expiry
        approval["withdrawn"] = True
        self.refused()

    def test_PR12_approval_reuse_for_another_plan_or_attempt(self):
        for key in ("task", "operation_reference", "audit_reference"):
            original = self.plan["request"][key]
            self.plan["request"][key] += "-NEW-ATTEMPT"
            self.refused()
            self.plan["request"][key] = original
        self.plan["request"]["completion"]["expected"] = "different completion"
        self.refused()

    def test_PR13_diff_matches_exact_proposed_bytes(self):
        packages = [review.prepare_review(self.plan)]
        _, context = self.context()
        packages.append(context)
        for package in packages:
            for item in package["files"]:
                with self.subTest(kind=package["kind"], path=item["path"]):
                    lines = item["diff"].splitlines()[2:]
                    before_lines = [json.loads(line[1:]) for line in lines
                                    if line.startswith(("-", " "))]
                    after_lines = [json.loads(line[1:]) for line in lines
                                   if line.startswith(("+", " "))]
                    before = b"" if item["before_image_hex"] is None else bytes.fromhex(item["before_image_hex"])
                    after = bytes.fromhex(item["after_image_hex"])
                    # Verify each shown line belongs byte-for-byte to the exact image.
                    self.assertTrue(all(line.encode() in before for line in before_lines))
                    self.assertTrue(all(line.encode() in after for line in after_lines))
                    self.assertEqual(sr.pre.digest(after), item["after_sha256"])
                    if before:
                        self.assertEqual(sr.pre.digest(before), item["before_sha256"])
                    # Independently apply each hunk to its before-image.
                    reconstructed = before.decode().splitlines(keepends=True)
                    offset, index = 0, 2
                    diff_lines = item["diff"].splitlines()
                    while index < len(diff_lines):
                        match = re.fullmatch(r'@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@', diff_lines[index])
                        self.assertIsNotNone(match)
                        start = max(0, int(match[1]) - 1)
                        index += 1
                        old, new = [], []
                        while index < len(diff_lines) and not diff_lines[index].startswith('@@'):
                            line = diff_lines[index]
                            if line[0] in ' -':
                                old.append(json.loads(line[1:]))
                            if line[0] in ' +':
                                new.append(json.loads(line[1:]))
                            index += 1
                        self.assertEqual(old, reconstructed[start + offset:start + offset + len(old)])
                        reconstructed[start + offset:start + offset + len(old)] = new
                        offset += len(new) - len(old)
                    self.assertEqual(after, ''.join(reconstructed).encode())
        item = packages[0]["files"][0]
        self.assertIn('\\r\\n', item["diff"])

    def test_PR14_no_canonical_filesystem_mutation(self):
        for context in (False, True):
            if context:
                fixture, _ = self.context()
                root = fixture.root
            else:
                root = self.root
            snapshot = lambda: {p.relative_to(root).as_posix(): p.read_bytes()
                                for p in root.rglob('*') if p.is_file()}
            before = snapshot()
            envelope, authorization = deepcopy(self.plan), deepcopy(self.authorization)
            with patch.object(Path, 'write_bytes', side_effect=AssertionError('Writes forbidden')), \
                 patch.object(Path, 'write_text', side_effect=AssertionError('Writes forbidden')), \
                 patch.object(sr, 'execute', side_effect=AssertionError('Writer forbidden')):
                review.prepare_review(self.plan)
                self.valid()
                saved = self.authorization
                self.authorization = None
                self.refused()
                self.authorization = saved
            self.assertEqual(before, snapshot())
            self.assertEqual(envelope, self.plan)
            self.assertEqual(authorization, self.authorization)

    def test_PR15_never_grants_production_authority(self):
        for synthetic in (True, False):
            self.authorization["human_authorization"]["synthetic"] = synthetic
            result = self.valid()
            self.assertEqual("UNVERIFIED", result["human_authenticity"])
            self.assertIn("PRODUCTION_WRITER_AUTHORIZATION", result["supervised"]["outstanding_requirements"])
        self.plan["proposed"]["operational_authority"] = True
        self.refused()

    def test_context_operations_completion_and_scope_are_immutable(self):
        self.context()
        original = deepcopy(self.plan)
        for mutation in (lambda p: p["proposed"]["operations"].pop(),
                         lambda p: p["proposed"]["operations"].append(deepcopy(p["proposed"]["operations"][0])),
                         lambda p: p["proposed"]["return"].update(final_action="EXECUTE"),
                         lambda p: p["request"]["writes"][0].update(fields=["Status"])):
            self.plan = deepcopy(original)
            mutation(self.plan)
            body = {k: v for k, v in self.plan["proposed"].items() if k != "plan_sha256"}
            self.plan["proposed"]["plan_sha256"] = review.assembly.fingerprint(body)
            self.refused()


if __name__ == "__main__":
    unittest.main()
