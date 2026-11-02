"""Both-mode installed-tool acceptance, reusing Checklist D and real writers.

Only test fixture boundaries are relocated. Installed writer code and allowlists
are unchanged; neither packet fields nor environment grant a production root.
"""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import json
import subprocess
import sys

from fixtures import FRAMEWORK, QUALIFICATION, fresh_instance, distribution, isolate_recovery
import test_recovery_end_to_end as end
import test_recovery_preflight as fixture_module


class InstalledAcceptance:
    mode = None

    def setUp(self):
        def scaffold(root):
            fresh_instance(root, mode=self.mode)
            verified = distribution.distribute(FRAMEWORK, root, verify=True)
            end.save(root.parent / "clean-scaffold.json", {
                "mode": self.mode, "distribution": verified,
                "hashes": end.rt._snapshot(root),
                "state": end.pre.op.state(root), "doctor": end.pre.op.doctor(root)})

        with patch.object(fixture_module, "fresh_instance", side_effect=scaffold):
            self.s = end.Scenario()
        root = self.s.root
        spec = importlib.util.spec_from_file_location(
            "installed_execution", root / "VALIDATION/recovery_execution.py")
        installed = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installed)
        isolate_recovery(installed)
        runtime, structural = installed.runtime, installed.structural
        # Test-only fixture compatibility: use the SAME fixed disposable roots
        # already used by Checklist D. Never ship a target selector or override.
        for key in ("WORKSPACE", "MAINTENANCE", "SYNTHETIC_ROOT", "ACCEPTANCE_ROOT", "LOCK_ROOT"):
            setattr(runtime, key, getattr(end.rt, key))
        structural.SYNTHETIC_ROOT = end.sr.SYNTHETIC_ROOT
        structural.EVIDENCE_ROOT = end.sr.EVIDENCE_ROOT
        installed.EVIDENCE_ROOT = QUALIFICATION / "installed-references"
        for name, value in (("execution", installed), ("rt", runtime),
                            ("sr", structural), ("pre", installed.pre)):
            replacement = patch.object(end, name, value)
            replacement.start()
            self.addCleanup(replacement.stop)
        self.assertTrue(Path(installed.__file__).is_relative_to(root))
        self.assertTrue(Path(installed.review.__file__).is_relative_to(root))
        self.assertTrue(Path(installed.runtime.__file__).is_relative_to(root))
        self.assertEqual(self.mode, end.pre.op.state(root)["DeploymentMode"])
        end.save(self.s.base / "installed-module-provenance.json", {
            "mode": self.mode, "execution": installed.__file__,
            "review": installed.review.__file__, "runtime": runtime.__file__,
            "operator": runtime.op.__file__, "test_boundary_override": True,
            "production_allowlist_changed": False})

    def test_E01_additional_negative_matrix(self):
        self.prepared()
        s = self.s
        original = deepcopy((s.plan2, s.auth2, s.context2))
        cases = []
        for role in ("Human Director", "Human Framework Maintainer"):
            plan, auth, context = deepcopy(original)
            auth["human_authorization"]["approvals"] = [
                a for a in auth["human_authorization"]["approvals"] if a["role"] != role]
            cases.append(("missing-" + role, plan, auth, context))
        for name, mutate in (
            ("plan", lambda p: p["proposed"].update(plan_sha256="0" * 64)),
            ("source", lambda p: p["request"]["inputs"][0].update(sha256="0" * 64)),
            ("scope", lambda p: p["request"]["writes"][0].update(path="00_FRAMEWORK/GOVERNANCE_RULES.md")),
            ("activate-context", lambda p: p["packet"]["completion"].update(ordinary_context="VALID")),
            ("resolve-blocker", lambda p: p["packet"]["writes"].append(
                {"path": end.pre.BLOCKERS, "operation": "set_fields", "fields": ["Status"], "after": {"Status": "RESOLVED"}})),
            ("framework-root", lambda p: p["request"]["target"].update(root=str(FRAMEWORK))),
        ):
            plan, auth, context = deepcopy(original)
            mutate(plan)
            cases.append((name, plan, auth, context))
        plan, auth, context = deepcopy(original)
        auth["human_authorization"]["withdrawn"] = True
        cases.append(("withdrawn", plan, auth, context))
        plan, auth, context = deepcopy(original)
        auth["human_authorization"]["binding"]["ids"]["review"]["review_sha256"] = "0" * 64
        cases.append(("fingerprint", plan, auth, context))
        plan, auth, context = deepcopy(original)
        auth["human_authorization"]["binding"]["target"]["root"] = str(s.root.parent / "other-instance")
        cases.append(("cross-instance-authorization", plan, auth, context))
        plan, auth, context = deepcopy(original)
        plan["packet"]["writes"][3]["after"]["row"]["final"] = "ACTIVE"
        cases.append(("invalid-context-transition", plan, auth, context))
        plan, auth, context = deepcopy(original)
        plan["packet"]["authorization"] = deepcopy(auth)
        cases.append(("packet-self-authorization", plan, {}, context))
        for label, plan, auth, context in cases:
            with self.subTest(mode=self.mode, case=label):
                result = self.refused(plan, auth, context)
                end.save(s.base / ("negative-" + label.replace(" ", "-") + ".json"), result)
        # Changed bytes/contracts and missing adoption must also fail when passed
        # directly to the installed preflight, without relying on review binding.
        for name, ref, changed in (
            ("canonical-bytes", s.f.source, b"Unexpected source mutation\n"),
            ("contract", end.pre.GOVERNANCE, b"Mismatched governance\n"),
        ):
            path = s.root / ref
            before = path.read_bytes()
            path.write_bytes(changed)
            try:
                packet = deepcopy(s.plan2["packet"])
                result = end.pre.validate(s.root, Path(s.plan2["evidence_root"]), packet)
                self.assertNotEqual("VALID_SYNTHETIC_PREFLIGHT", result["status"])
                self.refused()
                end.save(s.base / ("negative-" + name + ".json"), result)
            finally:
                path.write_bytes(before)
        packet = deepcopy(s.plan2["packet"])
        del packet["evidence"]["adoption"]
        before = end.rt._snapshot(s.root)
        result = end.pre.validate(s.root, Path(s.plan2["evidence_root"]), packet)
        self.assertNotEqual("VALID_SYNTHETIC_PREFLIGHT", result["status"])
        self.assertEqual(before, end.rt._snapshot(s.root))
        end.save(s.base / "negative-adoption-bypass.json", result)

    def test_E02_installed_ordinary_dispatch(self):
        # Reuse the existing fully bound ordinary dispatch fixture, independently
        # of recovery approvals, then install via the official distributor.
        import test_release
        fixture = test_release.legacy.ToolkitTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.values["DeploymentMode"] = self.mode
        fixture.write_state()
        # enrich_dispatch already invokes the official distributor for this
        # canonical-derived fixture. Existing targets must never be overwritten.
        distribution.distribute(FRAMEWORK, fixture.instance, verify=True)
        before = {p.relative_to(fixture.instance).as_posix(): p.read_bytes()
                  for p in fixture.instance.rglob("*") if p.is_file()}
        command = [sys.executable, "-E", "-B", str(fixture.instance / "TOOLS/adapt.py"),
                   "prompt", "next", "--instance", str(fixture.instance), "--json"]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual("Run atomic handoff dispatch", data["invocation"]["command"])
        self.assertEqual("BACKEND_TEST", data["invocation"]["workcell"])
        self.assertFalse(data["execution_authorized"])
        self.assertEqual(before, {p.relative_to(fixture.instance).as_posix(): p.read_bytes()
                                 for p in fixture.instance.rglob("*") if p.is_file()})
        end.save(self.s.base / "ordinary-dispatch.json", {"command": command, "output": data})


class ModeAAcceptance(InstalledAcceptance, end.EndToEndTests):
    mode = "MODE_A_EXISTING_SOLUTION"


class ModeBAcceptance(InstalledAcceptance, end.EndToEndTests):
    mode = "MODE_B_REQUIREMENTS_ONLY"


if __name__ == "__main__":
    unittest.main()
