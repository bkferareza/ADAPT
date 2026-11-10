"""Synthetic isolated assembly/partial-journal checks; never real authority."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fixtures import FRAMEWORK, QUALIFICATION, framework_version
import test_recovery_preflight as existing

spec = importlib.util.spec_from_file_location("assembly", FRAMEWORK / "VALIDATION/recovery_assembly.py")
assembly = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assembly)
pre = assembly.pre


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        # Reuse fixture setup/helpers, without inheriting and repeating its tests.
        self.fixture = existing.PreflightTests("test_valid_synthetic_purpose_b")
        temporary_root = QUALIFICATION / "fw0006-assembly-staging/tmp"
        temporary_root.mkdir(parents=True, exist_ok=True)
        self.temp_patch = patch.object(tempfile, "tempdir", str(temporary_root))
        self.temp_patch.start()
        self.addCleanup(self.temp_patch.stop)
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root, self.external, self.packet = self.fixture.root, self.fixture.external, self.fixture.packet
        self.bind()

    def bind(self, selected=None, budget=pre.op.MAX_BYTES):
        f = self.fixture
        f.refresh_inputs()
        # Budget policy is an extra current input, hash checked by preflight.
        f.packet["inputs"].append({"path": assembly.BUDGET,
            "sha256": pre.digest((self.root / assembly.BUDGET).read_bytes()),
            "class": "CURRENT_CANONICAL", "reason": "Recovery size/gate classification",
            "verified_at": "2026-10-18T06:00:00+00:00"})
        f.packet["inputs"].sort(key=lambda r: r["path"])
        f.plan()
        f.evidence("assembly", {"format": "synthetic-v1", "synthetic": True, "target": f.packet["target"],
            "purpose": pre.PURPOSE, "lane": assembly.LANE, "size": "XL", "max_bytes": budget,
            "size_reason": "Synthetic approved XL cross-lane recovery audit; byte ceiling is additional task budget.",
            "selected": selected if selected is not None else sorted(pre.REQUIRED | {f.source, assembly.BUDGET})})
        values = pre.op.state(self.root)
        auth_path = str(self.external / "authorization.json")
        # Authorization hash depends on trace after-values. Do not embed that hash
        # into its own authorized content: bind path only for trace notes.
        notes = "RECOVERY ONLY; NO ORDINARY EXECUTION AUTHORITY; " + f.packet["task"] + "; " + auth_path
        trace = f.packet["writes"][-1]
        trace["after"]["LastAction"] = "Recovery assembly " + f.packet["ids"]["CP"]
        trace["after"]["Notes"] = values["Notes"] + "\n" + notes
        self.authorize()

    def authorize(self):
        self.fixture.authorize()
        for name in ("maintainer", "director", "authorization"):
            record = copy.deepcopy(self.fixture.records[name])
            record["assembly"] = self.packet["evidence"]["assembly"]
            self.fixture.evidence(name, record)

    def stage(self):
        return assembly.stage(self.root, self.external, self.packet)

    def valid(self):
        plan = self.stage()
        self.assertEqual("STAGED", plan["status"], plan)
        self.assertEqual("NOT_APPLIED", plan["application"])
        self.assertFalse(plan["operational_authority"])
        self.assertFalse(plan["ids_reserved"])
        return plan

    def refused(self):
        result = self.stage()
        self.assertEqual("REFUSED", result["status"], result)
        self.assertEqual([], result["write_set"])
        return result

    def test_valid_exact_deterministic_plan_and_cross_references(self):
        plan = self.valid()
        self.assertEqual(plan, self.stage())
        self.assertTrue(assembly.validate_plan(self.root, self.external, self.packet, plan)["valid"])
        self.assertEqual(6, len(plan["write_set"]))
        self.assertEqual(7, len(plan["operations"]))
        self.assertEqual("STOP", plan["return"]["final_action"])
        for w in plan["write_set"]:
            self.assertEqual(w["proposed_final_sha256"], pre.digest(bytes.fromhex(w["after_image_hex"])))
            self.assertEqual(str(self.root / w["path"]), w["canonical_target"])
        index = self.output(plan, pre.INDEX)
        self.assertEqual("ARCHIVED", pre.op.table(index, "Index", ["Status"])[-1]["Status"])
        self.assertIn("STALE", bytes.fromhex(plan["operations"][1]["after_image_hex"]).decode())
        pack = self.output(plan, "10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-001.md")
        for heading in assembly.SECTIONS["CP"] + ("Recovery Basis",):
            self.assertIn("## " + heading, pack)
        self.assertIn("HANDOFF_ID: NONE", pack)
        self.assertIn("STATUS: DRAFT", pack)
        self.assertIn(pre.digest((self.root / self.fixture.source).read_bytes()), pack)
        self.assertIn("PRECEDING_CONTEXT_PACK_ID: CP-001", self.output(plan, "10_CONTEXT_ECONOMY/CONTEXT_DELTAS/CD-001.md"))
        handoff = self.output(plan, "06_HANDOFFS/ACTIVE/HO-001.md")
        self.assertIn("TO_WORKCELL / TO_LANE: Director Lane", handoff)
        self.assertIn("CONTEXT_DELTA_ID: CD-001", handoff)

    def test_primary_ids_exclude_embedded_snapshot_and_cross_artifact_references(self):
        for ref, body in (
            ('10_CONTEXT_ECONOMY/CONTEXT_PACKS/historical.md',
             '# Pack\nCONTEXT_PACK_ID: CP-003\nHANDOFF_ID: HO-004\n\n## History\nCONTEXT_PACK_ID: CP-001\nCONTEXT_DELTA_ID: CD-001\n'),
            ('06_HANDOFFS/CONSUMED/historical.md',
             '# Handoff\nHANDOFF_ID: HO-004\n\n## Context Delta Reference\nCONTEXT_DELTA_ID: CD-001\n'),
            ('10_CONTEXT_ECONOMY/CONTEXT_DELTAS/CD-001.md',
             '# Delta\nCONTEXT_DELTA_ID: CD-001\n')):
            (self.root/ref).write_text(body,encoding='utf-8')
        self.fixture.refresh_inputs()
        ids=assembly.allocate_ids(self.root,self.external,self.packet)
        self.assertEqual({'CP':'CP-004','HO':'HO-005','CD':'CD-002','SC':'SC-001'},ids)

    def test_legacy_crlf_primary_duplicates_refuse(self):
        body=b'# Historical handoff\r\nHANDOFF_ID: HO-009\r\n\r\n## Context Delta Reference\r\nCONTEXT_DELTA_ID: CD-008\r\n'
        self.assertEqual(['HO-009'],pre.declared_ids('06_HANDOFFS/CONSUMED/legacy.md',body.decode()))
        for name in ('first.md','second.md'):
            (self.root/'06_HANDOFFS/CONSUMED'/name).write_bytes(body)
        with self.assertRaises(pre.Refusal):
            assembly.allocate_ids(self.root,self.external,self.packet)

    def test_primary_metadata_conflicts_and_invalid_kinds_refuse(self):
        for body in ('CONTEXT_PACK_ID: CP-001\nCONTEXT_PACK_ID: CP-002\n',
                     'CONTEXT_PACK_ID: HO-001\r\n', 'CONTEXT_PACK_ID: NONE\n'):
            with self.subTest(body=body), self.assertRaises(pre.Refusal):
                pre.declared_ids('10_CONTEXT_ECONOMY/CONTEXT_PACKS/legacy.md',body)

    @staticmethod
    def output(plan, path):
        return bytes.fromhex(next(w for w in plan["write_set"] if w["path"] == path)["after_image_hex"]).decode("utf-8-sig")

    def test_missing_invalid_or_unbound_authorization(self):
        for name in ("maintainer", "director", "authorization"):
            with self.subTest(name=name):
                saved = self.packet["evidence"].pop(name)
                self.refused()
                self.packet["evidence"][name] = saved
        record = copy.deepcopy(self.fixture.records["authorization"])
        record["assembly"] = {"path": "wrong", "sha256": "0" * 64}
        self.fixture.evidence("authorization", record)
        self.refused()

    def test_changed_source_hash_and_before_images(self):
        self.fixture.change(self.fixture.source, lambda s: s + "changed")
        self.refused()
        self.bind()
        self.packet["writes"][-1]["before"]["LastAction"] = "wrong"
        self.authorize()
        self.refused()

    def test_unauthorized_paths_fields_and_operations(self):
        original = copy.deepcopy(self.packet)
        for field, value in (("path", "../outside"), ("path", pre.BLOCKERS),
                             ("path", "01_SOURCE_TRUTH/SYNTHETIC.md"),
                             ("path", pre.GOVERNANCE), ("fields", ["ActiveHandoff"]),
                             ("fields", ["Blocked"]), ("operation", "unrestricted_write")):
            with self.subTest(field=field, value=value):
                self.fixture.packet = self.packet = copy.deepcopy(original)
                self.packet["writes"][-1][field] = value
                self.authorize()
                self.refused()

    def test_id_allocation_issued_archive_consumed_and_partial_names(self):
        self.assertEqual(self.packet["ids"], assembly.allocate_ids(self.root, self.external, self.packet))
        for ref, body in (("06_HANDOFFS/CONSUMED/HO-009.md", "HANDOFF_ID: HO-009\n"),
                          ("10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-004.partial", "interrupted CP-004 CD-007 SC-003\n")):
            (self.root / ref).write_text(body, encoding="utf-8")
        allocated = assembly.allocate_ids(self.root, self.external, self.packet)
        self.assertEqual({"CP": "CP-005", "CD": "CD-008", "SC": "SC-004", "HO": "HO-010"}, allocated)
        self.fixture.packet["ids"] = allocated
        self.bind()
        self.valid()

    def test_history_collision_duplicate_definitions_and_aliases(self):
        (self.root / "06_HANDOFFS/ARCHIVE/HO-001.md").write_text("HANDOFF_ID: HO-001\n", encoding="utf-8")
        self.bind()
        self.refused()
        (self.root / "06_HANDOFFS/CONSUMED/HO-001.md").write_text("HANDOFF_ID: HO-001\n", encoding="utf-8")
        with self.assertRaises(pre.Refusal):
            assembly.allocate_ids(self.root, self.external, self.packet)
        self.refused()

    def test_bound_external_interrupted_ids_never_reused(self):
        self.fixture.evidence("id_history_interrupted", {"synthetic": True, "target": self.packet["target"],
            "purpose": pre.PURPOSE, "issued_ids": ["CP-001", "HO-005"]})
        self.assertEqual("CP-002", assembly.allocate_ids(self.root, self.external, self.packet)["CP"])
        self.assertEqual("HO-006", assembly.allocate_ids(self.root, self.external, self.packet)["HO"])
        self.authorize()
        self.refused()

    def test_invalid_pack_template_and_budget(self):
        self.fixture.change(assembly.TEMPLATES["CP"], lambda s: s.replace("## Scope Declaration", "## Broken"))
        self.bind()
        self.refused()
        self.fixture.change(assembly.TEMPLATES["CP"], lambda s: s.replace("## Broken", "## Scope Declaration"))
        self.bind(budget=128)
        self.refused()

    def test_changed_output_schema_and_cross_artifact_reference(self):
        plan = self.valid()
        for ref, before, after in (("10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-001.md", "STATUS: DRAFT", "STATUS: ACTIVE"),
                                   ("06_HANDOFFS/ACTIVE/HO-001.md", "CONTEXT_DELTA_ID: CD-001", "CONTEXT_DELTA_ID: CD-999"),
                                   (pre.INDEX, "ARCHIVED", "ACTIVE")):
            with self.subTest(ref=ref):
                changed = copy.deepcopy(plan)
                w = next(w for w in changed["write_set"] if w["path"] == ref)
                data = bytes.fromhex(w["after_image_hex"]).decode().replace(before, after)
                w["after_image_hex"] = data.encode().hex()
                w["proposed_final_sha256"] = pre.digest(data.encode())
                changed["plan_sha256"] = assembly.fingerprint({k: v for k, v in changed.items() if k != "plan_sha256"})
                self.assertFalse(assembly.validate_plan(self.root, self.external, self.packet, changed)["valid"])
        changed = copy.deepcopy(plan)
        changed["write_set"].append(copy.deepcopy(changed["write_set"][0]))
        self.assertFalse(assembly.validate_plan(self.root, self.external, self.packet, changed)["valid"])

    def test_revalidate_ids_and_inputs_before_future_write(self):
        plan = self.valid()
        (self.root / "06_HANDOFFS/ACTIVE/HO-001.md").write_text("partial", encoding="utf-8")
        self.assertFalse(assembly.validate_plan(self.root, self.external, self.packet, plan)["valid"])

    def test_recovery_only_selection(self):
        record = self.fixture.records["assembly"]
        record["selected"].remove(self.fixture.source)
        self.fixture.evidence("assembly", record)
        self.authorize()
        self.refused()

    def test_historical_pack_selection_and_ordinary_staleness_preserved(self):
        ref = "10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-008.md"
        (self.root / ref).write_text("CONTEXT_PACK_ID: CP-008\nHistorical ordinary pack; not current truth.\n", encoding="utf-8")
        self.fixture.change(pre.INDEX, lambda s: s + "\n| CP-008 | Context Steward | NONE | SOURCE_TRUTH_V1.0 | M | 2026-10-17 | STALE | Historical |\n")
        self.packet["ids"] = {"CP": "CP-009", "CD": "CD-001", "SC": "SC-001", "HO": "HO-001"}
        selected = sorted(pre.REQUIRED | {self.fixture.source, assembly.BUDGET, ref})
        self.bind(selected=selected)
        # Ordinary inventory cannot be implicitly treated as current recovery state.
        self.refused()
        next(i for i in self.packet["inputs"] if i["path"] == ref)["class"] = "HISTORICAL_RECOVERY"
        self.authorize()
        plan = self.valid()
        rows = pre.op.table(self.output(plan, pre.INDEX), "Index", ["CP-ID", "Status"])
        self.assertEqual([("CP-008", "STALE"), ("CP-009", "ARCHIVED")], [(r["CP-ID"], r["Status"]) for r in rows])

    def test_existing_journal_refuses_fresh_staging(self):
        self.valid()
        journal = self.external / self.packet["completion"]["journal"]
        journal.parent.mkdir()
        journal.write_text('{"event":"INTERRUPTED"}\n', encoding="utf-8")
        self.refused()

    def test_duplicate_external_issuance_refused(self):
        self.fixture.evidence("id_history_duplicate", {"synthetic": True, "target": self.packet["target"],
            "purpose": pre.PURPOSE, "issued_ids": ["CP-001", "CP-001"]})
        self.authorize()
        self.refused()

    def test_trace_preserves_escaped_notes_and_register_bytes(self):
        self.fixture.change(pre.op.CP, lambda s: s.replace("Synthetic fixture, no execution authority",
                                                              r"Synthetic fixture \| no execution authority"))
        self.bind()
        plan = self.valid()
        self.assertIn(r"Synthetic fixture \| no execution authority<br>RECOVERY ONLY", self.output(plan, pre.op.CP))
        for ref in (pre.INDEX, pre.STALE):
            w = next(w for w in plan["write_set"] if w["path"] == ref)
            self.assertTrue(bytes.fromhex(w["after_image_hex"]).startswith(bytes.fromhex(w["before_image_hex"])))

    def test_no_blocker_closure_retry_reset_or_ordinary_execution(self):
        plan = self.valid()
        before = pre.op.state(self.root)
        plane = self.output(plan, pre.op.CP)
        for field in ("Blocked", "ActiveBlockers", "ActiveGaps", "ActiveHandoff", "CurrentAuthority",
                      "ExecutionReadiness", "NextExpectedAction"):
            self.assertIn("| " + field + " | " + before[field] + " |", plane)
        self.assertEqual("OPEN", pre.op.table(self.output(plan, pre.STALE), "Register", ["Status"])[-1]["Status"])
        self.assertNotIn(pre.BLOCKERS, [w["path"] for w in plan["write_set"]])
        self.packet["completion"]["preserve_blockers_and_attempts"] = False
        self.authorize()
        self.refused()

    def test_fw0005_capability_rejected(self):
        self.fixture.change(pre.GOVERNANCE, lambda s: s.replace("VERSION: " + framework_version(), "VERSION: ADAPT-FW-0005"))
        result = self.refused()
        self.assertEqual("UNSUPPORTED_CAPABILITY", result["preflight"]["status"])

    def test_zero_writes_on_success_and_refusal(self):
        def snapshot():
            return {str(p): pre.digest(p.read_bytes()) for p in self.fixture.base.rglob("*") if p.is_file()}
        before = snapshot()
        self.valid()
        self.assertEqual(before, snapshot())
        self.packet["purpose"] = "INVALID"
        before = snapshot()
        self.refused()
        self.assertEqual(before, snapshot())

    def test_preflight_is_first(self):
        with patch.object(assembly.pre, "validate", return_value={"status": "INVALID_PREFLIGHT"}) as validate:
            with patch.object(assembly, "_build", side_effect=AssertionError("must not assemble")):
                self.refused()
                validate.assert_called_once()

    def test_journal_all_interruption_points_and_partial_state(self):
        plan = self.valid()
        observed = {i["path"]: i["sha256"] for i in plan["input_manifest"]}
        observed.update({w["path"]: w["expected_original_sha256"] for w in plan["write_set"]})
        records, previous = [], plan["plan_sha256"]
        self.assertEqual("PRISTINE_FIXTURE", assembly.inspect_journal(plan, records, observed)["status"])
        for i, operation in enumerate(plan["operations"]):
            # A write without its completion record must be exposed, never hidden.
            partial = dict(observed, **{operation["path"]: operation["after_sha256"]})
            self.assertEqual("REFUSED", assembly.inspect_journal(plan, records, partial)["status"])
            body = {"plan_sha256": plan["plan_sha256"], "previous_sha256": previous,
                    "sequence": i + 1, "path": operation["path"], "before_sha256": operation["before_sha256"],
                    "after_sha256": operation["after_sha256"], "event": "WRITE_COMPLETED"}
            record = {**body, "record_sha256": assembly.fingerprint(body)}
            records.append(record)
            previous = record["record_sha256"]
            observed = partial
            result = assembly.inspect_journal(plan, records, observed)
            self.assertEqual("INTERRUPTED" if i < 6 else "REPRESENTED_COMPLETE", result["status"])
            self.assertFalse(result["automatic_resume"])
            self.assertEqual("PRESERVE_AND_STOP_REAUTHORIZE", result["action"])
        self.assertEqual("REFUSED", assembly.inspect_journal(plan, records[::-1], observed)["status"])
        self.assertEqual("REFUSED", assembly.inspect_journal(plan, records[:-1], observed)["status"])
        changed = dict(observed, **{self.fixture.source: "0" * 64})
        self.assertEqual("REFUSED", assembly.inspect_journal(plan, records, changed)["status"])


if __name__ == "__main__":
    unittest.main()
