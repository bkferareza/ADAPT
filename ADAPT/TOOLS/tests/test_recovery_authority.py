"""AV-01..14: actual local reads/hashes; synthetic claims never human approval."""
import copy
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

import test_recovery_preflight as fixture_module
from fixtures import FRAMEWORK, framework_version

spec = importlib.util.spec_from_file_location("authority", FRAMEWORK / "VALIDATION/recovery_authority.py")
authority = importlib.util.module_from_spec(spec)
spec.loader.exec_module(authority)


class AuthorityTests(unittest.TestCase):
    def setUp(self):
        # Reuse the existing complete isolated preflight packet, not a new scaffold.
        self.fixture = fixture_module.PreflightTests()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.setUp()
        self.root, self.external = self.fixture.root, self.fixture.external
        self.packet, self.records = self.fixture.packet, self.fixture.records
        self.now = datetime.now(timezone.utc)
        self.start = (self.now - timedelta(days=2)).isoformat()
        self.end = (self.now + timedelta(days=2)).isoformat()
        for item in self.packet["inputs"]:
            item["verified_at"] = (self.now - timedelta(hours=1)).isoformat()
        self.fixture.authorize()
        self.source("director_source", b"Synthetic Director designation, not authenticated.\n")
        self.source("maintainer_source", b"Synthetic Maintainer role basis, not authenticated.\n")
        designation = self.records["designation"]
        designation["original_source"] = self.sources["director_source"]
        self.put("designation", designation)
        self.put("maintainer_provenance", {
            "human": "Synthetic Maintainer", "role": "Human Framework Maintainer",
            "target": self.packet["target"], "original_source": self.sources["maintainer_source"]})
        self.put("original_approval", {
            "approved": True, "binding": self.records["authorization"]["binding"],
            "inputs": self.packet["inputs"], "maintainer": "Synthetic Maintainer",
            "director": "Synthetic Director", "not_before": self.start, "expires_at": self.end})

    def source(self, name, data):
        if not hasattr(self, "sources"):
            self.sources = {}
        path = name + ".txt"
        (self.external / path).write_bytes(data)
        self.sources[name] = {"path": path, "sha256": authority.pre.digest(data)}

    def put(self, name, record):
        self.fixture.evidence(name, record)

    def verify(self, failed=None):
        result = authority.verify_authority(self.root, self.external, self.packet)
        self.assertFalse(result["operational_authority"], result)
        self.assertEqual("UNVERIFIED", result["human_authenticity"])
        self.assertEqual("UNVERIFIED", result["release_or_adoption"])
        for code in ("HUMAN_AUTHENTICITY_UNVERIFIED", "RELEASE_OR_ADOPTION_UNVERIFIED"):
            self.assertTrue(any(f["id"] == code and f["status"] == "UNVERIFIED"
                                for f in result["findings"]), result)
        if failed:
            self.assertEqual("INVALID_AUTHORITY_EVIDENCE", result["status"], result)
            self.assertTrue(any(f["id"] == failed and f["status"] == "FAIL"
                                for f in result["findings"]), result)
        return result

    def test_AV01_structural_binding(self):
        result = self.verify()
        self.assertEqual("PASS", result["structural_status"], result)
        self.assertEqual("UNVERIFIED", result["status"])
        self.assertEqual(framework_version(), result["claimed_effective_release"])

    def test_AV02_missing_original_approval(self):
        del self.packet["evidence"]["original_approval"]
        self.verify("ORIGINAL_HUMAN_APPROVAL")

    def test_AV03_wrong_director_designation(self):
        record = self.records["designation"]
        record["human"] = "Wrong Director"
        self.put("designation", record)
        self.verify("DIRECTOR_DESIGNATION")

    def test_AV04_wrong_maintainer_identity_or_role(self):
        original = copy.deepcopy(self.records["maintainer_provenance"])
        for key, value in (("human", "Other Maintainer"), ("role", "Human Director")):
            with self.subTest(key=key):
                self.put("maintainer_provenance", dict(original, **{key: value}))
                self.verify("MAINTAINER_PROVENANCE")

    def test_AV05_wrong_instance_or_task(self):
        target = copy.deepcopy(self.packet["target"])
        self.packet["target"]["identity"] = "Other instance"
        self.verify("INSTANCE_AND_ROOT")
        self.packet["target"] = target
        self.packet["task"] = "Unapproved task"
        self.verify("APPROVED_OPERATION_AND_SCOPE")

    def test_AV06_unapproved_mutation_scope(self):
        original = copy.deepcopy(self.packet["writes"])
        for key, value in (("path", authority.pre.BLOCKERS), ("operation", "execute"),
                           ("fields", ["Blocked"])):
            with self.subTest(key=key):
                self.packet["writes"] = copy.deepcopy(original)
                self.packet["writes"][-1][key] = value
                self.verify("APPROVED_OPERATION_AND_SCOPE")

    def test_AV07_changed_source_sha256(self):
        path = self.root / self.fixture.source
        path.write_bytes(path.read_bytes() + b"Changed bytes")
        self.verify("EXACT_SOURCE_SHA256")

    def test_AV08_expired_authority(self):
        record = self.records["original_approval"]
        record["expires_at"] = (self.now - timedelta(minutes=1)).isoformat()
        self.put("original_approval", record)
        self.verify("EVIDENCE_VALIDITY")

    def revocation(self, **overrides):
        return dict({"target": self.packet["target"], "task": self.packet["task"],
                     "original_approval": self.packet["evidence"]["original_approval"],
                     "checked_at": (self.now - timedelta(minutes=1)).isoformat(),
                     "expires_at": self.end, "revoked": False}, **overrides)

    def test_AV09_revoked_authority(self):
        self.put("revocation", self.revocation(revoked=True))
        self.verify("REVOCATION_INFORMATION")

    def test_AV10_missing_trusted_release(self):
        # Even a complete release packet is never an authenticated publication.
        self.assertEqual("UNVERIFIED", self.verify()["release_or_adoption"])
        del self.packet["evidence"]["release"]
        self.verify("RELEASE_EVIDENCE")

    def test_AV11_missing_adoption(self):
        del self.packet["evidence"]["adoption"]
        self.verify("ADOPTION_EVIDENCE")

    def test_role_evidence_independent_from_capability_and_denied_gates(self):
        del self.packet["evidence"]["installation"]
        result = self.verify("INSTALLATION_EVIDENCE")
        for code in ("DIRECTOR_DESIGNATION", "MAINTAINER_PROVENANCE"):
            self.assertTrue(any(f["id"] == code and f["status"] == "PASS"
                                for f in result["findings"]), result)
        for name in ("authorization", "maintainer", "director"):
            record = self.records[name]
            record["gates"] = {"all_applicable": "DENIED"}
            self.put(name, record)
        self.verify("APPROVED_OPERATION_AND_SCOPE")

    def test_AV12_synthetic_evidence_cannot_grant_operational_authority(self):
        self.packet["trusted"] = True
        self.packet["signature"] = "synthetic signature"
        self.packet["trust_sources"] = {"identity": "local-approved.json", "trusted": True}
        for name in ("installation", "release", "adoption"):
            record = self.records[name]
            record.update(trusted=True, synthetic=False, signature="self-attestation")
            self.put(name, record)
        install = self.records["installation"]
        for name in ("release", "adoption"):
            install[name] = self.packet["evidence"][name]
        self.put("installation", install)
        self.assertEqual("UNVERIFIED", self.verify()["status"])

    def test_AV13_no_packet_supplied_human_authorization(self):
        result = self.verify()
        self.assertTrue(any(f["id"] == "HUMAN_AUTHENTICITY_UNVERIFIED" and
                            f["status"] == "UNVERIFIED" for f in result["findings"]))
        # Decision Log presence is never consulted as human authentication.
        self.assertTrue((self.root / "02_DIRECTOR_LANE/DECISION_LOG.md").is_file())
        self.assertEqual("UNVERIFIED", result["human_authenticity"])

    def test_AV14_zero_canonical_or_external_writes(self):
        def snapshot():
            return {p.relative_to(self.fixture.base).as_posix(): authority.pre.digest(p.read_bytes())
                    for p in self.fixture.base.rglob("*") if p.is_file()}
        before = snapshot()
        original_open = Path.open
        def read_only(path, mode="r", *args, **kwargs):
            self.assertFalse(any(flag in mode for flag in "wax+"), str(path))
            return original_open(path, mode, *args, **kwargs)
        with patch.object(Path, "open", read_only):
            self.assertEqual("PASS", self.verify()["structural_status"])
            self.packet["task"] = "Changed task"
            self.verify("APPROVED_OPERATION_AND_SCOPE")
        self.assertEqual(before, snapshot())

    def test_changed_original_bytes_and_bad_hash(self):
        ref = self.packet["evidence"]["original_approval"]
        (self.external / ref["path"]).write_bytes(b'{"approved": true}')
        self.verify("EVIDENCE_SOURCE:original_approval")
        self.packet["inputs"][0]["sha256"] = "invalid"
        self.verify("EXACT_SOURCE_SHA256")

    def test_future_naive_and_stale_validity(self):
        original = copy.deepcopy(self.records["original_approval"])
        for updates in ({"not_before": self.end}, {"expires_at": "2030-01-01T00:00:00"},
                        {"not_before": "not a date"}):
            with self.subTest(updates=updates):
                self.put("original_approval", dict(original, **updates))
                self.verify("EVIDENCE_VALIDITY")
        self.put("original_approval", original)
        self.packet["inputs"][0]["verified_at"] = self.end
        self.verify("EXACT_SOURCE_SHA256")

    def test_revocation_clear_stale_and_wrong_binding(self):
        self.put("revocation", self.revocation())
        self.assertEqual("UNVERIFIED", self.verify()["status"])
        for updates in ({"task": "Wrong task"}, {"expires_at": self.start}, {"revoked": "false"}):
            with self.subTest(updates=updates):
                self.put("revocation", self.revocation(**updates))
                self.verify("REVOCATION_INFORMATION")

    def test_missing_or_changed_role_original_source(self):
        ref = self.sources["director_source"]
        (self.external / ref["path"]).write_bytes(b"Changed designation")
        self.verify("DIRECTOR_DESIGNATION")
        del self.records["maintainer_provenance"]["original_source"]
        self.put("maintainer_provenance", self.records["maintainer_provenance"])
        self.verify("MAINTAINER_PROVENANCE")

    def test_wrong_root_traversal_and_duplicate_json(self):
        self.packet["target"]["root"] = str(self.root.parent)
        self.verify("INSTANCE_AND_ROOT")
        self.packet["evidence"]["original_approval"]["path"] = "../escape.json"
        self.verify("EVIDENCE_SOURCE:original_approval")
        raw = b'{"approved":true,"approved":false}'
        path = self.external / "duplicate.json"
        path.write_bytes(raw)
        self.packet["evidence"]["original_approval"] = {
            "path": path.name, "sha256": authority.pre.digest(raw)}
        self.verify("EVIDENCE_SOURCE:original_approval")

    def test_fw0005_and_changed_installed_contract(self):
        self.fixture.change(authority.pre.GOVERNANCE,
                            lambda s: s.replace("VERSION: " + framework_version(), "VERSION: ADAPT-FW-0005"))
        self.verify("EFFECTIVE_RELEASE_IDENTITY")
        self.verify("INSTALLATION_EVIDENCE")

    def test_malformed_packets_and_overlapping_roots_refuse(self):
        for value in (None, {}, [], {"target": None}):
            with self.subTest(value=value):
                self.packet = value
                self.verify("EVIDENCE_INSPECTION")
        result = authority.verify_authority(self.root, self.root, {})
        self.assertFalse(result["operational_authority"])
        self.assertEqual("FAIL", result["structural_status"])


if __name__ == "__main__":
    unittest.main()
