"""Human maintenance entry scope checks; synthetic claims never grant writes."""
import builtins
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

from fixtures import FRAMEWORK

spec = importlib.util.spec_from_file_location(
    "supervised", FRAMEWORK / "VALIDATION/recovery_supervised.py")
supervised = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supervised)


class SupervisedTests(unittest.TestCase):
    def setUp(self):
        now = datetime.now(timezone.utc)
        self.start = (now - timedelta(hours=1)).isoformat()
        self.approved = (now - timedelta(minutes=20)).isoformat()
        self.checked = (now - timedelta(seconds=1)).isoformat()
        self.end = (now + timedelta(hours=1)).isoformat()
        self.packet = {
            "target": {"root": "D:/isolated-synthetic/ADAPT", "identity": "SYNTHETIC-001"},
            "workcell": "external-recovery-steward", "purpose": "RECOVERY_BOOTSTRAP_AUTHORIZATION",
            "task": "synthetic-bounded-assembly", "executor": "synthetic-executor",
            "writes": [{"path": "10_CONTEXT_ECONOMY/CONTEXT_PACK_INDEX.md", "fields": ["Status"],
                        "operation": "set_fields", "before_sha256": "a" * 64}],
            "inputs": [{"path": "00_FRAMEWORK/GOVERNANCE_RULES.md", "sha256": "b" * 64,
                        "verified_at": self.checked}],
            "evidence": {"original_approval": {"path": "approval-evidence.txt", "sha256": "c" * 64}},
            "ids": {"cp": "CP-SYNTHETIC"}, "completion": {"destination": "synthetic-human-review"},
            "gates": {"all_applicable": "APPROVED"}, "operation_reference": "SYNTHETIC-OP-001",
            "audit_reference": "SYNTHETIC-AUDIT-001"}
        self.config = {"target": deepcopy(self.packet["target"]),
                       "workcell": self.packet["workcell"], "executor": self.packet["executor"],
                       "required_gates": ["all_applicable"],
                       "authorities": {"Human Director": "synthetic-director",
                                       "Human Framework Maintainer": "synthetic-maintainer"}}
        self.response = {"synthetic": True, "binding": deepcopy(self.packet),
            "approved_at": self.approved, "checked_at": self.checked, "not_before": self.start,
            "expires_at": self.end, "withdrawn": False,
            "audit_reference": self.packet["audit_reference"], "audit_preservation_reference": "TEST-RETENTION",
            "approvals": [{"role": role, "human": human, "approved": True,
                "approved_at": self.approved,
                "role_basis_reference": "TEST-ROLE-" + role, "designation_reference": "TEST-DESIGNATION",
                "approval_reference": "TEST-APPROVAL-" + role}
                for role, human in self.config["authorities"].items()]}

    def verify(self, response=None, packet=None, config=None):
        result = supervised.SupervisedVerifier(
            self.config if config is None else config).verify(
                self.packet if packet is None else packet,
                human_authorization=self.response if response is None else response)
        self.assertFalse(result["operational_authority"])
        self.assertEqual("UNVERIFIED", result["release_or_adoption"])
        return result

    def refused(self, **kwargs):
        result = self.verify(**kwargs)
        self.assertEqual("AUTHORITY_UNVERIFIED", result["status"], result)
        return result

    def test_HS01_valid_synthetic_evidence(self):
        result = self.verify()
        self.assertEqual("SUPERVISED_EVIDENCE_VALID", result["status"], result)
        self.assertEqual("PASS", result["structural_status"])
        self.assertEqual("PASS", result["scope_status"])
        self.assertEqual("SYNTHETIC_VALID", result["human_authorization_evidence"])
        self.assertTrue(result["outstanding_requirements"])
        for field in ("audit_preservation_reference", "approvals", "binding"):
            with self.subTest(missing=field):
                response = deepcopy(self.response)
                del response[field]
                self.refused(response=response)

    def test_HS02_missing_explicit_maintenance_input_refuses(self):
        for verifier in (supervised.SupervisedVerifier(), supervised.SupervisedVerifier(self.config)):
            result = verifier.verify(self.packet)
            self.assertEqual("AUTHORITY_UNVERIFIED", result["status"])
            self.assertFalse(result["operational_authority"])
        self.assertEqual("AUTHORITY_UNVERIFIED", supervised.SupervisedVerifier().verify(
            self.packet, human_authorization=self.response)["status"])

    def test_HS03_packet_self_approval_refuses(self):
        self.packet.update(approved=True, trusted_host="local-approved.json",
                           authorities=self.config["authorities"], mode="HUMAN_SUPERVISED")
        self.assertEqual("AUTHORITY_UNVERIFIED",
                         supervised.SupervisedVerifier(self.config).verify(self.packet)["status"])
        self.packet["human_authorization"] = deepcopy(self.response)
        self.assertEqual("AUTHORITY_UNVERIFIED",
                         supervised.SupervisedVerifier(self.config).verify(self.packet)["status"])

    def test_HS04_local_boolean_is_insufficient(self):
        self.refused(response={"approved": True})
        self.refused(response={"approved": True, "binding": deepcopy(self.packet)})

    def test_HS05_wrong_governance_capacity_refuses(self):
        for field, value in (("role", "Director"), ("human", "wrong-human"),
                             ("approved", False),
                             ("role_basis_reference", ""), ("designation_reference", "")):
            with self.subTest(field=field):
                response = deepcopy(self.response)
                response["approvals"][0][field] = value
                self.refused(response=response)

    def test_HS06_wrong_instance_refuses(self):
        for field, value in (("target", {"root": "D:/wrong", "identity": "WRONG"}),
                             ("workcell", "wrong-workcell"), ("executor", "wrong-executor")):
            with self.subTest(field=field):
                packet, response = deepcopy(self.packet), deepcopy(self.response)
                packet[field] = value
                self.refused(packet=packet)
                response["binding"] = deepcopy(packet)
                self.refused(packet=packet, response=response)

    def test_HS07_unapproved_scope_refuses(self):
        for field, value in (("path", "01_CONTROL/CONTROL_PLANE.md"), ("fields", ["Blocked"]),
                             ("operation", "append_row"), ("before_sha256", "d" * 64)):
            with self.subTest(field=field):
                packet = deepcopy(self.packet)
                packet["writes"][0][field] = value
                self.refused(packet=packet)
        for field in ("task", "operation_reference", "audit_reference", "purpose"):
            with self.subTest(binding=field):
                packet = deepcopy(self.packet)
                packet[field] = "changed"
                self.refused(packet=packet)
        for field in ("inputs", "evidence"):
            packet = deepcopy(self.packet)
            reference = packet[field][0] if field == "inputs" else packet[field]["original_approval"]
            reference["sha256"] = "d" * 64
            self.refused(packet=packet)
        for field, value in (("gates", {"all_applicable": "DENIED"}),
                             ("ids", {}), ("completion", {})):
            packet = deepcopy(self.packet)
            packet[field] = value
            self.refused(packet=packet)
        packet = deepcopy(self.packet)
        packet["writes"][0]["path"] = "../outside"
        self.refused(packet=packet)

    def test_HS08_expired_or_withdrawn_refuses(self):
        for field, value in (("expires_at", self.start), ("withdrawn", True),
                             ("not_before", self.end), ("checked_at", self.end),
                             ("approved_at", "2026-01-01T00:00:00")):
            with self.subTest(field=field):
                response = deepcopy(self.response)
                response[field] = value
                self.refused(response=response)
        verifier = supervised.SupervisedVerifier(self.config)
        self.assertEqual("SUPERVISED_EVIDENCE_VALID", verifier.verify(
            self.packet, human_authorization=self.response)["status"])
        self.response["withdrawn"] = True
        self.assertEqual("AUTHORITY_UNVERIFIED", verifier.verify(
            self.packet, human_authorization=self.response)["status"])

    def test_HS09_dual_role_separation(self):
        for role in self.config["authorities"]:
            self.config["authorities"][role] = "same-synthetic-human"
        for approval in self.response["approvals"]:
            approval["human"] = "same-synthetic-human"
        self.assertEqual("SUPERVISED_EVIDENCE_VALID", self.verify()["status"])
        response = deepcopy(self.response)
        response["approvals"] = response["approvals"][:1]
        self.refused(response=response)
        self.response["approvals"][1]["approval_reference"] = self.response["approvals"][0]["approval_reference"]
        self.refused()

    def test_HS10_no_provider_or_network_dependency(self):
        original_import = builtins.__import__
        def without_github(name, *args, **kwargs):
            if any(token in name for token in ("github", "recovery_trust", "supervised_host")):
                raise ImportError("GitHub unavailable")
            return original_import(name, *args, **kwargs)
        with patch("builtins.__import__", side_effect=without_github), \
             patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden")):
            # Re-import with provider imports and network blocked.
            spec.loader.exec_module(supervised)
            self.assertEqual("SUPERVISED_EVIDENCE_VALID", self.verify()["status"])

    def test_HS11_no_operational_authority_even_if_mislabeled(self):
        for synthetic in (True, False):
            self.response["synthetic"] = synthetic
            result = self.verify()
            self.assertEqual("SUPERVISED_EVIDENCE_VALID", result["status"])
            self.assertFalse(result["operational_authority"])
            self.assertIn("PRODUCTION_WRITER_AUTHORIZATION", result["outstanding_requirements"])

    def test_HS12_zero_canonical_writes(self):
        packet, response, config = deepcopy(self.packet), deepcopy(self.response), deepcopy(self.config)
        with patch("builtins.open", side_effect=AssertionError("File access forbidden")), \
             patch.object(Path, "open", side_effect=AssertionError("File access forbidden")), \
             patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden")):
            self.assertEqual("SUPERVISED_EVIDENCE_VALID", self.verify()["status"])
            self.refused(packet={})
        self.assertEqual(packet, self.packet)
        self.assertEqual(response, self.response)
        self.assertEqual(config, self.config)


if __name__ == "__main__":
    unittest.main()
