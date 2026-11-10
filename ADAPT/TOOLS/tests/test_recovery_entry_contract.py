"""Prospective document contract checks; no recovery runtime or real approvals.

Refusal cases check mandatory policy clauses, not automated packet enforcement.
Runtime STOP/freshness and normal distribution are exercised by test_release.
"""
from pathlib import Path
import re
import tempfile
import unittest

from fixtures import FRAMEWORK, QUALIFICATION, fresh_instance, framework_version


class RecoveryEntryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = (FRAMEWORK / "CANONICAL_STARTERS/00_FRAMEWORK/GOVERNANCE_RULES.md").read_text(encoding="utf-8")
        cls.entry = cls.contract.split("#### Prospective amendment:", 1)[1]

    def require(self, *clauses):
        for clause in clauses:
            self.assertIn(clause, self.entry)

    def test_01_valid_blocked_submission_has_external_entry_and_two_purposes(self):
        self.require("may submit directly", "No ordinary context pack or completed 13-step dispatch is required",
                     "Exact instance identity and resolved root", "before SHA256",
                     "preserved raw diagnostics and failed attempts", "why ordinary Director context/Steward assembly is unavailable",
                     "FRAMEWORK_LEARNING_RECEIPT", "RECOVERY_BOOTSTRAP_AUTHORIZATION",
                     "EXTERNAL_RECEIPT, ORDINARY_DISPATCH_NOT_PERFORMED",
                     "Director-origin escalation arrival", "receipt alone neither registers nor promotes an FLC",
                     "AUTHORIZATION_ONLY / EXECUTION_STOP_REQUIRED", "then STOP")

    def test_02_missing_director_provenance_must_stop(self):
        self.require("Actual Human Director provenance: original human input", "applicable Director designation",
                     "A Driver, Maintainer or AI claiming Director authority is insufficient",
                     "Missing, unverifiable, conflicting, changed or out-of-scope inputs require STOP")

    def test_03_missing_maintainer_authority_must_stop(self):
        self.require("Applicable Human Maintainer authority: original human direction",
                     "expressly approved mutation scope", "Missing, unverifiable, conflicting, changed or out-of-scope inputs require STOP")

    def test_04_unrelated_mutation_is_forbidden_and_history_preserved(self):
        self.require("only allowed mutations are the selected external receipt",
                     "within its approved paths and operations", "Unrelated",
                     "mutation, canonical state/framework writes, FLC registration and operational",
                     "execution are rejected", "retry counters unchanged", "never reset counters, resolve blockers")

    def test_05_ordinary_execution_stays_blocked_after_entry(self):
        self.require("Ordinary execution remains blocked", "registered blocker resolution with required sign-off",
                     "separately authorized", "operational handback", "Resolution alone grants no")

    def test_06_stale_context_cannot_be_validated_by_entry(self):
        self.require("Entry does not validate stale context or override CONTEXT_GUARDRAIL or Gate 10",
                     "independently valid current context", "separately effective recovery assembly contract")

    def test_07_future_scaffold_carries_same_entry_without_historical_state(self):
        evidence = QUALIFICATION / "fw0006-entry-slice"
        evidence.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=evidence) as folder:
            target = Path(folder) / "ADAPT"
            fresh_instance(target)
            copied = (target / "00_FRAMEWORK/GOVERNANCE_RULES.md").read_text(encoding="utf-8")
            self.assertEqual(self.entry, copied.split("#### Prospective amendment:", 1)[1])
            for path in ("02_DIRECTOR_LANE/BLOCKER_REGISTER.md", "02_DIRECTOR_LANE/GAP_REGISTER.md"):
                text = (target / path).read_text(encoding="utf-8")
                text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
                self.assertNotIn("BLK-001", text)
                self.assertNotIn("GAP-T14-", text)
            self.assertIn("FLC-005: PROMOTED", copied)

    def test_08_normal_scaffold_sources_and_version_not_redefined(self):
        register = (FRAMEWORK / "FRAMEWORK_LEARNING_REGISTER.md").read_text(encoding="utf-8")
        self.assertIn("Current Framework Version: " + framework_version(), register)
        self.require("FLC-005 promoted under Rule 14", "Presence",
                     "in an unreleased source tree or test scaffold is not activation or authority")
        output = (FRAMEWORK / "SCAFFOLD_OUTPUT_CONTRACT.md").read_text(encoding="utf-8")
        self.assertIn("Copy the complete canonical file", output)
        director = (FRAMEWORK / "CANONICAL_STARTERS/15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_DIRECTOR.md").read_text(encoding="utf-8")
        self.assertIn("Every Director Lane action follows the 13-step Atomic Handoff Dispatch protocol", director)


if __name__ == "__main__":
    unittest.main()
