"""Synthetic onboarding conformance and integration; no real human approvals."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from fixtures import FRAMEWORK

spec=importlib.util.spec_from_file_location('onboarding_case',FRAMEWORK/'VALIDATION/onboarding_case.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


class OnboardingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='adapt-bootstrap-v2-onb-unit-')
        cls.base=Path(cls.temp.name);cls.source=cls.base/'acceptance/ADAPT'
        c.b.DOCUMENT=c.b.DOCUMENT.replace('No product code, workcells, milestone acceptance or QA signoff.','No product code, milestone acceptance or QA signoff. Governance onboarding with Gate 3 is permitted.')
        c.b.scaffold(cls.base)
        c.b.promote(cls.base,cls.source,c.data(cls.base,'basis.json'))
        c.b.context(cls.base,cls.source,c.data(cls.base,'basis.json'))
        c.fixture_inputs(cls.base,cls.source,1);c.context(cls.base,cls.source,1);c.route_fixture(cls.source,1)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def setUp(self):
        self.temp_case=tempfile.TemporaryDirectory();self.addCleanup(self.temp_case.cleanup)
        self.base=Path(self.temp_case.name);self.root=self.base/'ADAPT';shutil.copytree(self.source,self.root);self.t=c.target(1)
        for f in ['inputs-1.json','onb-context-1.json']:shutil.copyfile(self.__class__.base/f,self.base/f)

    def reject(self,reason,**kwargs):
        before=c.snapshot(self.root)
        with self.assertRaisesRegex(c.b.Stop,reason):c.preflight(self.root,self.t,**kwargs)
        self.assertEqual(before,c.snapshot(self.root))

    def alter_input(self,change):
        d=c.data(self.root,self.t['input']);change(d);c.write(self.root,self.t['input'],json.dumps(d))

    def test_first_empty_registry(self):self.assertEqual(c.preflight(self.root,self.t),'PASS_ONBOARDING_BASIS')
    def test_missing_director(self):
        (self.root/c.IDENTITY).unlink();self.reject('DIRECTOR_MISSING')
    def test_placeholder_director(self):
        c.write(self.root,c.IDENTITY,c.read(self.root,c.IDENTITY).replace(c.DIRECTOR,'{{DIRECTOR_IDENTITY}}'));self.reject('DIRECTOR_PLACEHOLDER')
    def test_conflicting_designation(self):
        self.alter_input(lambda d:d['designation'].update(human_owner='OTHER'));self.reject('DESIGNATION_CONFLICT')
    def test_wrong_project(self):
        c.write(self.root,c.IDENTITY,c.read(self.root,c.IDENTITY).replace('PROJECT: Bootstrap Acceptance','PROJECT: Other'));self.reject('DIRECTOR_AUTHORITY')
    def test_wrong_director_role(self):
        c.write(self.root,c.IDENTITY,c.read(self.root,c.IDENTITY).replace('ROLE: Director','ROLE: Developer'));self.reject('DIRECTOR_AUTHORITY')
    def test_missing_gate3(self):
        self.alter_input(lambda d:d.update(approval={}));self.reject('GATE_3')
    def test_mismatched_identity_gate3(self):
        self.alter_input(lambda d:d['approval'].update(identity='OTHER'));self.reject('GATE_3')
    def test_mismatched_role_gate3(self):
        self.alter_input(lambda d:d['approval'].update(role='QA Engineer'));self.reject('GATE_3')
    def test_unauthorized_executor(self):self.reject('EXECUTOR_AUTHORITY',executor='Backend Workcell')
    def test_spoofed_driver(self):
        c.b.set_state(self.root,CurrentAuthority='Director Lane');self.reject('EXECUTOR_AUTHORITY')
    def test_missing_ordinary_context(self):
        (self.root/self.t['pack']).unlink();self.reject('ORDINARY_CONTEXT_MISSING')
    def test_stale_ordinary_context(self):
        c.b.append(self.root,c.b.PRESERVED,'changed');self.reject('ORDINARY_CONTEXT_STALE')
    def test_missing_scope(self):
        self.alter_input(lambda d:d.update(scope=[]));self.reject('SCOPE_AUTHORIZATION')
    def test_product_mutation(self):self.reject('SCOPE_AUTHORIZATION',planned=['../project/src/greeting.py'])
    def test_duplicate_identity(self):
        c.b.put_row(self.root,c.REGISTRY,self.t['id'],[self.t['id'],'Planner','TESTALPHA',self.t['folder'],c.b.DATE,'ACTIVE','existing']);self.reject('DUPLICATE_IDENTITY')
    def test_existing_target_never_overwritten(self):
        c.write(self.root,self.t['folder']+'/private.txt','preserve');self.reject('DUPLICATE_IDENTITY')
    def test_invalid_handoff(self):
        c.write(self.root,self.t['request'],c.read(self.root,self.t['request']).replace('TO_WORKCELL / TO_LANE: Onboarding Orchestrator','TO_WORKCELL / TO_LANE: Backend'));self.reject('HANDOFF_BINDING')
    def test_missing_source_version(self):
        c.b.set_state(self.root,SourceTruthVersion='NONE');self.reject('SOURCE_VERSION')
    def test_protected_routing_mismatch(self):
        c.write(self.root,'07_GUARDRAILS/SCOPE_GUARDRAIL.md',c.read(self.root,'07_GUARDRAILS/SCOPE_GUARDRAIL.md').replace('RoutingMode: PROTECTED_DEFAULT','RoutingMode: DUAL_WRITE'));self.reject('ROUTING')
    def test_implementation_without_assignment(self):
        before=c.snapshot(self.root)
        with self.assertRaisesRegex(c.b.Stop,'IMPLEMENTATION_UNASSIGNED'):c.implementation(self.root,self.t)
        self.assertEqual(before,c.snapshot(self.root))
    def test_untraced_designation(self):
        c.write(self.root,c.b.DEC,c.read(self.root,c.b.DEC).replace('SYNTHETIC-HUMAN-DESIGNATION-001','unrelated'));self.reject('DESIGNATION_UNTRACED')
    def test_incomplete_artifacts_no_registration(self):
        c.generate(self.root,self.t);(self.root/self.t['folder']/'SCOPE_CONTRACT.md').unlink()
        with self.assertRaisesRegex(c.b.Stop,'INCOMPLETE_WORKCELL'):c.quality(self.root,self.t)
        self.assertNotIn('| PLANNER_TESTALPHA |',c.read(self.root,c.REGISTRY))
    def test_incomplete_blueprint_no_registration(self):
        c.generate(self.root,self.t);c.write(self.root,self.t['folder']+'/DEFAULT_AGENT_BLUEPRINT.md','# names only')
        with self.assertRaisesRegex(c.b.Stop,'BLUEPRINT_AGENTS'):c.quality(self.root,self.t)
        self.assertNotIn('| PLANNER_TESTALPHA |',c.read(self.root,c.REGISTRY))
    def test_actual_first_and_second_onboarding(self):
        c.onboard(self.base,self.root,1)
        self.assertEqual(len(list((self.root/self.t['folder']).iterdir())),15)
        with self.assertRaisesRegex(c.b.Stop,'IMPLEMENTATION_UNASSIGNED'):c.implementation(self.root,self.t)
        c.fixture_inputs(self.base,self.root,2);c.context(self.base,self.root,2);c.route_fixture(self.root,2)
        c.onboard(self.base,self.root,2)
        self.assertIn('| QA_TESTBETA |',c.read(self.root,c.REGISTRY))


if __name__=='__main__':unittest.main()
