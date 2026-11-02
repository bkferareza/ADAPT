"""SI-01..10: mechanical scaffold integration, not full agent-workflow acceptance."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fixtures import FRAMEWORK, QUALIFICATION, fresh_instance, distribution, isolate_recovery

MODES = ("MODE_A_EXISTING_SOLUTION", "MODE_B_REQUIREMENTS_ONLY")
RECOVERY = tuple("VALIDATION/recovery_" + name + ".py"
                 for name in ("preflight", "assembly", "runtime", "structural",
                              "supervised", "authority", "plan_review", "execution", "operational"))


def load(root, name):
    spec = importlib.util.spec_from_file_location(name, root / ("VALIDATION/" + name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class RecoveryScaffoldTests(unittest.TestCase):
    def setUp(self):
        base = QUALIFICATION / "scaffold-tests"
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.roots = []
        for mode in MODES:
            root = Path(self.temp.name) / mode / "ADAPT"
            root.parent.mkdir()
            fresh_instance(root, mode=mode)
            self.roots.append(root)

    def test_SI01_both_modes_components_and_imports(self):
        for root in self.roots:
            governance = (root / "00_FRAMEWORK/GOVERNANCE_RULES.md").read_text(encoding="utf-8")
            self.assertIn("DEFAULT AUTHORIZATION: HUMAN_SUPERVISED", governance)
            self.assertIn("A recovery packet must never authorize itself", governance)
            self.assertEqual(set(RECOVERY), {
                p.relative_to(root).as_posix() for p in (root / "VALIDATION").glob("*.py")})
            for ref in RECOVERY:
                self.assertTrue((root / ref).is_file(), ref)
                module = load(root, Path(ref).stem)
                if hasattr(module, "op"):
                    self.assertEqual(root / "TOOLS/supporting_modules/operator.py", Path(module.op.__file__))

    def test_SI02_framework_source_hashes(self):
        manifest = json.loads((FRAMEWORK / "TOOLS/MANIFEST.json").read_text())
        self.assertEqual(set(RECOVERY), set(manifest["instance_files"]))
        for root in self.roots:
            for ref in RECOVERY:
                self.assertEqual(hashlib.sha256((FRAMEWORK / ref).read_bytes()).hexdigest(),
                                 snapshot(root)[ref])
                self.assertEqual(manifest["instance_files"][ref], snapshot(root)[ref])

    def test_SI03_missing_tampered_payload_and_manifest(self):
        for root in self.roots:
            for ref in (*RECOVERY, "TOOLS/supporting_modules/operator.py", "TOOLS/MANIFEST.json"):
                path = root / ref
                original = path.read_bytes()
                for changed in (None, original + b"\n# tampered\n"):
                    if changed is None:
                        path.unlink()
                    else:
                        path.write_bytes(changed)
                    with self.assertRaises((ValueError, OSError)):
                        distribution.distribute(FRAMEWORK, root, verify=True)
                    path.write_bytes(original)
                self.assertTrue(distribution.distribute(FRAMEWORK, root, verify=True)["verified"])

    def test_SI04_ordinary_commands_unchanged(self):
        for root in self.roots:
            before = snapshot(root)
            for command, code in ((["state"], 0), (["doctor"], 0), (["prompt", "next"], 1)):
                result = subprocess.run([sys.executable, "-B", str(root / "TOOLS/adapt.py"),
                                         *command, "--instance", str(root), "--json"],
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(code, result.returncode, result.stdout + result.stderr)
                data = json.loads(result.stdout)
                if command == ["state"]:
                    self.assertEqual("NO", data["Blocked"])
                    self.assertEqual("NONE", data["ActiveBlockers"])
                    self.assertEqual("NEEDS_PLANNING", data["ExecutionReadiness"])
                if command[0] == "prompt":
                    self.assertEqual("BLOCKED", data["result"])
                    self.assertNotIn("invocation", data)
            self.assertEqual(before, snapshot(root))

    def test_SI05_fw0005_capability_refused(self):
        for root in self.roots:
            pre = load(root, "recovery_preflight")
            before = snapshot(root)
            packet = {"target": {"root": str(root), "identity": "Fixture"},
                      "purpose": pre.PURPOSE, "task": "Synthetic test", "executor": "Synthetic",
                      "evidence": {}}
            external = root.parent / "evidence"
            external.mkdir()
            result = pre.validate(root, external, packet)
            self.assertEqual("UNSUPPORTED_CAPABILITY", result["status"])
            self.assertIn("CAPABILITY", str(result["findings"]))
            self.assertFalse(result["operational_authority"])
            self.assertEqual(before, snapshot(root))

    def test_SI06_missing_authority_inside_synthetic_boundary(self):
        # Reach staging inside the fixed boundary, rather than merely testing
        # the outer path refusal. No approved-looking authorization is seeded.
        for installed in self.roots:
            runtime = load(installed, "recovery_runtime")
            isolate_recovery(runtime)
            runtime.SYNTHETIC_ROOT.mkdir(parents=True, exist_ok=True)
            from test_recovery_preflight import PreflightTests
            fixture = PreflightTests("test_valid_synthetic_purpose_b")
            with patch.object(tempfile, "tempdir", str(runtime.SYNTHETIC_ROOT)):
                fixture.setUp()
            try:
                root, external = fixture.root, fixture.external
                self.assertEqual("VALID_SYNTHETIC_PREFLIGHT",
                                 runtime.pre.validate(root, external, fixture.packet)["status"])
                del fixture.packet["evidence"]["authorization"]
                before, evidence = snapshot(root), snapshot(external)
                refused = runtime.pre.validate(root, external, fixture.packet)
                self.assertIn("AUTHORITY", str(refused["findings"]))
                result = runtime.execute(root, external, fixture.packet,
                                         {"plan_sha256": runtime.assembly.fingerprint({})})
                self.assertEqual("REFUSED", result["status"])
                self.assertFalse(result["operational_authority"])
                self.assertEqual(before, snapshot(root))
                self.assertEqual(evidence, snapshot(external))
                self.assertFalse(runtime.lock_path(root).exists())
            finally:
                fixture.doCleanups()

    def test_SI07_real_instance_boundary_refused(self):
        for root in self.roots:
            runtime = load(root, "recovery_runtime")
            before = snapshot(root)
            result = runtime.execute(root, root.parent, {}, {})
            self.assertEqual("REFUSED", result["status"])
            self.assertEqual("UNAUTHORIZED", result["real_execution"])
            self.assertIn("Outside fixed synthetic boundary", result["error"])
            self.assertEqual(before, snapshot(root))

    def test_SI08_no_historical_state_or_authority(self):
        for root in self.roots:
            for ref in ("02_DIRECTOR_LANE/BLOCKER_REGISTER.md", "02_DIRECTOR_LANE/DECISION_LOG.md",
                        "10_CONTEXT_ECONOMY/CONTEXT_INDEX.md", "10_CONTEXT_ECONOMY/STALE_CONTEXT_REGISTER.md"):
                text = (root / ref).read_text(encoding="utf-8")
                import re
                text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
                self.assertNotIn("BLK-001", text)
                self.assertNotIn("HO-007", text)
            self.assertEqual([], list((root / "10_CONTEXT_ECONOMY/CONTEXT_PACKS").iterdir()))
            self.assertEqual(set(RECOVERY), {p.relative_to(root).as_posix()
                                          for p in (root / "VALIDATION").rglob("*") if p.is_file()})
            for name in ("authorization.json", "installation.json", "adoption.json", "release.json"):
                self.assertEqual([], list(root.rglob(name)))

    def test_SI09_equivalent_recovery_contracts(self):
        refs = ("00_FRAMEWORK/GOVERNANCE_RULES.md", "10_CONTEXT_ECONOMY/CONTEXT_RULES.md",
                "07_GUARDRAILS/CONTEXT_GUARDRAIL.md", "15_COMMANDS_AND_DRIVERS/STOP_RULES.md",
                "15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md", *RECOVERY)
        for ref in refs:
            self.assertEqual((self.roots[0] / ref).read_bytes(), (self.roots[1] / ref).read_bytes())

    def test_SI10_inventory_manifest_and_standalone_imports(self):
        for root in self.roots:
            inventory = json.loads((root / "TOOLS/supporting_modules/instance_inventory.json").read_text())
            for ref in inventory["files"]:
                self.assertTrue((root / ref).is_file(), ref)
            script = "\n".join([
                "import importlib.util,json,pathlib,sys",
                f"root=pathlib.Path({str(root)!r})",
                f"for name in {tuple(Path(r).stem.removeprefix('recovery_') for r in RECOVERY)!r}:",
                " s=importlib.util.spec_from_file_location(name,root/('VALIDATION/recovery_'+name+'.py'))",
                " m=importlib.util.module_from_spec(s);s.loader.exec_module(m)",
                " if hasattr(m,'op'): assert pathlib.Path(m.op.__file__).is_relative_to(root)",
                "print('STANDALONE_IMPORTS_PASS')",
            ])
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            result = subprocess.run([sys.executable, "-I", "-B", "-c", script], cwd=root.parent,
                                    env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("STANDALONE_IMPORTS_PASS", result.stdout)

    def test_SI11_missing_or_changed_governance_refuses(self):
        for root in self.roots:
            for ref in distribution.RECOVERY_CONTRACTS:
                path = root / ref
                original = path.read_bytes()
                for changed in (None, original + b"\nChanged governance\n"):
                    if changed is None:
                        path.unlink()
                    else:
                        path.write_bytes(changed)
                    before = snapshot(root)
                    with self.assertRaisesRegex(ValueError, "governance contract"):
                        distribution.distribute(FRAMEWORK, root, verify=True)
                    self.assertEqual(before, snapshot(root))
                    path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
