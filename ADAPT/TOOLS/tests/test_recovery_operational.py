"""Operational entry/writer acceptance on disposable installed instances.

TestHost deliberately simulates operator decisions. It certifies technical
behavior only, never genuine human authority, publication or actual adoption.
"""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

from fixtures import FRAMEWORK, QUALIFICATION, fresh_instance
import test_recovery_assembly as existing
import test_recovery_supervised as humans


def load(root):
    spec = importlib.util.spec_from_file_location('operational', root / 'VALIDATION/recovery_operational.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


class TestHost:
    evidence_class = 'TECHNICAL_TEST'

    def __init__(self, module, root, ledger):
        self.module, self.root, self.ledger = module, root, ledger
        human = humans.SupervisedTests(); human.setUp()
        self.template = human.response
        self.scope = deepcopy(human.config)
        self.scope.update(target={'root': str(root), 'identity': 'Fixture'}, executor='Synthetic Operator')
        self.scope['authorities'] = {'Human Director': 'Synthetic Director',
                                    'Human Framework Maintainer': 'Synthetic Maintainer'}
        manifest = json.loads((root / 'TOOLS/MANIFEST.json').read_bytes())
        refs = {'TOOLS/' + p for p in manifest['files']} | {'TOOLS/MANIFEST.json'} | set(manifest['instance_files'])
        refs |= {module.pre.GOVERNANCE, module.op.SCHEMA, '15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md',
                 '15_COMMANDS_AND_DRIVERS/STOP_RULES.md', '10_CONTEXT_ECONOMY/CONTEXT_RULES.md',
                 '07_GUARDRAILS/CONTEXT_GUARDRAIL.md'}
        self.record = {'target': self.scope['target'], 'version': module.VERSION,
            'release_reference': 'TEST-RELEASE-NOT-PUBLICATION', 'adoption_reference': 'TEST-ADOPTION-ONLY',
            'installation_reference': 'TEST-INSTALLATION', 'installed_hashes': {
                p: module.pre.digest((root / p).read_bytes()) for p in refs},
            'scope': self.scope, 'evidence_class': self.evidence_class,
            'conditions': {'filesystem': 'LOCAL', 'exclusive_operator': True,
                           'power_loss_uncertainty': False}}
        self.authorization = None
        self.reviews = []
        self.alter = lambda a: a

    def installation(self, target):
        return deepcopy(self.record)

    def authorize(self, review):
        self.reviews.append(deepcopy(review))
        auth = deepcopy(self.template)
        auth['binding'] = deepcopy(review['authorization_binding'])
        auth['audit_reference'] = auth['binding']['audit_reference']
        for approval in auth['approvals']:
            approval['human'] = self.scope['authorities'][approval['role']]
            approval['approval_reference'] = auth['binding']['operation_reference'] + approval['role']
        self.authorization = self.alter({'maintenance_scope': deepcopy(self.scope), 'human_authorization': auth})
        return self.authorization

    def current(self, review):
        return deepcopy(self.authorization)


class OperationalAcceptance:
    mode = None

    def setUp(self):
        self.a = existing.AssemblyTests()
        def scaffold(root):
            fresh_instance(root, mode=self.mode)
        retained = QUALIFICATION / 'operational-fixtures'
        retained.mkdir(parents=True, exist_ok=True)
        base = tempfile.mkdtemp(prefix='op-', dir=retained)
        with patch.object(existing.existing, 'fresh_instance', side_effect=scaffold), patch.object(
                existing.existing.tempfile, 'TemporaryDirectory', return_value=SimpleNamespace(
                    name=base, cleanup=lambda: None)):
            self.a.setUp()
        self.addCleanup(self.a.doCleanups)
        self.f, self.root, self.external = self.a.fixture, self.a.root, self.a.external
        self.m = load(self.root)
        self.ledger = self.root.parent / 'operator-ledger'; self.ledger.mkdir()
        self.host = TestHost(self.m, self.root, self.ledger)
        self.entry = self.m.MaintenanceEntry(self.host)
        self.request = self.context_request()

    def context_request(self):
        f, p = self.f, self.f.packet
        # Current real fixture bytes, retaining source/history. Drop all fixture
        # authority/install records: production eligibility comes only from host.
        self.a.bind()
        p['evidence'] = {k:v for k,v in p['evidence'].items() if k in {'assembly', 'failure'} or k.startswith('attempt')}
        config = deepcopy(f.records['assembly']); config['format'] = 'operational-v1'; config.pop('synthetic')
        f.evidence('assembly', config)
        p['gates'] = {'all_applicable': 'APPROVED'}
        f.evidence('authorization', {k:deepcopy(p[k]) for k in ('purpose','target','task','executor','gates')})
        h = humans.SupervisedTests(); h.setUp()
        binding = deepcopy(h.packet)
        binding.update({k:deepcopy(p[k]) for k in ('purpose','target','task','executor','inputs','evidence','writes','ids','completion','gates')})
        binding.update(operation_reference='TEST-OP-' + uuid.uuid4().hex,
                       audit_reference='TEST-AUDIT-' + uuid.uuid4().hex)
        return {'kind':'CONTEXT', 'request':binding, 'parameters':deepcopy(p), 'evidence_root':str(f.external)}

    def structural_request(self):
        ref = self.m.pre.BLOCKERS
        path = self.root / ref
        lines = path.read_text(encoding='utf-8').splitlines(keepends=True)
        row = next(line for line in lines if line.startswith('| BLK-901 |'))
        path.write_text(''.join(line for line in lines if line != row) + '\n' + row, encoding='utf-8')
        binding = deepcopy(self.request['request'])
        binding.update(inputs=[{'path':p,'sha256':h,'verified_at':self.host.template['checked_at']}
                              for p,h in self.m.snapshot(self.root).items()],
                       writes=[{'path':ref,'operation':'set_fields','fields':['placement'],
                                'before_sha256':self.m.pre.digest(path.read_bytes())}],
                       ids={'blocker':'BLK-901'}, operation_reference='TEST-REPAIR-' + uuid.uuid4().hex,
                       completion={'expected':'Placement only; retain OPEN; STOP'})
        return {'kind':'STRUCTURAL','request':binding,'parameters':{'blocker':'BLK-901'},
                'evidence_root':str(self.external)}

    def accepted(self, request=None):
        plan = self.entry.preview(request or self.request)
        before = self.m.snapshot(self.root)
        result = self.entry.execute(plan)
        self.assertEqual('TECHNICAL_EXECUTION_ACCEPTED', result['status'], result)
        self.assertFalse(result['operational_authority'])
        self.assertEqual('NOT_TESTED', result['genuine_human_authority'])
        self.assertNotEqual(before, self.m.snapshot(self.root))
        self.assertEqual(result['final_hashes'], self.entry.audit(result['claim'])['final_hashes'])
        # Retain independent evidence outside temporary instance cleanup.
        dest = QUALIFICATION / 'operational-results'; dest.mkdir(exist_ok=True, parents=True)
        (dest / (self.mode + '-' + uuid.uuid4().hex + '.json')).write_text(json.dumps({
            'test':self.id(), 'mode':self.mode, 'module':self.m.__file__,
            'result':result, 'plan_sha256':plan['plan_sha256'], 'baseline':before,
            'genuine_human_authority':'NOT_TESTED'},indent=2)+'\n',encoding='utf-8')
        return plan, result

    def refused(self, plan=None):
        before = self.m.snapshot(self.root)
        if plan is None:
            with self.assertRaises(Exception):
                self.entry.preview(self.request)
        else:
            result = self.entry.execute(plan)
            self.assertEqual('REFUSED',result['status'],result)
        self.assertEqual(before,self.m.snapshot(self.root))

    def test_O01_structural(self):
        self.accepted(self.structural_request())
        self.assertIn('| OPEN |', (self.root / self.m.pre.BLOCKERS).read_text())

    def test_O02_context(self):
        self.accepted()
        self.assertEqual('YES',self.m.op.state(self.root)['Blocked'])

    def test_O03_same_instance_separate_reviews(self):
        first, result = self.accepted(self.structural_request())
        self.request = self.context_request()
        second, _ = self.accepted()
        self.assertEqual(2,len(self.host.reviews))
        self.assertNotEqual(first['plan_sha256'],second['plan_sha256'])
        self.assertNotEqual(first['authorization_binding'],second['authorization_binding'])

    def test_O04_missing_human(self):
        plan = self.entry.preview(self.request); self.host.alter = lambda a: None
        self.refused(plan)

    def test_O05_capacity(self):
        plan = self.entry.preview(self.request)
        def remove(a):
            a['human_authorization']['approvals'].pop(); return a
        self.host.alter = remove; self.refused(plan)

    def test_O06_wrong_instance(self):
        self.request['request']['target']['identity'] = 'other'; self.refused()

    def test_O07_version_adoption(self):
        for key,value in [('version','ADAPT-FW-0005'),('adoption_reference','')]:
            before = self.host.record[key]; self.host.record[key]=value
            self.refused(); self.host.record[key]=before

    def test_O08_changed_plan(self):
        plan=self.entry.preview(self.request); plan['operations'][0]['after_image_hex']+='20'
        self.refused(plan)

    def test_O09_changed_source(self):
        plan=self.entry.preview(self.request); path=self.root/self.f.source
        path.write_bytes(path.read_bytes()+b'changed\n'); self.refused(plan)

    def test_O10_unapproved_path(self):
        self.request['parameters']['writes'][0]['path']='01_SOURCE_TRUTH/other.md'
        self.request['request']['writes']=deepcopy(self.request['parameters']['writes']); self.refused()

    def test_O11_replay(self):
        first,_=self.accepted(self.structural_request()); self.request=self.context_request()
        self.request['request']['operation_reference']=first['request']['request']['operation_reference']
        plan=self.entry.preview(self.request); self.refused(plan)

    def test_O12_interruption_no_retry(self):
        plan=self.entry.preview(self.request)
        def interrupt(event,seq):
            if event=='after_replace': raise ValueError('TEST_INTERRUPTION')
        with patch.object(self.m,'_checkpoint',side_effect=interrupt):
            result=self.entry.execute(plan)
        self.assertEqual('INTERRUPTED',result['status'],result)
        self.assertTrue(Path(result['claim']).exists())
        self.assertTrue(list(self.ledger.rglob('journal.jsonl')))
        self.assertEqual('REFUSED',self.entry.execute(plan)['status'])

    def test_O13_ownership_conflict(self):
        plan=self.entry.preview(self.request)
        target=self.ledger/self.m.pre.digest(str(self.root).casefold().encode()); target.mkdir()
        (target/'00000000.claim.json').write_bytes(b'{}\n'); self.refused(plan)

    def test_O14_partial_evidence(self):
        plan=self.entry.preview(self.request); initial=self.m.snapshot(self.root)
        def interrupt(event,seq):
            if event=='after_completion' and seq==2: raise ValueError('TEST_PARTIAL')
        with patch.object(self.m,'_checkpoint',side_effect=interrupt): result=self.entry.execute(plan)
        self.assertEqual('INTERRUPTED',result['status'],result)
        self.assertNotEqual(initial,self.m.snapshot(self.root))
        self.assertTrue(list(self.ledger.rglob('interruption.json')))
        with self.assertRaises(Exception): self.entry.audit(result['claim'])

    def test_O15_journal_mismatch(self):
        _,result=self.accepted(); path=Path(result['journal']); path.write_bytes(path.read_bytes()+b'{}\n')
        with self.assertRaises(ValueError): self.entry.audit(result['claim'])

    def test_O16_final_state_invalid(self):
        plan=self.entry.preview(self.request)
        def corrupt(event,seq):
            if event=='after_replace' and seq==7:
                path=self.root/self.m.pre.INDEX; path.write_bytes(path.read_bytes()+b'bad\n')
        with patch.object(self.m,'_checkpoint',side_effect=corrupt): result=self.entry.execute(plan)
        self.assertEqual('INTERRUPTED',result['status'],result)

    def test_O17_no_implicit_resolution(self):
        self.accepted(); self.assertIn('| OPEN |',(self.root/self.m.pre.BLOCKERS).read_text())

    def test_O18_no_context_activation(self):
        self.accepted(); rows=self.m.op.table(self.m.op.text(self.root,self.m.pre.INDEX),'Index',['Status'])
        self.assertEqual('ARCHIVED',rows[-1]['Status'])

    def test_O19_no_handback(self):
        self.accepted(); self.assertEqual('YES',self.m.op.state(self.root)['Blocked'])
        with self.assertRaises(self.m.op.Problem): self.m.op.prompt_next(self.root)

    def test_O20_protected_without_host(self):
        protected=FRAMEWORK.parent/'ADAPT-DEV/ADAPT'
        before={p.relative_to(protected).as_posix():self.m.pre.digest(p.read_bytes())
                for p in protected.rglob('*') if p.is_file()}
        self.request['request']['target']={'root':str(protected),'identity':'ADAPT-SELF-HOST-001'}
        with self.assertRaises(ValueError): self.m.MaintenanceEntry().preview(self.request)
        self.refused()
        self.assertEqual(before,{p.relative_to(protected).as_posix():self.m.pre.digest(p.read_bytes())
                                 for p in protected.rglob('*') if p.is_file()})

    def test_O21_ordinary_lifecycle(self):
        with self.assertRaises(self.m.op.Problem): self.m.op.prompt_next(self.root)
        self.assertEqual('YES',self.m.op.state(self.root)['Blocked'])

    def test_O22_packet_cannot_supply_entry(self):
        self.request['approved']=True
        self.refused()

    def test_O23_withdraw_at_write(self):
        plan=self.entry.preview(self.request)
        def withdrawn(review):
            auth=deepcopy(self.host.authorization); auth['human_authorization']['withdrawn']=True; return auth
        self.host.current=withdrawn
        before=self.m.snapshot(self.root); result=self.entry.execute(plan)
        self.assertEqual('INTERRUPTED',result['status'],result)
        self.assertEqual(before,self.m.snapshot(self.root))

    def test_O24_unsupported_conditions(self):
        self.host.record['conditions']['power_loss_uncertainty']=True; self.refused()

    def test_O25_shared_interaction_needs_no_account_isolation(self):
        self.accepted(self.structural_request())

    def test_O26_interruption_boundaries(self):
        # Entire production writer boundary sweep on fresh disposable targets.
        for event in ('after_intent','before_replace','after_replace','after_completion'):
            for sequence in range(1,8):
                with self.subTest(event=event,sequence=sequence):
                    case=type(self)('test_O02_context'); case.setUp()
                    try:
                        plan=case.entry.preview(case.request)
                        def fail(e,s):
                            if (e,s)==(event,sequence): raise ValueError('TEST_BOUNDARY')
                        with patch.object(case.m,'_checkpoint',side_effect=fail): result=case.entry.execute(plan)
                        self.assertEqual('INTERRUPTED',result['status'],result)
                        claim=Path(result['claim']); self.assertTrue(claim.exists())
                        self.assertFalse(claim.with_name(claim.name.replace('.claim.','.outcome.')).exists())
                        with self.assertRaises(Exception): case.entry.audit(claim)
                    finally: case.doCleanups()

    def child(self, event, action):
        plan = self.entry.preview(self.request)
        source = self.root.parent / 'child-plan.json'
        source.write_text(json.dumps(plan), encoding='utf-8')
        script = '\n'.join([
            'import sys,pathlib,json,os,time',
            f'sys.path.insert(0,{str(Path(__file__).parent)!r})',
            'from test_recovery_operational import load,TestHost',
            f'root=pathlib.Path({str(self.root)!r}); m=load(root)',
            f'host=TestHost(m,root,pathlib.Path({str(self.ledger)!r}))',
            f'plan=json.loads(pathlib.Path({str(source)!r}).read_bytes())',
            'def checkpoint(e,s):',
            f' if e=={event!r} and s==1:',
            *['  '+line for line in action],
            'm._checkpoint=checkpoint',
            'print(json.dumps(m.MaintenanceEntry(host).execute(plan)),flush=True)',
        ])
        return plan, subprocess.Popen([sys.executable,'-B','-c',script], stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,text=True)

    def test_O27_abrupt_process_death(self):
        _,child=self.child('after_replace',['os._exit(73)'])
        out,err=child.communicate(timeout=60)
        self.assertEqual(73,child.returncode,(out,err))
        claims=list(self.ledger.rglob('*.claim.json')); self.assertEqual(1,len(claims))
        with self.assertRaises(Exception): self.entry.audit(claims[0])
        self.assertTrue(list(self.ledger.rglob('journal.jsonl')))

    def test_O28_real_competing_process(self):
        marker=self.root.parent/'child-owned'; release=self.root.parent/'child-release'
        plan,child=self.child('after_intent',[
            f'pathlib.Path({str(marker)!r}).write_text("owned")',
            'end=time.monotonic()+30',
            f'while not pathlib.Path({str(release)!r}).exists() and time.monotonic()<end: time.sleep(.05)',
        ])
        try:
            end=time.monotonic()+30
            while not marker.exists() and time.monotonic()<end and child.poll() is None:
                time.sleep(.05)
            self.assertTrue(marker.exists())
            self.refused(plan)
        finally:
            release.write_text('release')
            out,err=child.communicate(timeout=60)
        self.assertEqual(0,child.returncode,err)
        self.assertEqual('TECHNICAL_EXECUTION_ACCEPTED',json.loads(out)['status'],out)

    def test_O29_first_approval_cannot_authorize_context(self):
        self.accepted(self.structural_request())
        old=deepcopy(self.host.authorization)
        self.request=self.context_request(); plan=self.entry.preview(self.request)
        self.host.authorize=lambda review: old
        self.refused(plan)

    def test_O30_preview_is_read_only(self):
        root_before=self.m.snapshot(self.root)
        ledger_before=self.m.snapshot(self.ledger)
        plan=self.entry.preview(self.request)
        self.assertTrue(plan['files'])
        self.assertEqual(root_before,self.m.snapshot(self.root))
        self.assertEqual(ledger_before,self.m.snapshot(self.ledger))

    def test_O31_installation_bytes_changed(self):
        path=self.root/'VALIDATION/recovery_operational.py'
        path.write_bytes(path.read_bytes()+b'\n# changed\n')
        self.refused()

    def test_O32_audit_mismatch_blocks_sequential_entry(self):
        _,result=self.accepted(self.structural_request())
        self.request=self.context_request(); plan=self.entry.preview(self.request)
        path=Path(result['journal']); path.write_bytes(path.read_bytes()+b'{}\n')
        self.refused(plan)

    def index_request(self):
        path=self.root/self.m.pre.INDEX
        original=path.read_bytes()
        first=b'| CP-090 | Director Lane | NONE | SOURCE_TRUTH_V1.0 | M | 2026-10-18 | STALE | Preserve first |\n'
        second=b'| CP-091 | Director Lane | NONE | SOURCE_TRUTH_V1.0 | M | 2026-10-18 | ACTIVE | Preserve second |\n'
        path.write_bytes(original+b'\n'+first+b'\nHistorical disposition prose; retain verbatim.\n\n'+second)
        binding=deepcopy(self.request['request'])
        binding.update(inputs=[{'path':p,'sha256':h,'verified_at':self.host.template['checked_at']}
                              for p,h in self.m.snapshot(self.root).items()],
                       writes=[{'path':self.m.pre.INDEX,'operation':'set_fields','fields':['placement'],
                                'before_sha256':self.m.pre.digest(path.read_bytes())}],
                       ids={'register':'CONTEXT_INDEX','operation':'NORMALIZE_TABLE_PLACEMENT'},
                       operation_reference='TEST-INDEX-'+uuid.uuid4().hex,
                       completion={'expected':'Row placement only; preserve every value and prose; STOP'})
        return {'kind':'STRUCTURAL','request':binding,'parameters':deepcopy(binding['ids']),
                'evidence_root':str(self.external)}

    def test_O33_index_structure_preserves_prose_and_values(self):
        request=self.index_request(); before=(self.root/self.m.pre.INDEX).read_bytes()
        self.accepted(request)
        after=(self.root/self.m.pre.INDEX).read_bytes()
        self.assertEqual(sorted(before.splitlines()),sorted(after.splitlines()))
        rows=self.m.op.table(after.decode(),'Index',['CP-ID','Status'])
        self.assertEqual(['CP-090','CP-091'],[r['CP-ID'] for r in rows])
        self.assertEqual(['STALE','ACTIVE'],[r['Status'] for r in rows])

    def test_O34_index_repair_then_separate_context(self):
        first,_=self.accepted(self.index_request())
        self.f.packet['ids']['CP']='CP-092'
        self.request=self.context_request(); second,_=self.accepted()
        self.assertNotEqual(first['authorization_binding'],second['authorization_binding'])

    def test_O35_invalid_index_row_refuses(self):
        self.request=self.index_request()
        path=self.root/self.m.pre.INDEX
        path.write_bytes(path.read_bytes().replace(b'| CP-091 |',b'| CP-090 |'))
        self.refused()

    def test_O36_index_cannot_expand_structural_scope(self):
        self.request=self.index_request()
        self.request['request']['writes'][0]['fields']=['Status']
        self.refused()

    def test_O37_exact_json_types_are_required(self):
        plan=self.entry.preview(self.request)
        plan['operations'][0]['sequence']=True
        self.refused(plan)
        self.assertEqual([],self.host.reviews)
        self.host.record['conditions']['exclusive_operator']=1
        self.refused()

    def test_O38_resolved_source_aliases_refuse(self):
        packet=self.request['parameters']
        alias=deepcopy(packet['inputs'][0]); alias['path']=' '+alias['path']+' '
        alias['class']='HISTORICAL_RECOVERY'
        packet['inputs'].append(alias)
        self.request['request']['inputs']=deepcopy(packet['inputs'])
        self.refused()
        packet['inputs'].pop()
        self.request['request']['inputs']=deepcopy(packet['inputs'])
        evidence=packet['evidence'][next(iter(packet['evidence']))]
        evidence['path']=' '+evidence['path']+' '
        self.request['request']['evidence']=deepcopy(packet['evidence'])
        self.refused()

    def normal_entry(self):
        # Explicit simulated human responses, exclusively disposable test fixtures.
        self.host.record['scope']['role_evidence'] = {
            role: {'role_basis_reference': 'TEST-ROLE-' + role,
                   'designation_reference': 'TEST-DESIGNATION'}
            for role in self.host.scope['authorities']}
        self.decisions = lambda review: [
            {'decision': 'APPROVE_EXACT_ACTION', 'human': human, 'capacities': [role],
             'source_reference': 'TEST-SIMULATED-HUMAN-' + role,
             'plan_sha256': review['plan_sha256']}
            for role, human in self.host.scope['authorities'].items()]
        self.entry = self.m.MaintenanceEntry(installation=self.host.record, ledger=self.ledger,
            interaction=lambda review: self.decisions(review), synthetic=True)

    def test_HG01_malformed_register_report_review_approval_write_audit_stop(self):
        self.normal_entry()
        request = self.structural_request()
        before = self.m.snapshot(self.root)
        report = self.entry.diagnose(self.root, failure_id='TEST-MALFORMED-REGISTER',
            failed_action='ordinary dispatch', observed_error='Malformed Blockers placement', request=request)
        self.assertEqual('READY_FOR_HUMAN_REVIEW', report['status'])
        self.assertEqual(before, self.m.snapshot(self.root))
        for label in ('ISSUE:', 'CAUSE:', 'IMPACT:', 'RECOMMENDED ACTION:', 'FILES AFFECTED:',
                      'EXPECTED RESULT:', 'RISK:', 'APPROVAL REQUIRED:'):
            self.assertIn(label, report['review'])
        result = self.entry.execute(report['plan'])
        self.assertEqual('RECOVERY_VALIDATED', result['recovery_status'], result)
        self.assertEqual('STOP', result['action'])
        self.entry.audit(result['claim'])
        self.assertIn('| OPEN |', (self.root/self.m.pre.BLOCKERS).read_text())

    def test_HG02_interrupted_index_separate_fresh_context_approval(self):
        self.normal_entry()
        first = self.entry.preview(self.index_request())
        result = self.entry.execute(first)
        self.assertEqual('RECOVERY_VALIDATED', result['recovery_status'], result)
        self.entry.audit(result['claim'])
        self.f.packet['ids']['CP'] = 'CP-092'
        self.request = self.context_request()
        report = self.entry.diagnose(self.root, failure_id='TEST-EXHAUSTED-CONTEXT',
            failed_action='context assembly', observed_error='Stale context; exhausted retries', request=self.request)
        self.assertEqual('READY_FOR_HUMAN_REVIEW', report['status'], report.get('refusal'))
        self.assertNotEqual(first['plan_sha256'], report['plan']['plan_sha256'])
        result = self.entry.execute(report['plan'])
        self.assertEqual('RECOVERY_VALIDATED', result['recovery_status'], result)
        self.entry.audit(result['claim'])
        self.assertEqual('YES', self.m.op.state(self.root)['Blocked'])
        self.assertEqual('ARCHIVED', self.m.op.table(self.m.op.text(self.root,self.m.pre.INDEX),
            'Index',['Status'])[-1]['Status'])
        with self.assertRaises(self.m.op.Problem): self.m.op.prompt_next(self.root)

    def test_HG03_missing_rejected_ambiguous_wrong_capacity_or_plan_refuse(self):
        self.normal_entry()
        plan = self.entry.preview(self.structural_request())
        decisions = self.decisions(plan)
        variants = [None, [], [{'decision': 'REJECT'}], [{'decision': 'maybe'}]]
        for field, value in (('human','wrong-human'), ('capacities',['Unknown Role']),
                             ('plan_sha256','0'*64), ('source_reference','')):
            variant = deepcopy(decisions); variant[0][field] = value; variants.append(variant)
        before = self.m.snapshot(self.root)
        for variant in variants:
            self.decisions = lambda review, value=variant: value
            result = self.entry.execute(plan)
            self.assertEqual('RECOVERY_REFUSED', result['recovery_status'], result)
            self.assertEqual(before, self.m.snapshot(self.root))
            self.assertEqual({}, self.m.snapshot(self.ledger))

    def test_HG04_no_production_approval_from_packet(self):
        self.normal_entry()
        # Exercise genuine-input declaration branch without claiming real consent.
        self.entry.evidence_class = 'HUMAN_SUPERVISED'
        self.entry._record['evidence_class'] = 'HUMAN_SUPERVISED'
        self.entry.interaction = None
        plan = self.entry.preview(self.structural_request())
        self.refused(plan)

    def test_HG05_same_human_two_explicit_capacities_one_response(self):
        self.host.scope['authorities']['Human Framework Maintainer'] = 'Synthetic Director'
        self.normal_entry()
        self.decisions = lambda review: [{'human': 'Synthetic Director',
            'capacities': ['Human Director','Human Framework Maintainer'],
            'source_reference':'TEST-ONE-EXPLICIT-DUAL-CAPACITY-RESPONSE',
            'decision':'APPROVE_EXACT_ACTION','plan_sha256':review['plan_sha256']}]
        result = self.entry.execute(self.entry.preview(self.structural_request()))
        self.assertEqual('RECOVERY_VALIDATED', result['recovery_status'], result)
        self.entry.audit(result['claim'])

    def test_HG06_report_without_entry_or_valid_ordinary_state(self):
        path = self.root/self.m.op.CP
        path.write_bytes(b'Malformed ordinary state\n')
        before = self.m.snapshot(self.root)
        report = self.m.MaintenanceEntry().diagnose(self.root, failure_id='TEST-UNKNOWN',
            failed_action='ordinary action', observed_error='Unsupported failure')
        self.assertEqual('DIAGNOSTIC_ONLY', report['status'])
        self.assertEqual('STOP', report['action'])
        self.assertEqual([], report['proposed_mutation_scope'])
        self.assertEqual(before, self.m.snapshot(self.root))

    def test_HG07_withdraw_normal_decision_before_write(self):
        self.normal_entry()
        plan = self.entry.preview(self.structural_request())
        original = self.entry.authorize
        def withdraw(review):
            auth = original(review); self.entry.withdraw(); return auth
        self.entry.authorize = withdraw
        before = self.m.snapshot(self.root)
        result = self.entry.execute(plan)
        self.assertEqual('RECOVERY_INTERRUPTED', result['recovery_status'], result)
        self.assertEqual(before, self.m.snapshot(self.root))

    def test_HG08_unsupported_recovery_report_refuses_mutation(self):
        self.normal_entry()
        request = deepcopy(self.request); request['kind'] = 'GENERIC_FIX'
        before = self.m.snapshot(self.root)
        report = self.entry.diagnose(self.root, failure_id='TEST-UNSUPPORTED',
            failed_action='unknown action', observed_error='No supported repair', request=request)
        self.assertEqual('RECOVERY_REFUSED', report['status'])
        self.assertEqual('STOP', report['action'])
        self.assertEqual([], report['proposed_mutation_scope'])
        self.assertEqual(before, self.m.snapshot(self.root))
        self.assertEqual({}, self.m.snapshot(self.ledger))

    def test_O39_claim_reference_and_current_state_tampering_refuse(self):
        for tamper in ('claim','reference','current_state'):
            with self.subTest(tamper=tamper):
                case=type(self)('test_O01_structural');case.setUp()
                try:
                    _,result=case.accepted(case.structural_request())
                    claim=Path(result['claim']);record=json.loads(claim.read_bytes())
                    if tamper=='claim':
                        (case.root.parent/'original-claim.bin').write_bytes(claim.read_bytes())
                        record['authorization']['human_authorization']['approvals']=[]
                        claim.write_text(json.dumps(record),encoding='utf-8')
                    elif tamper=='reference':
                        reference=Path(record['reference'])
                        (case.root.parent/'original-reference.bin').write_bytes(reference.read_bytes())
                        reference.write_bytes(reference.read_bytes()+b'\n')
                    else:
                        path=case.root/case.f.source
                        path.write_bytes(path.read_bytes()+b'changed after completion\n')
                    with self.assertRaises(ValueError):case.entry.audit(claim)
                    case.request=case.context_request()
                    plan=case.entry.preview(case.request)
                    case.refused(plan)
                finally:case.doCleanups()


class ModeAOperational(OperationalAcceptance,unittest.TestCase):
    mode='MODE_A_EXISTING_SOLUTION'


class ModeBOperational(OperationalAcceptance,unittest.TestCase):
    mode='MODE_B_REQUIREMENTS_ONLY'
