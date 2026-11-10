"""Prospective continuity acceptance; every approval/release here is simulated.

The installed fixture runtime's VERSION is varied only in memory to model older
and future qualified releases. This does not widen any production version gate.
"""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import unittest
import uuid
from unittest.mock import patch

from fixtures import FRAMEWORK, framework_version
import test_recovery_operational as existing


class ContinuityCases:
    setUp = existing.OperationalAcceptance.setUp
    structural_request = existing.OperationalAcceptance.structural_request

    def context_request(self):
        # Each subsequent action gets fresh input evidence. Never overwrite the
        # original completed action's external records in these fixtures.
        if hasattr(self, 'ledger') and list(self.ledger.glob('*/*.claim.json')):
            external = self.root.parent / ('next-inputs-' + uuid.uuid4().hex)
            external.mkdir()
            for path in self.f.external.glob('*.json'):
                shutil.copyfile(path, external / path.name)
            self.f.external = self.a.external = self.external = external
            failure = deepcopy(self.f.records['failure'])
            failure['state'] = self.m.op.state(self.root)
            self.f.evidence('failure', failure)
        return existing.OperationalAcceptance.context_request(self)

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value if isinstance(value, bytes) else self.m.rt._encoded(value))
        return self.ref(path)

    def ref(self, path):
        return {'path': str(path.resolve()), 'sha256': self.m.pre.digest(path.read_bytes())}

    def version(self, version):
        self.m.VERSION = version
        self.host.record['version'] = version
        p = self.root / self.m.pre.GOVERNANCE
        text = p.read_text(encoding='utf-8')
        import re
        p.write_text(re.sub(r'^VERSION: .*$', 'VERSION: ' + version, text, flags=re.M), encoding='utf-8')
        self.host.record['installed_hashes'][self.m.pre.GOVERNANCE] = self.m.pre.digest(p.read_bytes())

    def complete(self, request):
        plan = self.entry.preview(request)
        result = self.entry.execute(plan)
        self.assertEqual('TECHNICAL_EXECUTION_ACCEPTED', result['status'], result)
        self.assertEqual('TECHNICAL_EXECUTION_ACCEPTED', self.entry.audit(result['claim'])['status'])
        return result

    def begin(self):
        self.version('ADAPT-FW-0005')
        result = self.complete(self.structural_request())
        self.original = result
        self.old = self.m.snapshot(self.ledger)
        return result

    def adoption(self, to_version):
        """Emit the same existing review/installation record shapes as adoption."""
        m = self.m
        e = self.root.parent / ('simulated-adoption-' + uuid.uuid4().hex)
        operation, source = e / 'operation', e / 'issued-source'
        backup = e / 'backup'
        shutil.copytree(self.root, backup)
        before = m.snapshot(self.root)
        manifest = json.loads((self.root / 'TOOLS/MANIFEST.json').read_bytes())
        for ref in ['TOOLS/' + p for p in manifest['files']] + list(manifest['instance_files']):
            self.write(source / 'ADAPT' / ref, (self.root / ref).read_bytes())
        manifest['release_framework_version'] = to_version
        self.write(source / 'ADAPT/TOOLS/MANIFEST.json', manifest)
        self.write(source / 'ADAPT/CANONICAL_STARTERS' / m.pre.GOVERNANCE,
                   (FRAMEWORK / 'CANONICAL_STARTERS' / m.pre.GOVERNANCE).read_bytes())
        from_version = self.host.record['version']
        self.version(to_version)
        self.write(self.root / 'TOOLS/MANIFEST.json', manifest)
        decision = 'DEC-' + str(int(to_version[9:])).zfill(3)
        row = ('| ' + decision + ' | Simulated adoption ' + to_version +
               ' | Engineering only | Synthetic Maintainer | 2026-11-09 | Framework | None | ACTIVE | No real authority |\n').encode()
        decision_path = self.root / '02_DIRECTOR_LANE/DECISION_LOG.md'
        data = decision_path.read_bytes()
        # Append in the existing table, before the Status Values section.
        data = data.replace(b'\n## Status Values', row + b'\n## Status Values')
        self.write(decision_path, data)
        changes = []
        for ref in (m.pre.GOVERNANCE, 'TOOLS/MANIFEST.json', '02_DIRECTOR_LANE/DECISION_LOG.md'):
            old, new = (backup / ref).read_bytes(), (self.root / ref).read_bytes()
            self.write(operation / 'actual-before-images' / ref, old)
            self.write(operation / 'actual-after-images' / ref, new)
            self.write(e / 'after-images' / ref, new)
            change = {'path': ref, 'operation': 'replace', 'before_sha256': m.pre.digest(old),
                      'after_sha256': m.pre.digest(new), 'after_image': 'after-images/' + ref}
            changes.append(change)
            self.write(operation / f'intent-{len(changes):02d}.json', change)
            self.write(operation / f'completion-{len(changes):02d}.json', dict(change, status='PASS',
                       actual_before_sha256=change['before_sha256'], actual_after_sha256=change['after_sha256']))
        revision = {'commit': 'a' * 40, 'tag': to_version, 'version': to_version}
        release = {'id': 1, 'tag_name': to_version, 'target_commitish': 'a' * 40,
                   'draft': False, 'prerelease': False, 'simulated': True}
        plan = {'review_id': e.name, 'review_revision': 'SIMULATED', 'target': str(self.root),
                'source': {'commit': 'a' * 40, 'tag': to_version, 'release_id': 1},
                'changes': changes, 'decision_id': decision}
        refs = {}
        for key, name, value in [('plan', 'adoption-plan.json', plan),
                                  ('decision_row', 'PROPOSED_DECISION_ROW.md', row),
                                  ('source_inventory', 'issued-source-inventory.json', m.snapshot(source)),
                                  ('source_revision', 'issued-source-revision.json', revision),
                                  ('release', 'official-release-verification.json', release)]:
            refs[key] = self.write(e / name, value)
        bound = {Path(ref['path']).name: ref['sha256'] for ref in refs.values()}
        fingerprint = m.assembly.fingerprint(bound)
        scope = [c['path'] for c in changes]
        refs['review'] = self.write(e / 'ADOPTION_REVIEW.json', {'review_id': e.name,
            'review_revision': 'SIMULATED', 'fingerprint': fingerprint, 'bound_artifacts': bound, 'scope_paths': scope})
        response = 'Simulated explicit approval for this exact adoption'
        refs['response'] = self.write(e / 'ORIGINAL_HUMAN_RESPONSE.txt', response.encode())
        refs['approval'] = self.write(e / 'HUMAN_ADOPTION_DECISION.json', {'decision': 'APPROVED',
            'capacity': 'Human Framework Maintainer', 'human_response_verbatim': response,
            'source_reference': 'SIMULATED TEST RESPONSE', 'fingerprint': fingerprint,
            'review_id': e.name, 'review_revision': 'SIMULATED', 'scope_paths': scope})
        for key, name, value in [
            ('before_inventory', 'before-inventory.json', before),
            ('after_inventory', 'after-inventory.json', m.snapshot(self.root)),
            ('intent', 'INTENT.json', {'status': 'AUTHORIZED_ONE_SHOT', 'fingerprint': fingerprint, 'changes': changes}),
            ('completion', 'COMPLETION.json', {'status': 'COMPLETED', 'fingerprint': fingerprint,
                'installation_validation': 'PASS', 'issued_framework': to_version, 'commit': 'a' * 40,
                'failures': 0, 'errors': 0, 'adoption_decision': decision}),
            ('validation', 'INSTALLATION_VALIDATION.json', {'status': 'PASS'}),
            ('distribution', 'distribution-verification.json', {'verified': True,
                'files': manifest['files'], 'instance_files': manifest['instance_files']})]:
            refs[key] = self.write(operation / name, value)
        index = dict(refs, target=deepcopy(self.host.scope['target']), ledger=str(self.ledger),
                     from_version=from_version, to_version=to_version, inventory_prefix='',
                     backup_root=str(backup), operation_root=str(operation), source_root=str(source))
        reference = self.write(e / 'transition-index.json', index)
        self.host.record.setdefault('framework_transitions', []).append(reference)
        # This represents separately completed installation, never recovery approval.
        for ref in self.host.record['installed_hashes']:
            self.host.record['installed_hashes'][ref] = m.pre.digest((self.root / ref).read_bytes())
        return index, reference

    def next_plan(self):
        self.request = self.context_request()
        return self.entry.preview(self.request)

    def assert_history_unchanged(self):
        current = self.m.snapshot(self.ledger)
        self.assertTrue(all(current.get(p) == h for p, h in self.old.items()))

    def test_one_adoption_historical_audit_and_next_action(self):
        first = self.begin()
        self.adoption(framework_version())
        historical = self.entry.audit_historical(first['claim'])
        self.assertFalse(historical['current_state_checked'])
        self.assertFalse(historical['operational_authority'])
        self.assertTrue(self.entry.audit(first['claim'])['current_state_checked'])
        self.complete(self.context_request())
        self.assert_history_unchanged()

    def test_two_successive_upgrades(self):
        self.begin()
        self.adoption('ADAPT-FW-0006')
        self.adoption(framework_version())
        self.complete(self.context_request())
        self.assert_history_unchanged()

    def test_recovery_between_upgrades(self):
        # Seed both pre-existing structural defects before the first claim.
        # Later recovery never introduces an unexplained instance mutation.
        existing.OperationalAcceptance.index_request(self)
        self.begin()
        self.adoption('ADAPT-FW-0006')
        binding = deepcopy(self.request['request'])
        binding.update(inputs=[{'path': p, 'sha256': h, 'verified_at': self.host.template['checked_at']}
                               for p, h in self.m.snapshot(self.root).items()],
                       writes=[{'path': self.m.pre.INDEX, 'operation': 'set_fields', 'fields': ['placement'],
                                'before_sha256': self.m.pre.digest((self.root / self.m.pre.INDEX).read_bytes())}],
                       ids={'register': 'CONTEXT_INDEX', 'operation': 'NORMALIZE_TABLE_PLACEMENT'},
                       operation_reference='SIMULATED-INDEX-' + uuid.uuid4().hex,
                       completion={'expected': 'Placement only; preserve every row; STOP'})
        self.complete({'kind': 'STRUCTURAL', 'request': binding, 'parameters': deepcopy(binding['ids']),
                       'evidence_root': str(self.external)})
        self.host.record['framework_transitions'] = []
        self.adoption(framework_version())
        self.f.packet['ids']['CP'] = 'CP-092'
        self.complete(self.context_request())
        self.assert_history_unchanged()

    def test_unauthorized_extra_mutation(self):
        self.begin(); self.adoption(framework_version())
        self.write(self.root / 'unapproved.txt', b'not part of adoption')
        before = self.m.snapshot(self.ledger)
        result = self.entry.execute(self.next_plan())
        self.assertEqual('REFUSED', result['status'], result)
        self.assertEqual(before, self.m.snapshot(self.ledger))
        self.assert_history_unchanged()

    def test_each_missing_or_corrupt_evidence(self):
        self.begin(); index, reference = self.adoption(framework_version())
        # Exercise every evidence class plus representative captured images,
        # backup and issued payload; avoid repeating the same hash check for
        # every unchanged file in a full inventory.
        dependencies = {}
        self.m.framework_transition(reference, self.host.scope['target'], self.ledger, dependencies)
        selected = {reference['path'].replace('\\', '/').casefold()}
        selected |= {ref['path'].replace('\\', '/').casefold() for ref in index.values()
                     if isinstance(ref, dict) and set(ref) == {'path', 'sha256'}}
        for folder, ref in [('backup_root', self.m.pre.GOVERNANCE),
                            ('source_root', 'ADAPT/CANONICAL_STARTERS/' + self.m.pre.GOVERNANCE),
                            ('operation_root', 'actual-before-images/' + self.m.pre.GOVERNANCE),
                            ('operation_root', 'actual-after-images/' + self.m.pre.GOVERNANCE),
                            ('operation_root', 'intent-01.json'), ('operation_root', 'completion-01.json')]:
            selected.add((Path(index[folder]) / ref).as_posix().casefold())
        for name in sorted(selected):
            path = Path(name); original = path.read_bytes()
            with self.subTest(path=name, fault='corrupt'):
                path.write_bytes(original + b'corrupt')
                with self.assertRaises(Exception):
                    self.m.framework_transition(reference, self.host.scope['target'], self.ledger)
                path.write_bytes(original)
            with self.subTest(path=name, fault='missing'):
                held = path.with_name(path.name + '.held')
                path.rename(held)
                try:
                    with self.assertRaises(Exception):
                        self.m.framework_transition(reference, self.host.scope['target'], self.ledger)
                finally:
                    held.rename(path)
        self.assert_history_unchanged()

    def test_wrong_target_ledger_duplicate_reorder_and_chain(self):
        self.begin(); self.adoption('ADAPT-FW-0006'); index, reference = self.adoption(framework_version())
        refs = deepcopy(self.host.record['framework_transitions'])
        for bad in ([refs[1], refs[0]], [refs[0], refs[0], refs[1]], [refs[1]], [refs[0]]):
            with self.subTest(chain=bad):
                self.host.record['framework_transitions'] = bad
                try:
                    result = self.entry.execute(self.next_plan())
                    self.assertEqual('REFUSED', result['status'], result)
                except ValueError:
                    pass
        self.host.record['framework_transitions'] = refs
        p = Path(reference['path']); original = p.read_bytes()
        for key, value in [('ledger', str(self.ledger.parent)), ('target', dict(index['target'], identity='Wrong')),
                           ('from_version', 'ADAPT-FW-0004'), ('to_version', 'ADAPT-FW-0005')]:
            with self.subTest(field=key):
                bad = deepcopy(index); bad[key] = value
                self.host.record['framework_transitions'][-1] = self.write(p, bad)
                with self.assertRaises(Exception): self.next_plan()
        p.write_bytes(original)
        self.host.record['framework_transitions'] = refs
        self.assert_history_unchanged()

    def test_interrupted_recovery_cannot_be_bypassed(self):
        self.version('ADAPT-FW-0005')
        plan = self.entry.preview(self.structural_request())
        def interrupt(event, sequence):
            if event == 'after_replace': raise ValueError('SIMULATED INTERRUPTION')
        with patch.object(self.m, '_checkpoint', side_effect=interrupt): result = self.entry.execute(plan)
        self.assertEqual('INTERRUPTED', result['status'])
        self.adoption(framework_version())
        before = self.m.snapshot(self.ledger)
        result = self.entry.execute(self.next_plan())
        self.assertEqual('REFUSED', result['status'], result)
        self.assertEqual(before, self.m.snapshot(self.ledger))

    def test_operation_reference_and_claim_replay(self):
        self.begin(); self.adoption(framework_version())
        request = self.context_request()
        claim = json.loads(Path(self.original['claim']).read_bytes())
        request['request']['operation_reference'] = claim['plan']['request']['request']['operation_reference']
        result = self.entry.execute(self.entry.preview(request))
        self.assertEqual('REFUSED', result['status'], result)
        # Replaying the completed original plan is also refused before ownership.
        result = self.entry.execute(claim['plan'])
        self.assertEqual('REFUSED', result['status'], result)
        self.assert_history_unchanged()

    def test_new_action_requires_both_approvals(self):
        self.begin(); self.adoption(framework_version())
        plan = self.next_plan()
        def remove(auth):
            auth['human_authorization']['approvals'].pop()
            return auth
        self.host.alter = remove
        result = self.entry.execute(plan)
        self.assertEqual('REFUSED', result['status'], result)
        self.assert_history_unchanged()

    def test_evidence_changes_after_review_or_during_write(self):
        self.begin(); index, _ = self.adoption(framework_version())
        plan = self.next_plan(); path = Path(index['response']['path']); original = path.read_bytes()
        path.write_bytes(b'Changed response')
        self.assertEqual('REFUSED', self.entry.execute(plan)['status'])
        path.write_bytes(original)
        def change(event, sequence):
            if event == 'after_intent': path.write_bytes(b'Changed while writing')
        with patch.object(self.m, '_checkpoint', side_effect=change): result = self.entry.execute(plan)
        self.assertEqual('INTERRUPTED', result['status'], result)
        self.assert_history_unchanged()

    def test_extra_evidence_file_during_write(self):
        self.begin(); index, _ = self.adoption(framework_version())
        plan = self.next_plan()
        def change(event, sequence):
            if event == 'after_intent':
                (Path(index['backup_root']) / 'unreviewed.txt').write_bytes(b'extra evidence')
        with patch.object(self.m, '_checkpoint', side_effect=change): result = self.entry.execute(plan)
        self.assertEqual('INTERRUPTED', result['status'], result)
        self.assert_history_unchanged()

    def test_semantically_mismatched_evidence_even_with_fresh_reference_hash(self):
        self.begin(); index, reference = self.adoption(framework_version())
        p = Path(reference['path']); original_index = p.read_bytes()
        for key, field, value in [('approval', 'decision', 'REJECTED'),
                                  ('approval', 'capacity', 'Human Director'),
                                  ('completion', 'status', 'INTERRUPTED'),
                                  ('completion', 'fingerprint', 'wrong review'),
                                  ('validation', 'status', 'FAIL'),
                                  ('distribution', 'verified', False),
                                  ('release', 'draft', True),
                                  ('source_revision', 'version', 'ADAPT-FW-0004'),
                                  ('after_inventory', 'unapproved.txt', '0' * 64)]:
            with self.subTest(key=key, field=field):
                path = Path(index[key]['path']); original = path.read_bytes()
                bad = json.loads(original); bad[field] = value
                changed_index = deepcopy(index); changed_index[key] = self.write(path, bad)
                changed_ref = self.write(p, changed_index)
                try:
                    with self.assertRaises(Exception):
                        self.m.framework_transition(changed_ref, self.host.scope['target'], self.ledger)
                finally:
                    path.write_bytes(original); p.write_bytes(original_index)
        self.assert_history_unchanged()

    def test_old_claim_corruption_and_missing_transition_refuse(self):
        self.begin(); self.adoption(framework_version())
        refs = self.host.record.pop('framework_transitions')
        result = self.entry.execute(self.next_plan())
        self.assertEqual('REFUSED', result['status'], result)
        self.host.record['framework_transitions'] = refs
        p = Path(self.original['journal']); p.write_bytes(p.read_bytes() + b'{}\n')
        result = self.entry.execute(self.next_plan())
        self.assertEqual('REFUSED', result['status'], result)


class ModeAContinuity(ContinuityCases, unittest.TestCase):
    mode = 'MODE_A_EXISTING_SOLUTION'


class ModeBContinuity(ContinuityCases, unittest.TestCase):
    mode = 'MODE_B_REQUIREMENTS_ONLY'
