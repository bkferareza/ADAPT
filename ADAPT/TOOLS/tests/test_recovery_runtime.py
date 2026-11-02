"""Genuine filesystem execution under the fixed maintenance synthetic boundary."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fixtures import FRAMEWORK, runtime_child_setup
import test_recovery_assembly as existing

spec = importlib.util.spec_from_file_location("runtime", FRAMEWORK / "VALIDATION/recovery_runtime.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
pre, assembly = runtime.pre, runtime.assembly


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        runtime.SYNTHETIC_ROOT.mkdir(parents=True, exist_ok=True)
        self.temp_patch = patch.object(tempfile, "tempdir", str(runtime.SYNTHETIC_ROOT))
        self.temp_patch.start()
        self.addCleanup(self.temp_patch.stop)
        self.f = existing.AssemblyTests("test_valid_exact_deterministic_plan_and_cross_references")
        # AssemblyTests chooses its own maintenance temp root. Replace just that
        # setting, preserving the original fixture builder and authority records.
        with patch.object(existing.tempfile, "TemporaryDirectory",
                          side_effect=lambda: self.original_temp(dir=runtime.SYNTHETIC_ROOT)):
            self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.root, self.external, self.packet = self.f.root, self.f.external, self.f.packet
        self.plan = self.f.valid()
        self.before = runtime._snapshot(self.root)
        self.evidence_before = runtime._snapshot(self.external)
        self.addCleanup(self.clean_lock)

    original_temp = staticmethod(tempfile.TemporaryDirectory)

    def clean_lock(self):
        # Test harness only: production API never deletes interrupted ownership.
        path = runtime.lock_path(self.root)
        if path.exists():
            path.unlink()

    def run_plan(self, **kwargs):
        args = dict(instance=self.root, evidence_root=self.external, packet=self.packet, plan=self.plan)
        args.update(kwargs)
        return runtime.execute(**args)

    def journal(self):
        return self.external / self.plan["journal"]["path"]

    def success(self):
        result = self.run_plan()
        self.assertEqual("SYNTHETIC_EXECUTION_VALIDATED", result["status"], result)
        self.assertEqual("UNAUTHORIZED", result["real_execution"])
        self.assertFalse(result["operational_authority"])
        return result

    def refusal(self, **kwargs):
        result = self.run_plan(**kwargs)
        self.assertEqual("REFUSED", result["status"], result)
        self.assertEqual(self.before, runtime._snapshot(self.root))
        return result

    def test_RT01_valid_plan_exact_mutation_inventory(self):
        self.success()
        after = runtime._snapshot(self.root)
        changes = {p for p in after if after[p] != self.before.get(p)}
        self.assertEqual({w["path"] for w in self.plan["write_set"]}, changes)
        self.assertFalse(runtime.lock_path(self.root).exists())

    def test_RT02_invalid_authority_before_write(self):
        del self.packet["evidence"]["authorization"]
        self.refusal()
        self.assertFalse(self.journal().exists())

    def test_RT03_wrong_target_traversal_and_boundary(self):
        self.refusal(instance=FRAMEWORK)
        self.refusal(instance=self.root / ".." / "instance")
        self.packet["target"]["identity"] = "Wrong"
        self.refusal()

    def test_RT04_source_before_image_and_write_time_change(self):
        ref = self.f.fixture.source
        path = self.root / ref
        data = path.read_bytes()
        path.write_bytes(data + b"changed")
        self.assertEqual("REFUSED", self.run_plan()["status"])
        path.write_bytes(data)
        def change(event, seq):
            if event == "after_intent" and seq == 1:
                path.write_bytes(data + b"changed at write time")
        with patch.object(runtime, "_checkpoint", side_effect=change):
            self.assertEqual("INTERRUPTED", self.run_plan()["status"])
        self.assertFalse((self.root / self.plan["operations"][0]["path"]).exists())

    def test_RT05_unauthorized_operations_paths_and_fields(self):
        for key, value in (("path", pre.BLOCKERS), ("operation", "delete"), ("fields", ["Blocked"])):
            packet = copy.deepcopy(self.packet)
            packet["writes"][-1][key] = value
            self.refusal(packet=packet)
        plan = copy.deepcopy(self.plan)
        plan["operations"][0]["path"] = "../escape"
        plan["plan_sha256"] = assembly.fingerprint({k: v for k, v in plan.items() if k != "plan_sha256"})
        self.refusal(plan=plan)

    def test_RT06_actual_second_process_writer_refused(self):
        payload = self.external / "child.json"
        payload.write_text(json.dumps({"packet": self.packet, "plan": self.plan}), encoding="utf-8")
        def second(event, seq):
            if event == "after_intent" and seq == 1:
                script = (
                    "import importlib.util,json,pathlib;"
                    f"s=importlib.util.spec_from_file_location('r',{str(FRAMEWORK / 'VALIDATION/recovery_runtime.py')!r});"
                    "r=importlib.util.module_from_spec(s);s.loader.exec_module(r);"
                    + runtime_child_setup(runtime) +
                    f"d=json.loads(pathlib.Path({str(payload)!r}).read_text());"
                    f"print(json.dumps(r.execute({str(self.root)!r},{str(self.external)!r},d['packet'],d['plan'])))")
                child = subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, text=True, timeout=30)
                self.assertEqual(0, child.returncode, child.stderr)
                result = json.loads(child.stdout)
                self.assertEqual("REFUSED", result["status"], result)
                self.assertIn("Existing ownership", result["error"], result)
        with patch.object(runtime, "_checkpoint", side_effect=second):
            self.success()

    def test_RT07_interrupted_ownership_never_stolen(self):
        path = runtime.lock_path(self.root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'{"pid":-1,"interrupted":true}')
        before = path.read_bytes()
        self.refusal()
        self.assertEqual(before, path.read_bytes())

    def test_RT08_journal_filesystem_and_external_evidence_agree(self):
        self.success()
        result = runtime.audit(self.root, self.journal(), self.plan)
        self.assertTrue(result["filesystem_agreement"], result)
        self.assertEqual(7, result["completed_operations"])
        records = [json.loads(line) for line in self.journal().read_text().splitlines()]
        self.assertEqual(16, len(records))
        self.assertEqual("FINAL_VALIDATED", records[-1]["event"])

    def test_RT09_every_operation_boundary_interruption(self):
        # Separate isolated fixture per crash; real partial files and journals.
        for event in ("before_intent", "after_intent", "after_mutation", "after_completion"):
            for seq in range(1, 8):
                with self.subTest(event=event, sequence=seq):
                    fixture = RuntimeTests("test_RT01_valid_plan_exact_mutation_inventory")
                    fixture.setUp()
                    try:
                        def crash(at, number):
                            if (at, number) == (event, seq):
                                raise RuntimeError("original synthetic failure")
                        with patch.object(runtime, "_checkpoint", side_effect=crash):
                            result = fixture.run_plan()
                        self.assertEqual("INTERRUPTED", result["status"], result)
                        self.assertEqual("original synthetic failure", result["error"])
                        checked = runtime.audit(fixture.root, fixture.journal(), fixture.plan)
                        self.assertEqual("INTERRUPTED", checked["status"], checked)
                        self.assertEqual(event != "after_mutation", checked["filesystem_agreement"])
                        self.assertTrue(runtime.lock_path(fixture.root).exists())
                        before = runtime._snapshot(fixture.root)
                        self.assertEqual("REFUSED", fixture.run_plan()["status"])
                        self.assertEqual(before, runtime._snapshot(fixture.root))
                        self.assertIn("original synthetic failure", fixture.journal().read_text())
                    finally:
                        fixture.doCleanups()

    def test_RT10_abrupt_process_death_and_no_resume(self):
        payload = self.external / "child.json"
        payload.write_text(json.dumps({"packet": self.packet, "plan": self.plan}), encoding="utf-8")
        script = (
            "import importlib.util,json,pathlib,os;"
            f"s=importlib.util.spec_from_file_location('r',{str(FRAMEWORK / 'VALIDATION/recovery_runtime.py')!r});"
            "r=importlib.util.module_from_spec(s);s.loader.exec_module(r);"
            + runtime_child_setup(runtime) +
            f"d=json.loads(pathlib.Path({str(payload)!r}).read_text());"
            "r._checkpoint=lambda event,seq: os._exit(73) if (event,seq)==('after_mutation',3) else None;"
            f"r.execute({str(self.root)!r},{str(self.external)!r},d['packet'],d['plan'])")
        child = subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, timeout=30)
        self.assertEqual(73, child.returncode)
        checked = runtime.audit(self.root, self.journal(), self.plan)
        self.assertEqual("INTERRUPTED", checked["status"], checked)
        self.assertFalse(checked["filesystem_agreement"])
        before = runtime._snapshot(self.root)
        self.assertEqual("REFUSED", self.run_plan()["status"])
        self.assertEqual(before, runtime._snapshot(self.root))

    def test_RT11_tampered_truncated_or_reordered_journal(self):
        self.success()
        data = self.journal().read_bytes()
        lines = data.splitlines(keepends=True)
        for altered in (data[:-4], data.replace(b'WRITE_COMPLETED', b'WRITE_TAMPERED', 1),
                        b"".join([lines[0], lines[2], lines[1], *lines[3:]])):
            self.journal().write_bytes(altered)
            self.assertEqual("INVALID_JOURNAL", runtime.audit(self.root, self.journal(), self.plan)["status"])
        self.journal().write_bytes(data)
        (self.root / self.plan["operations"][0]["path"]).write_bytes(b"changed")
        self.assertEqual("INVALID_JOURNAL", runtime.audit(self.root, self.journal(), self.plan)["status"])

    def test_RT12_id_collision_and_prior_execution_reuse(self):
        path = self.root / self.plan["operations"][0]["path"]
        path.write_bytes(b"previously issued CP-001")
        self.assertEqual("REFUSED", self.run_plan()["status"])
        path.unlink()
        self.success()
        self.assertEqual("REFUSED", self.run_plan()["status"])
        self.assertTrue(self.journal().exists())

    def test_RT13_final_schema_references_and_output_tampering(self):
        result = self.success()
        self.assertEqual("PASS", result["validation"]["schemas_and_references"])
        manifest = self.external / self.plan["return"]["manifest"]
        manifest.write_bytes(manifest.read_bytes() + b" ")
        self.assertEqual("INVALID_JOURNAL", runtime.audit(self.root, self.journal(), self.plan)["status"])

    def test_RT14_blocker_remains_open(self):
        before = (self.root / pre.BLOCKERS).read_bytes()
        self.success()
        self.assertEqual(before, (self.root / pre.BLOCKERS).read_bytes())
        self.assertEqual("YES", pre.op.state(self.root)["Blocked"])
        self.assertIn("OPEN", before.decode())

    def test_RT15_retry_evidence_unrelated_handoff_preserved(self):
        path = self.root / "06_HANDOFFS/ARCHIVE/HO-000.md"
        path.write_text("HANDOFF_ID: HO-000\nHistorical unrelated handoff", encoding="utf-8")
        self.f.bind()
        self.plan = self.f.valid()
        before = path.read_bytes()
        evidence = runtime._snapshot(self.external)
        self.success()
        self.assertEqual(before, path.read_bytes())
        after = runtime._snapshot(self.external)
        self.assertTrue(all(after[p] == h for p, h in evidence.items()))

    def test_RT16_no_ordinary_context_activation(self):
        state = pre.op.state(self.root)
        self.success()
        final = pre.op.state(self.root)
        for key in state:
            if key not in {"LastContextDelta", "LastAction", "Notes"}:
                self.assertEqual(state[key], final[key], key)
        self.assertIn("ARCHIVED", (self.root / pre.INDEX).read_text())

    def test_RT17_protected_instance_rejected_before_read(self):
        target = FRAMEWORK.parent / "ADAPT-DEV/ADAPT"
        with patch.object(runtime.assembly, "validate_plan", side_effect=AssertionError("must not inspect")):
            self.refusal(instance=target)

    def test_RT18_existing_component_reuse(self):
        with patch.object(runtime.assembly, "validate_plan", wraps=runtime.assembly.validate_plan) as validate, \
             patch.object(runtime.assembly, "allocate_ids", wraps=runtime.assembly.allocate_ids) as allocate, \
             patch.object(runtime.assembly, "inspect_journal", wraps=runtime.assembly.inspect_journal) as inspect:
            self.success()
            self.assertGreaterEqual(validate.call_count, 2)
            self.assertGreaterEqual(allocate.call_count, 1)
            self.assertGreaterEqual(inspect.call_count, 2)

    def test_hard_link_alias_rejected(self):
        path = self.root / self.f.fixture.source
        alias = self.external / "hardlink"
        os.link(path, alias)
        self.assertEqual("REFUSED", self.run_plan()["status"])

    def test_symlink_target_rejected(self):
        link = self.root.parent / "linked"
        try:
            link.symlink_to(self.root, target_is_directory=True)
        except OSError as error:
            self.skipTest("OS disallows creating symlinks: " + str(error))
        self.addCleanup(link.unlink)
        self.refusal(instance=link)

    def test_conflicting_unbound_file_at_write_time(self):
        def conflict(event, seq):
            if event == "after_intent" and seq == 2:
                (self.root / "undeclared.txt").write_bytes(b"conflicting mutation")
        with patch.object(runtime, "_checkpoint", side_effect=conflict):
            self.assertEqual("INTERRUPTED", self.run_plan()["status"])
        self.assertEqual("INTERRUPTED", runtime.audit(self.root, self.journal(), self.plan)["status"])

    def test_changed_authority_after_intent_refuses_mutation(self):
        path = self.external / self.packet["evidence"]["authorization"]["path"]
        def conflict(event, seq):
            if (event, seq) == ("after_intent", 1):
                path.write_bytes(path.read_bytes() + b" ")
        with patch.object(runtime, "_checkpoint", side_effect=conflict):
            result = self.run_plan()
        self.assertEqual("INTERRUPTED", result["status"], result)
        self.assertEqual(self.before, runtime._snapshot(self.root))
        self.assertTrue(runtime.lock_path(self.root).exists())

    def test_changed_journal_after_intent_refuses_mutation(self):
        def conflict(event, seq):
            if (event, seq) == ("after_intent", 1):
                with self.journal().open("ab") as stream:
                    stream.write(b"tampered\n")
        with patch.object(runtime, "_checkpoint", side_effect=conflict):
            result = self.run_plan()
        self.assertEqual("INTERRUPTED", result["status"], result)
        self.assertEqual(self.before, runtime._snapshot(self.root))
        self.assertIn("journal_error", result)
        self.assertIn(b"tampered", self.journal().read_bytes())

    @unittest.skipUnless(os.name == "nt", "Windows junction check")
    def test_windows_junction_escape_rejected(self):
        link = self.root.parent / "junction"
        created = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(FRAMEWORK)],
                                 capture_output=True, text=True, timeout=15)
        self.assertEqual(0, created.returncode, created.stdout + created.stderr)
        self.addCleanup(os.rmdir, link)
        self.refusal(instance=link)


if __name__ == "__main__":
    unittest.main()
