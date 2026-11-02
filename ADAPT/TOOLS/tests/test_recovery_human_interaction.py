"""Simulated operator acceptance; no independent human usability evidence."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from test_recovery_operational import OperationalAcceptance

class InteractionAcceptance:
    context_request = OperationalAcceptance.context_request
    index_request = OperationalAcceptance.index_request
    def setUp(self):
        OperationalAcceptance.setUp(self)
        scope = self.host.record['scope']
        scope['authorities']['Human Framework Maintainer'] = 'Synthetic Director'
        scope['role_evidence'] = {r: {'role_basis_reference': 'TEST-ROLE-' + r,
            'designation_reference': 'TEST-DESIGNATION'} for r in scope['authorities']}
        self.reenter()
        self.request = self.index_request()
        path = self.root / self.m.pre.INDEX
        path.write_bytes(path.read_bytes() + b'\n| CP-092 | Director Lane | NONE | SOURCE_TRUTH_V1.0 | M | 2026-10-18 | STALE | Preserve third |\n')
        binding = self.request['request']
        binding['inputs'] = [{'path': p, 'sha256': h, 'verified_at': self.host.template['checked_at']}
                             for p, h in self.m.snapshot(self.root).items()]
        binding['writes'][0]['before_sha256'] = self.m.pre.digest(path.read_bytes())
        self.before = self.m.snapshot(self.root)
    def reenter(self):
        self.entry = self.m.MaintenanceEntry(installation=self.host.record,
            ledger=self.ledger, synthetic=True)
    def review(self):
        r = self.entry.interact(self.request)
        self.assertEqual('AWAITING_HUMAN', r['status'], r)
        for field in ('ISSUE:', 'IMPACT:', 'RECOMMENDATION:', 'CHANGES:', 'RISK:', 'DECISION:'):
            self.assertIn(field, r['text'])
        master = (self.root / '15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_MASTER.md').read_text(encoding='utf-8')
        self.assertIn('interact(response=', master)
        self.assertIn('STOP the execution turn', master)
        self.assertNotIn('SHA256', r['text'])
        self.assertNotIn('authorization_binding', r['text'])
        self.assertEqual(self.before, self.m.snapshot(self.root))
        return r
    def reply(self, text='APPROVE', **kw):
        return self.entry.interact(response=text, human='Synthetic Director',
            source_reference='TEST-SIMULATED-ORIGINAL-RESPONSE', **kw)
    def test_A_F_I_approve_dual_capacity_new_session(self):
        review = self.review()
        self.reenter()
        result = self.reply('yes, approve this action')
        self.assertEqual('RECOVERY_VALIDATED', result.get('recovery_status'), result)
        self.entry.audit(result['claim'])
        for field in ('STATUS: SUCCEEDED', 'ACTION:', 'CHANGES:', 'VALIDATION:',
                      'REMAINING ISSUES:', 'NEXT ACTION:', 'APPROVAL:'):
            self.assertIn(field, result['text'])
        record = json.loads(Path(result['claim']).read_bytes())
        approvals = record['authorization']['human_authorization']['approvals']
        self.assertEqual(2, len(approvals))
        self.assertEqual(1, len(set(a['approval_reference'] for a in approvals)))
        again = self.reply()
        self.assertEqual('BLOCKED', again['status'])
        output = self.root.parent / 'human-interaction-transcript.json'
        output.write_text(json.dumps({'ADAPT_REVIEW': review['text'], 'HUMAN': 'yes, approve this action',
            'ADAPT_RESULT': result['text'], 'evidence_class': 'TECHNICAL_TEST'}, indent=2))
    def test_B_reject(self):
        self.review(); self.assertIn('rejected', self.reply('do not proceed')['text'])
        self.assertEqual(self.before, self.m.snapshot(self.root))
        self.assertEqual('BLOCKED', self.reply()['status'])
    def test_C_details_preserve_pending(self):
        self.review(); ledger = self.m.snapshot(self.ledger)
        result = self.reply('SHOW DETAILS')
        self.assertIn('SHA256', result['text'])
        self.assertEqual(ledger, self.m.snapshot(self.ledger))
        self.assertEqual('RECOVERY_VALIDATED', self.reply().get('recovery_status'))
    def test_D_ambiguous(self):
        self.review(); result = self.reply('maybe later')
        self.assertIn('clarify', result['text']); self.assertEqual(self.before, self.m.snapshot(self.root))
    def test_E_multiple(self):
        self.review(); another = deepcopy(self.request)
        another['request']['task'] = 'another reviewed task'
        another['request']['operation_reference'] += '-another'
        self.assertEqual('AWAITING_HUMAN', self.entry.interact(another)['status'])
        result = self.reply(); self.assertIn('Select exactly one', result['text'])
        self.assertEqual(self.before, self.m.snapshot(self.root))
        self.assertEqual('RECOVERY_VALIDATED', self.reply(action='another reviewed task').get('recovery_status'))
    def test_G_stale(self):
        self.review(); path = self.root / self.m.pre.INDEX
        path.write_bytes(path.read_bytes() + b'changed source\n')
        before = self.m.snapshot(self.root); result = self.reply()
        self.assertIn('fresh review', result['text'].lower())
        self.assertEqual(before, self.m.snapshot(self.root))
    def test_H_success_reporting_failure_no_replay(self):
        self.review()
        def postcheck(result):
            self.assertEqual('RECOVERY_VALIDATED', result['recovery_status'])
            self.assertEqual('TECHNICAL_EXECUTION_ACCEPTED', self.entry.audit(result['claim'])['status'])
            rows = self.m.op.table(self.m.op.text(self.root, self.m.pre.INDEX), 'Index', ['CP-ID', 'Status'])
            self.assertEqual(['CP-090', 'CP-091', 'CP-092'], [r['CP-ID'] for r in rows])
            self.assertEqual('YES', self.m.op.state(self.root)['Blocked'])
            self.assertIn('Historical disposition prose; retain verbatim.', self.m.op.text(self.root, self.m.pre.INDEX))
            # Actual incident pattern: complete row compared against a partial dictionary.
            complete = {'BLK-ID': 'BLK-001', 'Severity': 'HIGH', 'Status': 'OPEN', 'Notes': 'preserved'}
            assert complete == {'BLK-ID': 'BLK-001', 'Severity': 'HIGH', 'Status': 'OPEN'}
        result = self.reply(reporting_check=postcheck)
        self.assertIn('RECOVERY: SUCCEEDED', result['text'])
        self.assertIn('REPORTING: FAILED', result['text'])
        self.assertIn('No recovery retry is necessary', result['text'])
        self.entry.audit(result['claim']); before = self.m.snapshot(self.root)
        self.reenter()
        replay = self.reply()
        self.assertEqual('BLOCKED', replay['status'])
        self.assertIn('RECOVERY: SUCCEEDED', replay['text'])
        self.assertIn('REPORTING: FAILED', replay['text'])
        self.assertIn('No recovery retry is necessary', replay['text'])
        self.assertEqual(before, self.m.snapshot(self.root))
    def test_J_invalid_context_diagnosis(self):
        r = self.entry.diagnose(self.root, failure_id='TEST-INVALID-CONTEXT',
            failed_action='ordinary entry', observed_error='Context Index rows misplaced', request=self.request)
        self.assertIn('ISSUE:', r['text']); self.assertIn('DECISION:', r['review'])
        self.assertEqual(self.before, self.m.snapshot(self.root))
    def test_L_missing_authority(self):
        self.host.record['scope']['authorities']['Human Framework Maintainer'] = 'Other Human'
        self.reenter(); self.review(); result = self.reply()
        self.assertIn('Human Framework Maintainer', result['text']); self.assertEqual(self.before, self.m.snapshot(self.root))
    def test_L_withdrawn_before_write(self):
        self.review()
        original = self.entry.current
        def withdrawn(review):
            auth = original(review); auth['human_authorization']['withdrawn'] = True; return auth
        self.entry.current = withdrawn
        result = self.reply(); self.assertEqual('RECOVERY_INTERRUPTED', result.get('recovery_status'))
        self.assertEqual(self.before, self.m.snapshot(self.root))
    def test_L_no_response_provenance(self):
        self.review(); result = self.entry.interact(response='APPROVE')
        self.assertEqual('BLOCKED', result['status']); self.assertEqual(self.before, self.m.snapshot(self.root))
    def test_N_model_assisted_equivalent(self):
        self.review(); result = self.reply('Please go ahead with the reviewed repair.', interpreted_decision='APPROVE')
        self.assertEqual('RECOVERY_VALIDATED', result.get('recovery_status'), result)

class ModeAHumanInteraction(InteractionAcceptance, unittest.TestCase):
    mode = 'MODE_A_EXISTING_SOLUTION'
class ModeBHumanInteraction(InteractionAcceptance, unittest.TestCase):
    mode = 'MODE_B_REQUIREMENTS_ONLY'


def manual_session(mode="MODE_B_REQUIREMENTS_ONLY"):
    """Optional human acceptance on a disposable fixture; never targets ADAPT-DEV."""
    case_type = {'MODE_A_EXISTING_SOLUTION': ModeAHumanInteraction,
                 'MODE_B_REQUIREMENTS_ONLY': ModeBHumanInteraction}[mode]
    case = case_type('test_A_F_I_approve_dual_capacity_new_session')
    case.setUp()
    try:
        print('Disposable ' + mode + ' test fixture. No real instance approval or adoption. Existing blocker remains open.')
        print(case.entry.interact(case.request)['text'])
        turns = []
        while True:
            reply = input('HUMAN> ')
            case.reenter()
            result = case.reply(reply)
            print(result['text'])
            turns.append({'response': reply, 'result': result})
            if result['status'] != 'AWAITING_HUMAN':
                break
        answers = input('Could you identify the change, decide, and understand the result without help? Describe any difficulty: ')
        record = {'evidence_class': 'MANUAL_OPERATOR_SELF_REPORT_ON_TECHNICAL_FIXTURE',
                  'mode': case.mode, 'turns': turns, 'operator_feedback': answers,
                  'independent_authentication': False}
        output = case.ledger / 'manual-acceptance.json'
        output.write_text(json.dumps(record, indent=2))
        print('Actual session record:', output)
    finally:
        case.doCleanups()
