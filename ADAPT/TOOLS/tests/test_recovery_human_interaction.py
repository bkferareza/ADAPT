"""Simulated operator acceptance; no independent human usability evidence."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
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
        self.capture(None, r)
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
        result = self.entry.interact(response=text, human='Synthetic Director',
            source_reference='TEST-SIMULATED-ORIGINAL-RESPONSE', **kw)
        self.capture(text, result)
        return result
    def capture(self, response, result):
        with (self.root.parent / 'chat-contract-transcript.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'test': self.id(), 'evidence_class': 'TECHNICAL_TEST',
                'human_response_simulated': response, 'result': result,
                'chat_delivery_observed': False}) + '\n')
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

    def test_chat_approval_details_and_rejection_are_self_contained(self):
        review = self.review()
        self.assertIn('Do you approve this exact action?', review['text'])
        self.assertIn('Execution remains blocked', review['text'])
        details = self.reply('Show details.')
        self.assertIn('decision remains pending', details['text'])
        self.assertIn('Row placement only', details['text'])
        self.assertEqual(self.before, self.m.snapshot(self.root))
        rejected = self.reply('Reject.')
        self.assertIn('CHANGES: None', rejected['text'])
        self.assertIn('No recovery attempted', rejected['text'])
        self.assertIn('Request a new review', rejected['text'])

    def test_chat_failed_validation_explains_no_changes_and_fresh_review(self):
        self.review()
        path = self.root / self.m.pre.INDEX
        path.write_bytes(path.read_bytes() + b'changed after review\n')
        before = self.m.snapshot(self.root)
        result = self.reply()
        self.assertIn('CHANGES: None', result['text'])
        self.assertIn('plan or source changed', result['text'])
        self.assertIn('fresh review', result['text'])
        self.assertEqual(before, self.m.snapshot(self.root))

    def test_chat_no_pending_review_explains_next_step(self):
        result = self.reply('Approve.')
        self.assertEqual('NO_PENDING_REVIEW', result['reason'])
        self.assertIn('no pending reviewed action', result['text'])
        self.assertIn('no instance files changed', result['text'])
        self.assertIn('request a new review', result['text'])
        self.assertEqual(self.before, self.m.snapshot(self.root))

    def test_chat_question_is_not_literal_consent(self):
        self.review()
        for response in ('Approve?', 'Approve...', 'Approve only if the blocker closes.'):
            result = self.reply(response)
            self.assertEqual('AWAITING_HUMAN', result['status'])
            self.assertIn('clarify', result['text'])
            self.assertEqual(self.before, self.m.snapshot(self.root))
        result = self.reply('Approve.')
        self.assertEqual('RECOVERY_VALIDATED', result['recovery_status'])
        self.entry.audit(result['claim'])

    def test_chat_renderer_failure_has_truthful_fallback_and_no_replay(self):
        self.review()
        with patch.object(self.m, 'human_outcome', side_effect=RuntimeError('renderer unavailable')):
            result = self.reply()
        self.assertEqual('RECOVERY_VALIDATED', result['recovery_status'])
        self.assertEqual('FAILED', result['reporting_status'])
        self.assertIn('Recovery succeeded and passed validation', result['text'])
        self.assertIn('Reporting failed', result['text'])
        self.assertIn('do not retry recovery', result['text'])
        self.assertIn('blocker remains open', result['text'])
        self.entry.audit(result['claim'])
        before = self.m.snapshot(self.root)
        self.reenter()
        replay = self.reply()
        self.assertEqual('BLOCKED', replay['status'])
        self.assertEqual(before, self.m.snapshot(self.root))

    def test_chat_interrupted_operation_preserves_uncertainty(self):
        self.review()
        original = self.entry.current
        def withdrawn(review):
            auth = original(review); auth['human_authorization']['withdrawn'] = True; return auth
        self.entry.current = withdrawn
        result = self.reply()
        self.assertEqual('RECOVERY_INTERRUPTED', result['recovery_status'])
        self.assertIn('exact completed write extent has not been established', result['text'])
        self.assertIn('do not retry or resume', result['text'])
        self.assertEqual(self.before, self.m.snapshot(self.root))

    def test_R1_interrupted_write_then_reporting_failure(self):
        self.review()
        def interrupt(event, sequence):
            if event == 'after_replace':
                raise OSError('injected interruption after actual replacement')
        writer_results = []
        def reporting_failure(result):
            writer_results.append(result)
            raise RuntimeError('injected reporting check failure')
        with patch.object(self.m, '_checkpoint', side_effect=interrupt):
            result = self.reply(reporting_check=reporting_failure)
        saved = writer_results[0]
        self.assertEqual('RECOVERY_INTERRUPTED', saved['recovery_status'])
        self.assertNotEqual(self.before[self.m.pre.INDEX], self.m.snapshot(self.root)[self.m.pre.INDEX])
        claim = Path(saved['claim'])
        record = json.loads(claim.read_bytes())
        journal = Path(record['evidence']) / 'journal.jsonl'
        self.assertTrue(journal.is_file())
        self.assertEqual(saved, json.loads((Path(record['evidence']) / 'interruption.json').read_bytes()))
        self.assertEqual(saved, json.loads(next((self.ledger / 'pending-reviews').glob('*.result')).read_bytes()))
        for key, value in saved.items():
            self.assertEqual(value, result[key])
        self.assertIn('RECOVERY: INTERRUPTED', result['text'])
        self.assertIn('REPORTING: FAILED', result['text'])
        self.assertNotIn('CHANGES: None', result['text'])
        self.assertIn('may have partially changed', result['text'])
        self.assertIn(str(claim), result['text'])
        self.assertEqual('STOP', result['action'])
        before = self.m.snapshot(self.root), self.m.snapshot(self.ledger)
        self.reenter()
        with patch.object(self.entry, 'execute', side_effect=AssertionError('writer replay')):
            replay = self.reply()
        self.assertEqual('BLOCKED', replay['status'])
        self.assertEqual(before, (self.m.snapshot(self.root), self.m.snapshot(self.ledger)))

    def test_R2_saved_success_renderer_failure(self):
        self.review()
        completed = self.reply('yes, approve this action')
        self.entry.audit(completed['claim'])
        before = self.m.snapshot(self.root)
        claim = Path(completed['claim'])
        saved_path = claim.with_name(claim.name.replace('.claim.', '.outcome.'))
        saved_bytes = saved_path.read_bytes()
        used = {str(p): p.read_bytes() for p in (self.ledger / 'pending-reviews').glob('*.used')}
        self.reenter()
        with patch.object(self.entry, 'execute', side_effect=AssertionError('writer replay')) as writer, \
             patch.object(self.entry, 'authorize', side_effect=AssertionError('approval replay')) as approval, \
             patch.object(self.m, 'human_outcome', side_effect=RuntimeError('renderer unavailable')) as renderer:
            result = self.reply(action=self.request['request']['task'])
        writer.assert_not_called()
        approval.assert_not_called()
        self.assertEqual(1, renderer.call_count)
        self.assertEqual('BLOCKED', result['status'])
        self.assertEqual('RECOVERY_VALIDATED', result['recovery_status'])
        for field in ('RECOVERY: SUCCEEDED', 'REPORTING: FAILED', 'previously succeeded',
                      'recorded validation passed', 'saved outcome remains authoritative',
                      'No recovery replay is necessary'):
            self.assertIn(field, result['text'])
        self.assertEqual(completed['claim'], result['claim'])
        self.assertEqual(saved_bytes, saved_path.read_bytes())
        self.assertEqual(used, {str(p): p.read_bytes() for p in (self.ledger / 'pending-reviews').glob('*.used')})
        self.assertEqual(before, self.m.snapshot(self.root))
        self.entry.audit(result['claim'])

    def test_interruption_after_file_validation_retains_validation(self):
        self.review()
        original = self.m.rt._persist_new
        def fail_completion(path, data):
            if Path(path).name == 'completion.json':
                raise OSError('injected completion persistence failure')
            return original(path, data)
        def reporting_failure(result):
            raise RuntimeError('reporting unavailable')
        with patch.object(self.m.rt, '_persist_new', side_effect=fail_completion):
            result = self.reply(reporting_check=reporting_failure)
        self.assertEqual('RECOVERY_INTERRUPTED', result['recovery_status'])
        self.assertEqual(result['final_hashes'], self.m.snapshot(self.root))
        journal = Path(result['journal'])
        self.assertEqual(result['journal_sha256'], self.m.pre.digest(journal.read_bytes()))
        self.assertIn(b'FINAL_VALIDATED', journal.read_bytes())
        self.assertIn('RECOVERY: INTERRUPTED', result['text'])
        self.assertIn('REPORTING: FAILED', result['text'])
        self.assertIn('VALIDATION: Recorded file validation passed', result['text'])
        self.assertNotIn('RECOVERY: SUCCEEDED', result['text'])
        self.assertNotIn('CHANGES: None', result['text'])

    def test_incomplete_saved_outcome_audit_failure_is_unknown(self):
        self.review()
        completed = self.reply()
        self.entry.audit(completed['claim'])
        claim = Path(completed['claim'])
        saved = claim.with_name(claim.name.replace('.claim.', '.outcome.'))
        saved.write_text('{}', encoding='utf-8')
        before = self.m.snapshot(self.root)
        self.reenter()
        with patch.object(self.entry, 'execute', side_effect=AssertionError('writer replay')) as writer, \
             patch.object(self.m, 'human_outcome', wraps=self.m.human_outcome) as renderer:
            result = self.reply()
        writer.assert_not_called()
        renderer.assert_not_called()
        self.assertIn('RECOVERY: UNKNOWN', result['text'])
        self.assertIn('CHANGES: UNKNOWN', result['text'])
        self.assertIn('VALIDATION: UNKNOWN', result['text'])
        self.assertEqual(completed['claim'], result['claim'])
        self.assertEqual('{}', saved.read_text(encoding='utf-8'))
        self.assertEqual(before, self.m.snapshot(self.root))

    def test_reporting_failure_after_writer_refusal(self):
        self.review()
        original = self.entry._authority
        def refuse(plan, *, initial=False):
            if initial and self.entry._authorization is not None:
                raise ValueError('HUMAN_APPROVAL_REFUSED')
            return original(plan, initial=initial)
        def reporting_failure(result):
            self.assertEqual('RECOVERY_REFUSED', result['recovery_status'])
            raise RuntimeError('reporting unavailable')
        with patch.object(self.entry, '_authority', side_effect=refuse):
            result = self.reply(reporting_check=reporting_failure)
        self.assertEqual('RECOVERY_REFUSED', result['recovery_status'])
        self.assertIn('RECOVERY: REFUSED', result['text'])
        self.assertIn('REPORTING: FAILED', result['text'])
        self.assertNotIn('RECOVERY: SUCCEEDED', result['text'])
        self.assertNotIn('CHANGES: None', result['text'])
        self.assertEqual(self.before, self.m.snapshot(self.root))

    def test_reporting_fallback_incomplete_evidence(self):
        for evidence in (None, {}, {'recovery_status': 'RECOVERY_VALIDATED'},
                         {'recovery_status': 'RECOVERY_INTERRUPTED', 'status': 'INTERRUPTED'},
                         {'recovery_status': 'RECOVERY_REFUSED'}):
            with self.subTest(evidence=evidence):
                result = self.m.reporting_fallback(evidence, 'renderer unavailable')
                self.assertIn('CHANGES: UNKNOWN', result['text'])
                self.assertNotIn('RECOVERY: SUCCEEDED', result['text'])
                self.assertNotIn('CHANGES: None', result['text'])
                self.assertIn('REPORTING: FAILED', result['text'])
                self.assertIn('VALIDATION: UNKNOWN', result['text'])
                self.assertEqual('STOP', result['action'])

    def test_missing_writer_outcome_reporting_failure(self):
        self.review()
        def reporting_failure(result):
            raise RuntimeError('missing result at reporting stage')
        # Deliberately absent evidence, never a mocked successful mutation.
        with patch.object(self.entry, 'execute', return_value=None) as writer, \
             patch.object(self.m, 'human_outcome', side_effect=RuntimeError('renderer unavailable')) as renderer:
            result = self.reply(reporting_check=reporting_failure)
        writer.assert_called_once()
        renderer.assert_not_called()
        self.assertIn('RECOVERY: UNKNOWN', result['text'])
        self.assertIn('CHANGES: UNKNOWN', result['text'])
        self.assertIn('VALIDATION: UNKNOWN', result['text'])
        self.assertEqual(self.before, self.m.snapshot(self.root))

    def test_preexecution_renderer_failure_no_second_render(self):
        self.host.record['scope']['authorities']['Human Framework Maintainer'] = 'Other Human'
        self.reenter()
        self.review()
        with patch.object(self.m, 'human_outcome', side_effect=RuntimeError('renderer unavailable')) as renderer:
            result = self.reply()
        self.assertEqual(1, renderer.call_count)
        self.assertIn('REPORTING: FAILED', result['text'])
        self.assertIn('CHANGES: UNKNOWN', result['text'])
        self.assertEqual(self.before, self.m.snapshot(self.root))

    def test_R3_consumed_evidence_outcome_matrix(self):
        for defect in ('empty_reference', 'unreadable_reference', 'missing_reference',
                       'missing_claim', 'missing_outcome', 'missing_completion',
                       'failed_audit', 'lookup_and_renderer_failure'):
            with self.subTest(defect=defect):
                self.setUp()
                self.review()
                completed = self.reply()
                self.assertEqual('RECOVERY_VALIDATED', completed['recovery_status'])
                self.assertNotEqual(self.before[self.m.pre.INDEX], self.m.snapshot(self.root)[self.m.pre.INDEX])
                self.entry.audit(completed['claim'])
                claim = Path(completed['claim'])
                record = json.loads(claim.read_bytes())
                reference = Path(record['reference'])
                saved = claim.with_name(claim.name.replace('.claim.', '.outcome.'))
                originals = {str(p): p.read_bytes().hex() for p in (reference, claim, saved)}
                (self.root.parent / 'r3-original-evidence.json').write_text(json.dumps(originals, indent=2))
                if defect in ('empty_reference', 'lookup_and_renderer_failure'):
                    reference.write_bytes(b'{}')
                elif defect == 'unreadable_reference':
                    reference.write_bytes(b'\xff\x00invalid JSON')
                elif defect == 'missing_reference':
                    reference.unlink()
                elif defect == 'missing_claim':
                    claim.unlink()
                elif defect == 'missing_outcome':
                    saved.unlink()
                elif defect == 'missing_completion':
                    (Path(record['evidence']) / 'completion.json').unlink()
                else:
                    journal = Path(record['evidence']) / 'journal.jsonl'
                    journal.write_bytes(journal.read_bytes() + b'{}\n')
                before = self.m.snapshot(self.root), self.m.snapshot(self.ledger)
                self.reenter()
                with patch.object(self.entry, 'execute', side_effect=AssertionError('writer replay')) as writer, \
                     patch.object(self.entry, 'authorize', side_effect=AssertionError('approval replay')) as approval, \
                     patch.object(self.m, 'human_outcome', wraps=self.m.human_outcome,
                                  side_effect=RuntimeError('renderer unavailable')
                                  if defect == 'lookup_and_renderer_failure' else None) as renderer:
                    result = self.reply(action=self.request['request']['task'])
                writer.assert_not_called()
                approval.assert_not_called()
                renderer.assert_not_called()
                for field in ('RECOVERY: UNKNOWN', 'REPORTING: FAILED', 'CHANGES: UNKNOWN',
                              'VALIDATION: UNKNOWN', 'earlier action may have changed files',
                              'No action was repeated', 'responsible human', 'STOP'):
                    self.assertIn(field, result['text'])
                self.assertNotIn('CHANGES: None', result['text'])
                self.assertNotIn('RECOVERY: SUCCEEDED', result['text'])
                self.assertEqual('BLOCKED', result['status'])
                self.assertEqual('STOP', result['action'])
                self.assertEqual('DECISION_ALREADY_CONSUMED', result['reason'])
                self.assertEqual(str(reference), result['reference'])
                self.assertEqual(self.request['request']['operation_reference'], result['operation_reference'])
                if defect not in ('empty_reference', 'unreadable_reference', 'missing_reference', 'lookup_and_renderer_failure'):
                    self.assertEqual(str(claim), result['claim'])
                self.assertEqual(before, (self.m.snapshot(self.root), self.m.snapshot(self.ledger)))

    def test_outcome_boundary_no_execution_rejection_and_audited_reentry(self):
        for situation in ('no_execution', 'rejection', 'audited_reentry'):
            with self.subTest(situation=situation):
                self.setUp()
                if situation != 'no_execution':
                    self.review()
                if situation == 'rejection':
                    rejected = self.reply('Reject.')
                    self.assertIn('CHANGES: None', rejected['text'])
                if situation == 'audited_reentry':
                    completed = self.reply()
                    self.entry.audit(completed['claim'])
                    self.assertEqual('RECOVERY_VALIDATED', completed['recovery_status'])
                    self.assertIn('REPORTING: SUCCEEDED', completed['text'])
                    self.assertIn('Recovery completed and validated', completed['text'])
                    self.assertNotEqual(self.before, self.m.snapshot(self.root))
                before = self.m.snapshot(self.root), self.m.snapshot(self.ledger)
                self.reenter()
                with patch.object(self.entry, 'execute', side_effect=AssertionError('unauthorized writer')) as writer, \
                     patch.object(self.entry, 'authorize', side_effect=AssertionError('unauthorized approval')) as approval:
                    result = self.reply()
                writer.assert_not_called()
                approval.assert_not_called()
                self.assertEqual('STOP', result['action'])
                self.assertEqual('BLOCKED', result['status'])
                self.assertIn('STOP', result['text'])
                if situation == 'audited_reentry':
                    self.assertEqual('RECOVERY_VALIDATED', result['recovery_status'])
                    self.assertEqual(completed['claim'], result['claim'])
                    self.assertIn('RECOVERY: SUCCEEDED', result['text'])
                    self.assertIn('REPORTING: SUCCEEDED', result['text'])
                else:
                    self.assertIn('No recovery', result['text'])
                    self.assertEqual(self.before, self.m.snapshot(self.root))
                    if situation == 'rejection':
                        self.assertIn('rejected', result['text'])
                self.assertEqual(before, (self.m.snapshot(self.root), self.m.snapshot(self.ledger)))

    def test_chat_shared_ordinary_contract_installed_for_all_roles(self):
        master = (self.root / '15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_MASTER.md').read_text(encoding='utf-8')
        for clause in ('Every role,', 'early STOP still requires a meaningful chat response',
                       'planning/intake', 'ordinary development', 'handoff/escalation',
                       'What actually happened', 'important verified findings',
                       'What remains unresolved', 'whether human input is needed',
                       'semantic requirements, not mandatory headings',
                       'returning a tool\'s JSON does not deliver a chat response',
                       'Deliver the human-facing chat response', 'await the actual human response'):
            self.assertIn(clause, master)
        # These are distributed prompt checks, not a claim that a model delivered chat.
        prompts = self.root / '15_COMMANDS_AND_DRIVERS'
        for prompt in prompts.glob('ACTION_PROMPT_*.md'):
            if prompt.name == 'ACTION_PROMPT_MASTER.md':
                continue
            self.assertIn('Atomic Handoff Dispatch', prompt.read_text(encoding='utf-8'), prompt.name)

class ModeAHumanInteraction(InteractionAcceptance, unittest.TestCase):
    mode = 'MODE_A_EXISTING_SOLUTION'
class ModeBHumanInteraction(InteractionAcceptance, unittest.TestCase):
    mode = 'MODE_B_REQUIREMENTS_ONLY'


def prepare_conversation_fixture(mode='MODE_B_REQUIREMENTS_ONLY'):
    """Test-only setup for a later real Codex conversation; never approves anything.

    The host loads session.json, reads the installed master, invokes the existing
    MaintenanceEntry.interact and delivers its findings in chat. No console relay.
    """
    case_type = {'MODE_A_EXISTING_SOLUTION': ModeAHumanInteraction,
                 'MODE_B_REQUIREMENTS_ONLY': ModeBHumanInteraction}[mode]
    case = case_type('test_A_F_I_approve_dual_capacity_new_session')
    case.setUp()
    session = case.root.parent / 'conversation-session.json'
    session.write_text(json.dumps({'evidence_class': 'TECHNICAL_TEST',
        'human_usability': 'NOT_TESTED', 'mode': mode, 'instance': str(case.root),
        'installation': case.host.record, 'ledger': str(case.ledger),
        'request': case.request, 'fixture_human': 'Synthetic Director',
        'notice': 'Simulated capacities authorize only this disposable fixture; no protected authority.'}, indent=2))
    return session


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
