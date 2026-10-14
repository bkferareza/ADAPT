"""Canonical-derived fixtures only; no client instance or network access."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "adapt.py"
FRAMEWORK = SCRIPT.parents[2]
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("toolkit", SCRIPT)
toolkit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toolkit)
sys.path.insert(0, str(FRAMEWORK / "TOOLS/tests"))
from fixtures import enrich_dispatch


class ToolkitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.instance = self.base / "instance"
        shutil.copytree(FRAMEWORK / "CANONICAL_STARTERS", self.instance)
        for name in ("CONTEXT_PACKS", "CONTEXT_DELTAS", "CONTEXT_SUMMARIES"):
            (self.instance / "10_CONTEXT_ECONOMY" / name).mkdir()
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.git("init")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "--allow-empty", "-m", "Temporary fixture")
        self.values = {field: "NONE" for field in toolkit.reader.FIELDS}
        self.values.update(ProjectName="Fixture", ProjectType="Web App",
                           DeploymentMode="MODE_A_EXISTING_SOLUTION", RoutingMode="PROTECTED_DEFAULT",
                           InitializationMode="FULL_EXTERNAL_ADAPT_INSTANCE_SCAFFOLD",
                           SourceTruthVersion="SOURCE_TRUTH_V0.1", ActiveMilestone="M01", ActiveCycle="C01",
                           CurrentAuthority="BACKEND_TEST", ActiveWorkcell="BACKEND_TEST",
                           ActiveHandoff="06_HANDOFFS/ACTIVE/HO-0001.md", ExecutionReadiness="READY",
                           CurrentPhase="EXECUTION", Blocked="NO", LastAction="Fixture initialization",
                           NextExpectedAction="Run atomic handoff dispatch", LastConsolidatedAt="NEVER", Notes="")
        self.write_state()
        registry = self.read(toolkit.REGISTRY)
        registry = registry.replace("## Status Values", "| BACKEND_TEST | Backend Developer | Test | ADAPT/03_WORKCELLS/BACKEND_TEST/ | 2026-10-15 | ACTIVE | Fixture |\n\n## Status Values")
        self.write(toolkit.REGISTRY, registry)
        folder = "03_WORKCELLS/BACKEND_TEST"
        identity = self.template("WORKCELL_IDENTITY_TEMPLATE.md").replace("{{ROLE}}_{{IDENTITY}}", "BACKEND_TEST")
        identity = identity.replace("{{IDENTITY}}", "Test").replace("{{ROLE}}", "Backend Developer")
        identity = identity.replace("02_DIRECTOR_LANE/SCOPE_CONTRACT_Backend Developer_Test.md", "02_DIRECTOR_LANE/SCOPE_CONTRACT_BACKEND_TEST.md")
        self.write(folder + "/WORKCELL_IDENTITY.md", identity)
        scope = self.template("SCOPE_CONTRACT_TEMPLATE.md").replace("{{ROLE}}_{{IDENTITY}}", "BACKEND_TEST")
        for token, value in {"IN_SCOPE_ITEM_1": "Inspect src/example.py", "IN_SCOPE_ITEM_2": "Report findings",
                             "IN_SCOPE_ITEM_N": "Stop after report", "PATH_PATTERN": "src/example.py",
                             "FILE_TYPES": "Python", "RESTRICTIONS": "Fixture only"}.items():
            scope = scope.replace("{{" + token + "}}", value)
        self.write("02_DIRECTOR_LANE/SCOPE_CONTRACT_BACKEND_TEST.md", scope)
        self.write(folder + "/DEFAULT_AGENT_BLUEPRINT.md", self.template("DEFAULT_AGENT_BLUEPRINT_TEMPLATE.md"))
        handoff = self.template("HANDOFF_TEMPLATE.md").replace("STATUS: DRAFT", "STATUS: ACTIVE")
        for token, value in {"HANDOFF_ID": "HO-0001", "FROM_WORKCELL_ID": "Director Lane",
                             "TO_WORKCELL_ID": "BACKEND_TEST", "SOURCE_TRUTH_VERSION": "SOURCE_TRUTH_V0.1",
                             "CONTEXT_PACK_ID": "CP-0001"}.items():
            handoff = handoff.replace("{{" + token + "}}", value)
        self.write(self.values["ActiveHandoff"], handoff)
        context = self.template("CONTEXT_PACK_TEMPLATE.md")
        context = context.replace("CP-{{SEQUENCE}}", "CP-0001")
        for token, value in {"WORKCELL_ID": "BACKEND_TEST", "HANDOFF_ID": "HO-0001",
                             "SOURCE_TRUTH_VERSION": "SOURCE_TRUTH_V0.1"}.items():
            context = context.replace("{{" + token + "}}", value)
        self.write("10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-0001.md", context)
        enrich_dispatch(self.instance)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True, check=True)

    def read(self, path):
        return (self.instance / path).read_text(encoding="utf-8")

    def write(self, path, content):
        target = self.instance / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def template(self, name):
        return self.read("08_TEMPLATES/" + name)

    def write_state(self):
        template = (FRAMEWORK / "CANONICAL_STARTERS" / toolkit.CP).read_text(encoding="utf-8")
        for field, value in self.values.items():
            import re
            template = re.sub(r"^\| " + field + r" \| .*? \|$",
                              lambda _: f"| {field} | {value} |", template, flags=re.M)
        self.write(toolkit.CP, template)

    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args,
                               "--instance", str(self.instance), "--json"],
                              capture_output=True, text=True, check=False)

    def expect_fail(self, code, *args):
        result = self.cli(*args)
        self.assertEqual(result.returncode, 1, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(any(d["id"] == code and d["status"] == "FAIL" for d in data["diagnostics"]), data)
        if args[0] == "prompt":
            self.assertNotIn("operator_preview", data)
        return data

    def snapshot(self):
        return {p.relative_to(self.instance).as_posix(): p.read_bytes()
                for p in self.instance.rglob("*") if p.is_file()}

    def test_end_to_end_determinism_and_no_mutation(self):
        before = self.snapshot()
        (self.repo / "example.txt").write_text("bounded fixture", encoding="utf-8")
        repo_before = {p.relative_to(self.repo).as_posix(): p.read_bytes()
                       for p in self.repo.rglob("*") if p.is_file()}
        for command in [("state",), ("doctor",), ("prompt", "next"),
                        ("evidence", "--repo", str(self.repo), "--file", "example.txt")]:
            with self.subTest(command=command):
                first, second = self.cli(*command), self.cli(*command)
                self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
                self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
                self.assertEqual(first.stdout, second.stdout)
                data = json.loads(first.stdout)
                if command[0] == "state":
                    self.assertEqual(list(data), list(toolkit.reader.FIELDS))
                if command[0] == "doctor":
                    self.assertFalse(any(d["status"] == "FAIL" for d in data["diagnostics"]))
                    self.assertTrue(any(d["status"] == "NOT_CHECKED" for d in data["diagnostics"]))
                if command[0] == "prompt":
                    self.assertFalse(data["execution_authorized"])
                    self.assertTrue(data["preview_only"])
                    self.assertEqual(data["invocation"]["command"], "Run atomic handoff dispatch")
                if command[0] == "evidence":
                    self.assertEqual(data["changed_paths"], ["example.txt"])
                    self.assertEqual(len(data["artifacts"]), 3)
                    self.assertNotIn("bounded fixture", first.stdout)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(repo_before, {p.relative_to(self.repo).as_posix(): p.read_bytes()
                                      for p in self.repo.rglob("*") if p.is_file()})

    def test_missing_control_plane(self):
        (self.instance / toolkit.CP).unlink()
        self.expect_fail("ARTIFACT_MISSING", "state")

    def test_duplicate_control_plane(self):
        content = self.read(toolkit.CP)
        content = content.replace("| Notes |  |", "| Notes |  |\n| Notes | duplicate |")
        self.write(toolkit.CP, content)
        self.expect_fail("CP_STRUCTURE", "state")

    def test_authority_conflict(self):
        self.values["CurrentAuthority"] = "Director Lane"
        self.write_state()
        self.expect_fail("AUTHORITY_CONFLICT", "prompt", "next")

    def test_missing_active_handoff(self):
        (self.instance / self.values["ActiveHandoff"]).unlink()
        self.expect_fail("ARTIFACT_MISSING", "prompt", "next")
        self.expect_fail("ARTIFACT_MISSING", "doctor")

    def test_unknown_workcell(self):
        self.write(toolkit.REGISTRY, (FRAMEWORK / "CANONICAL_STARTERS" / toolkit.REGISTRY).read_text(encoding="utf-8"))
        self.expect_fail("WORKCELL_UNKNOWN", "prompt", "next")

    def test_incomplete_scope(self):
        ref = "02_DIRECTOR_LANE/SCOPE_CONTRACT_BACKEND_TEST.md"
        self.write(ref, self.read(ref).replace("src/example.py", "{{PATH_PATTERN}}"))
        self.expect_fail("SCOPE_INCOMPLETE", "prompt", "next")

    def test_unsupported_next_action(self):
        ref = self.values["ActiveHandoff"]
        self.write(ref, self.read(ref).replace("| Command | Run atomic handoff dispatch |", "| Command | Run QA validation |"))
        self.expect_fail("NEXT_SELECTION_UNSUPPORTED", "prompt", "next")

    def test_missing_repository_and_invalid_root(self):
        self.expect_fail("PATH_ROOT", "evidence", "--repo", str(self.base / "absent"))
        with self.assertRaises(toolkit.Problem):
            toolkit.root_path(self.base / "absent")

    def test_invalid_references(self):
        for reference in ("../escape.md", "/absolute.md", "https://example.invalid/x", "C:\\secret", ".git/config"):
            with self.subTest(path=reference), self.assertRaises(toolkit.Problem):
                toolkit.bounded(self.instance, reference)
        self.expect_fail("PATH_BOUNDARY", "evidence", "--repo", str(self.repo), "--file", "../escape.md")

    def test_malformed_registry(self):
        self.write(toolkit.REGISTRY, self.read(toolkit.REGISTRY).replace("| Workcell ID |", "| Other |"))
        self.expect_fail("ARTIFACT_TABLE", "prompt", "next")

    def test_context_conflict(self):
        ref = "10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-0001.md"
        self.write(ref, self.read(ref).replace("WORKCELL_ID: BACKEND_TEST", "WORKCELL_ID: OTHER"))
        self.expect_fail("CONTEXT_BINDING", "prompt", "next")

    def test_register_consistency_and_closed_preview(self):
        ref = "02_DIRECTOR_LANE/BLOCKER_REGISTER.md"
        self.write(ref, self.read(ref).replace("## Severity Values", "| BLK-001 | HIGH | Example | Fixture | BI-001 | Director | 2026-10-15 | Director | OPEN | NONE | NONE |\n\n## Severity Values"))
        self.expect_fail("CP-C10", "doctor")
        self.expect_fail("BLOCKER_SCOPE_UNVERIFIED", "prompt", "next")

    def test_starter_placeholders_unverified_not_failed(self):
        self.write(toolkit.CP, (FRAMEWORK / "CANONICAL_STARTERS" / toolkit.CP).read_text(encoding="utf-8"))
        result = self.cli("doctor")
        self.assertEqual(result.returncode, 0, result.stdout)
        data = json.loads(result.stdout)
        self.assertTrue(any(d["status"] == "UNVERIFIED" for d in data["diagnostics"]))
        self.assertFalse(any(d["status"] == "FAIL" for d in data["diagnostics"]))

    def test_human_output_and_usage_error(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "state", "--instance", str(self.instance)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("ProjectName: Fixture", result.stdout)
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "state"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)

    def test_git_queries_are_bounded_read_only(self):
        with patch.object(toolkit.subprocess, "run", wraps=subprocess.run) as run:
            toolkit.evidence(self.instance, str(self.repo), [])
        forbidden = {"fetch", "pull", "checkout", "add", "commit", "reset", "clean", "push"}
        self.assertEqual(run.call_count, 4)
        for call in run.call_args_list:
            self.assertFalse(forbidden.intersection(call.args[0]))
            self.assertNotIn("shell", call.kwargs)
            self.assertEqual(call.kwargs["env"]["GIT_OPTIONAL_LOCKS"], "0")

    def test_state_reader_output_compatibility(self):
        result = self.cli("state")
        legacy = subprocess.run([sys.executable, "-B", str(FRAMEWORK / "EXPERIMENTS/STATE_READER/state_reader.py"),
                                 "--instance", str(self.instance), "--json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, legacy.returncode)
        self.assertEqual(result.stdout, legacy.stdout)

    def test_schema_drift_and_invalid_enum(self):
        ref = toolkit.SCHEMA
        self.write(ref, self.read(ref).replace("### ProjectName", "### DifferentName"))
        self.expect_fail("SCHEMA_COMPATIBILITY", "doctor")
        self.values["CurrentPhase"] = "INVENTED_PHASE"
        self.write_state()
        self.expect_fail("CP_ENUM", "doctor")
        self.expect_fail("PREVIEW_STATE_UNVERIFIED", "prompt", "next")

    def test_malformed_handoff_and_wrong_target(self):
        ref = self.values["ActiveHandoff"]
        original = self.read(ref)
        self.write(ref, original.replace("HANDOFF_ID: HO-0001", "HANDOFF_ID: HO-0001\nHANDOFF_ID: HO-0002"))
        self.expect_fail("BIND_HEADER", "prompt", "next")
        self.write(ref, original.replace("TO_WORKCELL / TO_LANE: BACKEND_TEST", "TO_WORKCELL / TO_LANE: OTHER"))
        self.expect_fail("HANDOFF_BINDING", "prompt", "next")

    def test_handoff_reference_outside_active(self):
        self.values["ActiveHandoff"] = "06_HANDOFFS/CONSUMED/HO-0001.md"
        self.write_state()
        self.expect_fail("HANDOFF_LOCATION", "prompt", "next")

    def test_absent_evidence_file_and_limits(self):
        result = self.cli("evidence", "--repo", str(self.repo), "--file", "missing.txt")
        self.assertEqual(result.returncode, 0, result.stdout)
        files = json.loads(result.stdout)["artifacts"]
        self.assertEqual(files[-1], {"root": "repo", "path": "missing.txt", "exists": False})
        with self.assertRaises(toolkit.Problem):
            toolkit.evidence(self.instance, str(self.repo), ["file"] * 101)
        target = self.repo / "oversized.txt"
        target.write_bytes(b"x" * (toolkit.MAX_BYTES + 1))
        self.expect_fail("EVIDENCE_LIMIT", "evidence", "--repo", str(self.repo), "--file", target.name)

    def test_diagnostics_do_not_echo_malformed_artifact_values(self):
        self.write(toolkit.CP, self.read(toolkit.CP).replace("| Notes |  |", "| Notes | private-sentinel | extra |"))
        result = self.cli("state")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("private-sentinel", result.stdout + result.stderr)

    def test_missing_required_instance_file_and_inactive_rule(self):
        (self.instance / "05_VALIDATION/QA_STRATEGY.md").unlink()
        self.expect_fail("INSTANCE_FILE", "doctor")
        data = json.loads(self.cli("doctor").stdout)
        self.assertEqual(next(d["status"] for d in data["diagnostics"] if d["id"] == "CP-C01"), "NOT_EXERCISED")

    def test_failures_do_not_mutate_instance(self):
        self.values["CurrentAuthority"] = "OTHER"
        self.write_state()
        before = self.snapshot()
        self.expect_fail("AUTHORITY_CONFLICT", "prompt", "next")
        self.assertEqual(before, self.snapshot())

    def test_declared_handoff_and_context_id_conflicts(self):
        self.values["ActiveHandoff"] = "HO-0001"
        self.write_state()
        ref = "06_HANDOFFS/ACTIVE/HO-0001.md"
        original = self.read(ref)
        self.write(ref, original.replace("HANDOFF_ID: HO-0001", "HANDOFF_ID: HO-9999"))
        self.expect_fail("HANDOFF_BINDING", "prompt", "next")
        self.write(ref, original)
        ref = "10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-0001.md"
        self.write(ref, self.read(ref).replace("CONTEXT_PACK_ID: CP-0001", "CONTEXT_PACK_ID: CP-9999"))
        self.expect_fail("CONTEXT_BINDING", "prompt", "next")

    def test_empty_binding_header_cannot_consume_next_line(self):
        ref = self.values["ActiveHandoff"]
        self.write(ref, self.read(ref).replace("FROM_WORKCELL: Director Lane", "FROM_WORKCELL:"))
        self.expect_fail("BIND_HEADER", "prompt", "next")

    def test_unknown_register_status(self):
        ref = "02_DIRECTOR_LANE/BLOCKER_REGISTER.md"
        self.write(ref, self.read(ref).replace("## Severity Values", "| BLK-001 | HIGH | Example | Fixture | BI-001 | Director | 2026-10-15 | Director | UNKNOWN | NONE | NONE |\n\n## Severity Values"))
        self.expect_fail("REGISTER_STATE", "prompt", "next")
        self.expect_fail("REGISTER_STATE", "doctor")


if __name__ == "__main__":
    unittest.main()
