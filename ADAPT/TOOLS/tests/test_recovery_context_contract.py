"""RC-01..10 document contracts and synthetic scaffold propagation only.

No synthetic authorization is accepted by a recovery runtime here: that runtime
is exercised separately in test_recovery_operational. Existing ordinary runtime
refusal regressions live in test_release.
"""
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest

from fixtures import FRAMEWORK, QUALIFICATION, fresh_instance, distribution


STARTERS = FRAMEWORK / "CANONICAL_STARTERS"
OWNER = "00_FRAMEWORK/GOVERNANCE_RULES.md"
TITLE = "##### Purpose B completion: bounded recovery context assembly"
REFERENCES = (
    "07_GUARDRAILS/CONTEXT_GUARDRAIL.md",
    "10_CONTEXT_ECONOMY/CONTEXT_RULES.md",
    "15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_CONTEXT_STEWARD.md",
    "15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_DIRECTOR.md",
    "15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md",
    "15_COMMANDS_AND_DRIVERS/STOP_RULES.md",
)


class RecoveryContextContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = (STARTERS / OWNER).read_text(encoding="utf-8").split(TITLE, 1)[1]

    def require(self, *clauses):
        # Normalize wrapping; assertions check policy text, never runtime behavior.
        body = " ".join(self.body.split())
        for clause in clauses:
            self.assertIn(clause, body)

    def test_rc01_effective_applicable_authorization_contract(self):
        self.require("FW-0006: This is the single normative assembly contract", "lawful release and installation/adoption",
                     "external authorization alone cannot enable it",
                     "original Human Maintainer direction", "all applicable human gates",
                     "DEPLOYMENT_ACCEPTANCE_REQUIRED")

    def test_rc02_exact_target_purpose_scope_and_executor_contract(self):
        self.require("exactly one resolved instance root and identity, one purpose",
                     "RECOVERY_BOOTSTRAP_AUTHORIZATION", "path/field/operation allowlist",
                     "explicitly named operator delegated by that human",
                     "cannot designate itself as Human Maintainer or Human Director",
                     "not ordinary Context Steward dispatch")

    def test_rc03_missing_authority_sources_changed_hashes_contract(self):
        self.require("Missing or invalid authority/source evidence produces STOP without canonical mutation",
                     "Changed input hashes produce STOP", "before each write",
                     "Missing/unregistered source", "unsupported prerequisites",
                     "separately lawful authorization bound to the observed partial state")

    def test_rc04_stale_ordinary_context_and_guardrail_contract(self):
        self.require("Keep stale ordinary packs invalid", "never reconstructed from a stale pack",
                     "historical recovery evidence", "It is never indexed ACTIVE for ordinary use")
        guard = (STARTERS / REFERENCES[0]).read_text(encoding="utf-8")
        self.assertIn("There is no override for this guardrail", guard)
        self.assertIn("An archived recovery pack cannot satisfy ordinary context requirements", guard)

    def test_rc05_source_hash_and_completion_manifest_contract(self):
        self.require("SHA256 of raw bytes, verification time, evidence class, inclusion reason",
                     "current registered source version matching SourceTruthVersion",
                     "final output hashes belong in the external completion manifest",
                     "avoiding self-hash/circular references", "before/after SHA256")

    def test_rc06_closed_write_surface_contract(self):
        table = self.body.split("The complete possible write surface is:", 1)[1].split(
            "The authorization must enumerate", 1)[0]
        paths = re.findall(r"^\| ((?:10_CONTEXT_ECONOMY|06_HANDOFFS|02_DIRECTOR_LANE)/.*?) \|", table, re.M)
        self.assertEqual(paths, [
            "10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-{sequence}.md",
            "10_CONTEXT_ECONOMY/CONTEXT_INDEX.md",
            "10_CONTEXT_ECONOMY/STALE_CONTEXT_REGISTER.md",
            "10_CONTEXT_ECONOMY/CONTEXT_DELTAS/CD-{sequence}.md",
            "06_HANDOFFS/ACTIVE/HO-{sequence}.md",
            "02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md",
        ])
        self.require("All other canonical writes are rejected", "Reject traversal, symlink/reparse redirection",
                     "Reject out-of-scope writes", "never reuse an issued ID",
                     "inability to exclude concurrent writers is STOP")

    def test_rc07_existing_schema_integration_contract(self):
        pack = (STARTERS / "08_TEMPLATES/CONTEXT_PACK_TEMPLATE.md").read_text(encoding="utf-8")
        for field in ("STATUS", "CONTEXT_PACK_ID", "WORKCELL_ID", "HANDOFF_ID",
                      "SOURCE_TRUTH_VERSION", "DATE_ASSEMBLED", "CONTEXT_SIZE"):
            self.assertRegex(pack, rf"(?m)^{field}:")
        index = (STARTERS / "10_CONTEXT_ECONOMY/CONTEXT_INDEX.md").read_text(encoding="utf-8")
        for status in ("ACTIVE", "STALE", "SUPERSEDED", "ARCHIVED"):
            self.assertIn(f"- {status} —", index)
        self.require("No new lifecycle statuses are introduced", "Do not mark stale records RESOLVED or ACCEPTED_RISK",
                     "PRECEDING_CONTEXT_PACK_ID = this new CP-ID", "LastContextDelta = actual CD-ID",
                     "final schema/index/stale/delta/handoff/control-plane consistency",
                     "HANDOFF_TEMPLATE.md", "Do not make the emitted HO the control plane ActiveHandoff")

    def test_rc08_completion_preserves_blockers_and_requires_handback_contract(self):
        self.require("Completion does not resolve any blocker, reset exhausted attempt counts",
                     "launch the next registered command", "Separate registered blocker resolution",
                     "separately authorized operational handback", "then STOP",
                     "No change to Blocked, ActiveBlockers, ActiveGaps or ExecutionReadiness is authorized")

    def test_rc09_synthetic_fresh_scaffold_copies_contract_without_history(self):
        evidence = QUALIFICATION / "fw0006-context-slice"
        evidence.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=evidence) as folder:
            target = Path(folder) / "ADAPT"
            fresh_instance(target)
            self.assertEqual(self.body, (target / OWNER).read_text(encoding="utf-8").split(TITLE, 1)[1])
            for ref in REFERENCES:
                expected = (STARTERS / ref).read_text(encoding="utf-8").replace(
                    "PROJECT: {{PROJECT_NAME}}", "PROJECT: Fixture")
                self.assertEqual(expected, (target / ref).read_text(encoding="utf-8"))
            for ref in ("02_DIRECTOR_LANE/BLOCKER_REGISTER.md", "10_CONTEXT_ECONOMY/CONTEXT_INDEX.md",
                        "10_CONTEXT_ECONOMY/STALE_CONTEXT_REGISTER.md"):
                actual = re.sub(r"<!--.*?-->", "", (target / ref).read_text(encoding="utf-8"), flags=re.S)
                self.assertNotIn("BLK-001", actual)
                self.assertNotIn("ADAPT-DEV", actual)
            self.assertEqual([], list((target / "10_CONTEXT_ECONOMY/CONTEXT_PACKS").iterdir()))
            distribution.distribute(FRAMEWORK, target, verify=True)

    def test_rc10_inventory_manifest_and_ordinary_workflow_compatibility(self):
        inventory = json.loads((FRAMEWORK / "TOOLS/supporting_modules/instance_inventory.json").read_text())
        for ref in (OWNER, *REFERENCES):
            self.assertIn(ref, inventory["files"])
        manifest = json.loads((FRAMEWORK / "TOOLS/MANIFEST.json").read_text())
        for ref, expected in manifest["files"].items():
            self.assertEqual(expected, hashlib.sha256((FRAMEWORK / "TOOLS" / ref).read_bytes()).hexdigest())
        steward = (STARTERS / REFERENCES[2]).read_text(encoding="utf-8")
        self.assertIn("Every Context Steward action follows the 13-step Atomic Handoff Dispatch protocol", steward)
        self.assertIn("For ordinary context supporting an approved Onboard request", steward)
        register = (FRAMEWORK / "FRAMEWORK_LEARNING_REGISTER.md").read_text(encoding="utf-8")
        self.assertIn("Current Framework Version: ADAPT-FW-0006", register)
        owners = [p for p in STARTERS.rglob("*.md") if TITLE in p.read_text(encoding="utf-8")]
        self.assertEqual([STARTERS / OWNER], owners)


if __name__ == "__main__":
    unittest.main()
