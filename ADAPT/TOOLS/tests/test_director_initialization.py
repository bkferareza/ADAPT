"""Synthetic conformance and actual two-file designation transition tests.

These fixtures do not authenticate or stand in for real Human Owner approvals.
The separate stage-by-stage MODE_A acceptance is retained as execution evidence.
"""
import copy
import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest

from fixtures import FRAMEWORK

spec = importlib.util.spec_from_file_location('director_case', FRAMEWORK / 'VALIDATION/director_case.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
b = d.b


class DirectorInitializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='director-initialization-fixture-')
        cls.base = Path(cls.temp.name)
        d.scaffold(cls.base)
        cls.source = cls.base / 'acceptance/ADAPT'
        cls.basis = d.supply_designation(cls.base, cls.source)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.temp_case = tempfile.TemporaryDirectory(prefix='director-initialization-case-')
        self.addCleanup(self.temp_case.cleanup)
        self.base = Path(self.temp_case.name)
        self.root = self.base / 'ADAPT'
        shutil.copytree(self.source, self.root)
        shutil.copy2(self.__class__.base / d.DESIGNATION, self.base / d.DESIGNATION)
        self.basis = copy.deepcopy(self.__class__.basis)

    def alter_input(self, **values):
        data = d.c.data(self.base, d.DESIGNATION)
        data.update(values)
        b.write(self.base, d.DESIGNATION, json.dumps(data))
        self.basis['input_sha256'] = b.sha(self.base / d.DESIGNATION)

    def reject(self, reason, **kwargs):
        before = b.snapshot(self.root)
        with self.assertRaisesRegex(b.Stop, reason):
            d.preflight(self.base, self.root, self.basis, **kwargs)
        self.assertEqual(before, b.snapshot(self.root), 'Failed eligibility must not write')

    def test_fresh_scaffold_is_unresolved_with_no_context_workcells_or_gate1(self):
        self.assertIn('HUMAN_OWNER: {{DIRECTOR_IDENTITY}}', b.read(self.root, d.IDENTITY))
        self.assertFalse((self.root / b.APPROVAL).exists())
        self.assertEqual(b.state(self.root)['SourceTruthVersion'], 'NONE')
        self.assertEqual(d.preflight(self.base, self.root, self.basis)['human_owner'], d.DIRECTOR)

    def test_actual_registered_designation_has_exact_two_file_scope_and_trace(self):
        before = b.snapshot(self.root)
        plane = (self.root / b.CP).read_bytes()
        d.designate(self.base, self.root, self.basis)
        after = b.snapshot(self.root)
        self.assertEqual({p for p in before if before[p] != after[p]}, set(d.SCOPE))
        self.assertEqual(before.keys(), after.keys())
        self.assertEqual(plane, (self.root / b.CP).read_bytes())
        identity = b.read(self.root, d.IDENTITY)
        self.assertNotIn('{{', identity)
        for line in ['ROLE: Director', 'WORKCELL_TYPE: Director Lane', 'HUMAN_OWNER: ' + d.DIRECTOR]:
            self.assertIn(line, identity)
        decision = b.read(self.root, b.DEC)
        self.assertIn('DIRECTOR_DESIGNATION: SYNTHETIC-HUMAN-DESIGNATION-001', decision)
        self.assertIn(self.basis['input_sha256'], decision)
        self.assertIn('Codex synthetic validation executor', decision)
        self.assertEqual(d.c.data(self.base, 'designation-result.json')['next_action'], d.NEXT)
        self.assertNotIn('| SOURCE_TRUTH_V0.1 |', b.real_rows(self.root / b.LOG))

    def test_missing_human_designation(self):
        (self.base / d.DESIGNATION).unlink()
        self.reject('MISSING_DESIGNATION')

    def test_conflicting_designation_project(self):
        self.alter_input(project='Other project')
        self.reject('DESIGNATION_CONFLICT')

    def test_conflicting_existing_human_director(self):
        b.write(self.root, d.IDENTITY, b.read(self.root, d.IDENTITY).replace('{{DIRECTOR_IDENTITY}}', 'OTHER HUMAN'))
        self.reject('DIRECTOR_ALREADY_SET_OR_CONFLICT')

    def test_unresolved_designated_human(self):
        self.alter_input(human_owner='{{DIRECTOR_IDENTITY}}')
        self.reject('HUMAN_DESIGNATION')

    def test_unresolved_other_required_identity_field(self):
        b.write(self.root, d.IDENTITY, b.read(self.root, d.IDENTITY).replace('INITIALIZED: 2026-10-16', 'INITIALIZED: {{DATE}}'))
        self.reject('UNRESOLVED_IDENTITY')

    def test_incorrect_executing_authority(self):
        self.reject('EXECUTOR_AUTHORITY', executor='Backend Workcell')

    def test_control_plane_lane_mismatch(self):
        b.set_state(self.root, CurrentAuthority='Context Steward')
        self.reject('EXECUTOR_AUTHORITY')

    def test_unregistered_standalone_command(self):
        self.reject('REGISTERED_COMMAND', command='INITIALIZE_DIRECTOR_IDENTITY')

    def test_natural_language_command_is_not_exact_registered_invocation(self):
        self.reject('REGISTERED_COMMAND', command='please initialize the Director')

    def test_product_mutation_not_in_designation_scope(self):
        self.reject('MUTATION_BOUNDARY', planned=[*d.SCOPE, '../project/src/greeting.py'])

    def test_control_plane_or_intake_write_not_in_designation_scope(self):
        self.reject('MUTATION_BOUNDARY', planned=[*d.SCOPE, b.CP, b.INTAKE])

    def test_designation_does_not_grant_gate1(self):
        d.designate(self.base, self.root, self.basis)
        basis = b.inputs(self.root, populate_director=False)
        approval = d.c.data(self.root, b.APPROVAL)
        approval['approved'] = False
        b.write(self.root, b.APPROVAL, json.dumps(approval))
        basis['approval_sha256'] = b.sha(self.root / b.APPROVAL)
        before = b.snapshot(self.root)
        with self.assertRaisesRegex(b.Stop, 'GATE_1'):
            b.promote(self.base, self.root, basis)
        self.assertEqual(before, b.snapshot(self.root))

    def test_ordinary_implementation_requires_workcell_and_context(self):
        d.designate(self.base, self.root, self.basis)
        with self.assertRaisesRegex(b.Stop, 'IMPLEMENTATION_UNASSIGNED'):
            d.c.implementation(self.root, d.c.target(1))
        with self.assertRaisesRegex(b.Stop, 'ORDINARY_CONTEXT_MISSING'):
            b.ordinary(self.root, None)

    def test_reassignment_not_authorized_by_initial_stage(self):
        d.designate(self.base, self.root, self.basis)
        self.alter_input(human_owner='OTHER HUMAN')
        self.reject('DESIGNATION_HISTORY')

    def test_same_owner_repeat_cannot_reuse_qualification(self):
        d.designate(self.base, self.root, self.basis)
        self.reject('DESIGNATION_HISTORY')

    def test_qualification_cannot_authorize_adjacent_intake(self):
        self.basis['action'] = 'general Director intake'
        self.reject('QUALIFICATION_SCOPE')

    def test_qualification_after_initialization_phase_is_blocked(self):
        b.set_state(self.root, CurrentPhase='SOURCE_TRUTH_READY')
        self.reject('INITIAL_STATE')

    def test_driver_assertion_is_not_original_human_designation(self):
        self.alter_input(origin='DRIVER_ASSERTION')
        self.reject('HUMAN_INPUT_REQUIRED')

    def test_changed_original_designation_bytes(self):
        b.append(self.base, d.DESIGNATION, '\n')
        self.reject('DESIGNATION_HASH')

    def test_changed_contract_binding(self):
        b.append(self.root, '15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_DIRECTOR.md', '\nchanged\n')
        self.reject('CONTRACT_BINDING')

    def test_prior_designation_in_archive_blocks_reset_reuse(self):
        b.write(self.root, '06_HANDOFFS/ARCHIVE/prior.md', 'DIRECTOR_DESIGNATION: historical attempt\n')
        self.reject('DESIGNATION_HISTORY')

    def test_prior_promotion_history_blocks_initial_setup(self):
        b.append(self.root, b.LOG, '\n| SOURCE_TRUTH_V0.1 | old.txt | ACTIVE |\n')
        self.reject('PROMOTION_HISTORY')

    def test_actual_active_artifacts_override_none_control_fields(self):
        b.write(self.root, '06_HANDOFFS/ACTIVE/HO-9999.md', 'STATUS: ACTIVE\n')
        self.reject('ACTIVE_ARTIFACT')

    def test_incomplete_scaffold_is_not_repaired_through_designation(self):
        (self.root / 'STARTUP.md').unlink()
        self.reject('SCAFFOLD_INCOMPLETE')

    def test_no_new_command_schema_field_gate_or_tool_is_introduced(self):
        self.assertEqual(len(re.findall(r'^\| \d+ \|', b.read(self.root, '15_COMMANDS_AND_DRIVERS/COMMAND_REGISTRY.md'), re.M)), 18)
        self.assertEqual(len(re.findall(r'^### \w+\s*$', b.read(self.root, '15_COMMANDS_AND_DRIVERS/CONTROL_PLANE_SCHEMA.md'), re.M)), 21)
        self.assertEqual(len(re.findall(r'^### Stop Rule \d+', b.read(self.root, '15_COMMANDS_AND_DRIVERS/STOP_RULES.md'), re.M)), 15)
        self.assertEqual(len(re.findall(r'^### Gate \d+', b.read(self.root, '15_COMMANDS_AND_DRIVERS/HUMAN_APPROVAL_GATES.md'), re.M)), 11)
        self.assertNotIn('AI_OPERATOR:', b.read(self.root, d.IDENTITY))
        self.assertIn('Gate 3', b.read(self.root, '15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_ONBOARDING.md'))
        self.assertIn('Gate 1', b.read(self.root, '00_FRAMEWORK/SOURCE_AUTHORITY_POLICY.md'))


if __name__ == '__main__':
    unittest.main()
