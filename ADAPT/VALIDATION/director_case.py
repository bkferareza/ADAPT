"""Synthetic Director-initialization conformance and agent-guided file actions.

Validation asset only, not a shipped command, approval authenticator or generic
execution engine. Each CLI invocation exercises one documented stage then stops.
The caller must inspect its actual artifacts before invoking the next stage.
"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil

spec = importlib.util.spec_from_file_location('onboarding', Path(__file__).with_name('onboarding_case.py'))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
b = c.b
IDENTITY = c.IDENTITY
SCOPE = [IDENTITY, b.DEC]
DIRECTOR = c.DIRECTOR
DESIGNATION = 'synthetic-human-designation.json'
NEXT = 'Promote {{DOCUMENT}} as {{SOURCE_TRUTH_VERSION}}'
PINS = list(dict.fromkeys([*b.CONTRACTS, *c.PINS, '00_FRAMEWORK/ROLE_MODEL.md',
                          '15_COMMANDS_AND_DRIVERS/COMMAND_SYNTAX.md']))


def scaffold(base):
    b.DOCUMENT = b.DOCUMENT.replace('No product code, workcells, milestone acceptance or QA signoff.',
                                    'No product code, milestone acceptance or QA signoff. Governance onboarding with Gate 3 is permitted.')
    b.scaffold(base, 'MODE_A_EXISTING_SOLUTION', prepare_promotion=False)
    root = base / 'acceptance/ADAPT'
    b.need(c.metadata(b.read(root, IDENTITY), 'HUMAN_OWNER') == '{{DIRECTOR_IDENTITY}}', 'PREPOPULATED_DIRECTOR')
    b.need(not (root / b.APPROVAL).exists(), 'PREPOPULATED_GATE1')
    b.write(base, 'initial-unresolved.json', json.dumps({'state': b.state(root), 'identity': b.read(root, IDENTITY),
            'hashes': b.snapshot(root), 'notice': 'Actual scaffold completed before designation, Gate 1 or context input.'}, indent=2))


def supply_designation(base, root):
    """Original input fixture; synthetic provenance is assumed, never authenticated."""
    human = {'synthetic_fixture_only': True, 'origin': 'CURRENT_SYNTHETIC_HUMAN_INPUT',
             'designator': 'SYNTHETIC HUMAN OWNER', 'human_owner': DIRECTOR,
             'project': b.state(root)['ProjectName'], 'role': 'Director', 'lane': 'Director Lane',
             'designation_text': f'I explicitly designate {DIRECTOR} as the human Director for {b.state(root)["ProjectName"]}.',
             'reference': 'SYNTHETIC-HUMAN-DESIGNATION-001', 'ai_operator': 'Codex synthetic validation executor',
             'scope': SCOPE, 'notice': 'TEST FIXTURE ONLY: no real Human Owner designation or approval.'}
    b.write(base, DESIGNATION, json.dumps(human, indent=2) + '\n')
    basis = {'input_sha256': b.sha(base / DESIGNATION), 'before': {p: b.sha(root / p) for p in SCOPE},
             'control_plane_sha256': b.sha(root / b.CP), 'contracts': {p: b.sha(root / p) for p in PINS},
             'current_invocation': 'Run Director intake', 'executor': 'Director Lane', 'action': 'initial designation'}
    b.write(base, 'designation-basis.json', json.dumps(basis, indent=2) + '\n')
    return basis


def preflight(base, root, basis, command='Run Director intake', executor='Director Lane', planned=None):
    """Read-only mechanical checks for the fixed synthetic acceptance case."""
    b.need(command == basis['current_invocation'] == 'Run Director intake', 'REGISTERED_COMMAND')
    b.need('`Run Director intake`' in b.read(root, '15_COMMANDS_AND_DRIVERS/COMMAND_REGISTRY.md') and
           '| `Run Director intake` | Director Lane |' in b.read(root, '15_COMMANDS_AND_DRIVERS/COMMAND_ROUTING_MATRIX.md'), 'COMMAND_ROUTING')
    b.need('### Rule 1 — Commands Must Use Exact ADAPT Command Names' in b.read(root, '15_COMMANDS_AND_DRIVERS/COMMAND_SYNTAX.md'), 'COMMAND_SYNTAX')
    b.need('## Initial Director designation stage' in b.read(root, '15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_DIRECTOR.md'), 'MISSING_CONTRACT')
    b.need(basis['action'] == 'initial designation', 'QUALIFICATION_SCOPE')
    s = b.state(root)
    b.need(executor == basis['executor'] == s['CurrentAuthority'] == 'Director Lane', 'EXECUTOR_AUTHORITY')
    b.need(s['CurrentPhase'] == 'INITIALIZED' and s['SourceTruthVersion'] == 'NONE' and s['ExecutionReadiness'] == 'NEEDS_PLANNING', 'INITIAL_STATE')
    b.need(all(s[k] == 'NONE' for k in ['ActiveWorkcell', 'ActiveHandoff', 'ActiveMilestone', 'ActiveCycle']), 'ACTIVE_BINDING')
    b.need(s['Blocked'] == 'NO' and s['ActiveBlockers'] == 'NONE', 'SETUP_BLOCKED')
    b.need((root / 'STARTUP.md').is_file() and 'SCAFFOLDED; STOP' in b.read(root, 'STARTUP.md'), 'SCAFFOLD_INCOMPLETE')
    startup = json.loads(b.read(root, 'STARTUP.md').split('```json\n', 1)[1].split('\n```', 1)[0])
    b.need(startup['missing'] == [] and startup['status'] == 'SCAFFOLDED; STOP', 'SCAFFOLD_INCOMPLETE')
    b.need(all(b.sha(b.FRAMEWORK / p) == h for p, h in startup['frozen_source_hashes'].items()), 'SCAFFOLD_PROVENANCE')
    b.need(all((root / p).is_file() and b.sha(root / p) == h for p, h in basis['contracts'].items()), 'CONTRACT_BINDING')
    b.need(set(basis['contracts']) == set(PINS), 'CONTRACT_INVENTORY')
    for folder in ['03_WORKCELLS', '06_HANDOFFS/ACTIVE', '10_CONTEXT_ECONOMY/CONTEXT_PACKS']:
        b.need(not any(p.is_file() and p.name not in {'README.md', 'ROLE_WORKCELL_BLUEPRINTS.md'} for p in (root / folder).rglob('*')), 'ACTIVE_ARTIFACT')
    for path in root.rglob('*.md'):
        rel = path.relative_to(root).as_posix()
        if rel.startswith(('00_FRAMEWORK/', '07_GUARDRAILS/', '08_TEMPLATES/', '15_COMMANDS_AND_DRIVERS/', 'TOOLS/')):
            continue
        text = b.read(root, rel)
        b.need(not re.search(r'^\| SOURCE_TRUTH_V\d', b.real_rows(path), re.M), 'PROMOTION_HISTORY')
        b.need('DIRECTOR_DESIGNATION:' not in text and 'BOOTSTRAP_ATTEMPT:' not in text, 'DESIGNATION_HISTORY')
        if path.name == 'WORKCELL_REGISTRY.md':
            b.need(not re.search(r'^\| [A-Z]+_[A-Z0-9]+ \|', b.real_rows(path), re.M), 'WORKCELL_HISTORY')
    b.need((root / IDENTITY).is_file(), 'DIRECTOR_MISSING')
    text = b.read(root, IDENTITY)
    b.need(c.metadata(text, 'PROJECT') == s['ProjectName'] and c.metadata(text, 'ROLE') == 'Director' and c.metadata(text, 'WORKCELL_TYPE') == 'Director Lane', 'DIRECTOR_SCHEMA')
    b.need(c.metadata(text, 'HUMAN_OWNER') == '{{DIRECTOR_IDENTITY}}', 'DIRECTOR_ALREADY_SET_OR_CONFLICT')
    b.need('{{' not in text.replace('{{DIRECTOR_IDENTITY}}', '', 1), 'UNRESOLVED_IDENTITY')
    b.need((base / DESIGNATION).is_file(), 'MISSING_DESIGNATION')
    b.need(b.sha(base / DESIGNATION) == basis['input_sha256'], 'DESIGNATION_HASH')
    d = c.data(base, DESIGNATION)
    b.need(d.get('synthetic_fixture_only') is True, 'SYNTHETIC_LABEL')
    b.need(d.get('origin') == 'CURRENT_SYNTHETIC_HUMAN_INPUT' and d.get('designator') == 'SYNTHETIC HUMAN OWNER', 'HUMAN_INPUT_REQUIRED')
    owner = d.get('human_owner', '')
    b.need(owner == DIRECTOR and '{{' not in owner and '\n' not in owner and '|' not in owner, 'HUMAN_DESIGNATION')
    b.need(d.get('project') == s['ProjectName'] and d.get('role') == 'Director' and d.get('lane') == 'Director Lane', 'DESIGNATION_CONFLICT')
    b.need(d.get('reference') == 'SYNTHETIC-HUMAN-DESIGNATION-001' and d.get('designation_text') == f'I explicitly designate {DIRECTOR} as the human Director for {s["ProjectName"]}.', 'DESIGNATION_UNTRACED')
    b.need(set(d.get('scope', [])) == set(SCOPE) and set(planned if planned is not None else SCOPE) == set(SCOPE), 'MUTATION_BOUNDARY')
    b.need(all(b.sha(root / p) == h for p, h in basis['before'].items()) and b.sha(root / b.CP) == basis['control_plane_sha256'], 'BEFORE_CHANGED')
    return d


def designate(base, root, basis):
    d = preflight(base, root, basis)
    before = b.snapshot(root)
    shutil.copytree(root, base / 'before-designate')
    original_identity = (root / IDENTITY).read_bytes()
    original_decision = (root / b.DEC).read_bytes()
    result_identity = original_identity.replace(b'HUMAN_OWNER: {{DIRECTOR_IDENTITY}}', ('HUMAN_OWNER: ' + DIRECTOR).encode(), 1)
    b.need(result_identity != original_identity and result_identity.replace(('HUMAN_OWNER: ' + DIRECTOR).encode(), b'HUMAN_OWNER: {{DIRECTOR_IDENTITY}}', 1) == original_identity, 'IDENTITY_DIFFERENCE')
    decision_id = b.next_decision_id(root)
    evidence = {'synthetic_fixture_only': True, 'original_input': str(base / DESIGNATION), 'input_sha256': basis['input_sha256'],
                'designation_text': d['designation_text'], 'designation_reference': d['reference'], 'ai_operator': d['ai_operator'],
                'command': 'Run Director intake', 'project': d['project'], 'role': 'Director', 'lane': 'Director Lane',
                'state_before_and_after': b.state(root), 'allowed_writes': SCOPE, 'before_hashes': basis['before'],
                'identity_after_sha256': hashlib.sha256(result_identity).hexdigest(), 'contract_hashes': basis['contracts'],
                'history': 'Full retained instance markdown and live registers checked: no promotion, designation, workcell, context or active handoff; scaffold startup provenance verified.',
                'job_size': 'S: bounded identity and one decision record; minimum setup evidence, no ordinary pack',
                'guardrails': 'Context uses explicit minimum setup basis; mutation exact two-file scope; handoff uses human completion qualification; routing PROTECTED_DEFAULT preserved; no contract/product/QA actions.',
                'stage_attempts': {str(i): {'attempts': 1, 'result': 'COMPLETE under Initial Director designation stage'} for i in range(1, 14)},
                'identity_delta': 'HUMAN_OWNER placeholder replaced only; decision row appended; control plane unchanged; no CP/CD/handoff/workcell created.',
                'next_registered_action': NEXT, 'gate1_approved': False, 'completion': 'Human completion only; STOP. Qualification consumed; all ordinary requirements remain.'}
    cells = [decision_id, 'Initial human Director designation', 'Post-scaffold accountability only',
             d['designator'] + ' explicitly designates ' + DIRECTOR,
             datetime.now(timezone(timedelta(hours=8))).isoformat(), IDENTITY, 'No inferred identity or workcell onboarding', 'ACTIVE',
             'DIRECTOR_DESIGNATION: ' + d['reference'] + '; SourceTruthVersion NONE; ' + json.dumps(evidence, separators=(',', ':'))]
    row = ('| ' + ' | '.join(cells) + ' |\n').encode()
    b.need(original_decision.count(b'<!-- EXAMPLE:') == 1, 'DECISION_SCHEMA')
    offset = original_decision.index(b'<!-- EXAMPLE:')
    result_decision = original_decision[:offset] + row + original_decision[offset:]
    b.need(result_decision.replace(row, b'', 1) == original_decision, 'APPEND_ONLY')
    preflight(base, root, basis)  # Recheck actual inputs and bytes immediately before writing.
    (root / IDENTITY).write_bytes(result_identity)
    (root / b.DEC).write_bytes(result_decision)
    after = b.snapshot(root)
    changed = {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
    b.need(changed == set(SCOPE), 'ACTUAL_MUTATION_BOUNDARY')
    b.need((root / b.CP).read_bytes() == (base / 'before-designate' / b.CP).read_bytes(), 'CONTROL_MUTATION')
    b.checkpoint(base, root, 'designate', before)
    b.write(base, 'designation-result.json', json.dumps({'status': 'DIRECTOR_IDENTITY_INITIALIZED', 'decision_id': decision_id,
            'input_sha256': basis['input_sha256'], 'next_action': NEXT, 'state': b.state(root),
            'identity_reverse_verified': True, 'decision_inverse_verified': True, 'changed': sorted(changed),
            'fixture_notice': 'Synthetic test only; not a real designation or human approval.'}, indent=2))
    b.cli(base, root, 'state'); b.cli(base, root, 'doctor'); b.cli(base, root, 'prompt', 'next', expected=1)
    print('PASS_DIRECTOR_DESIGNATION; STOP')


def promotion_inputs(base, root):
    b.need(c.metadata(b.read(root, IDENTITY), 'HUMAN_OWNER') == DIRECTOR, 'DIRECTOR_UNRESOLVED')
    identity_hash = b.sha(root / IDENTITY)
    basis = b.inputs(root, populate_director=False)
    b.need(b.sha(root / IDENTITY) == identity_hash, 'PROMOTION_INPUT_CHANGED_DIRECTOR')
    b.write(base, 'basis.json', json.dumps(basis, indent=2))
    print('SYNTHETIC_GATE1_INPUT_READY; no promotion executed')


def verify(base, root):
    t = c.target(1)
    b.need(c.quality(root, t) == 'PASS_WORKCELL_QUALITY', 'WORKCELL_QUALITY')
    b.need(len(list((root / t['folder']).iterdir())) == 15, 'WORKCELL_FILE_COUNT')
    b.need(b.state(root)['SourceTruthVersion'] == b.VERSION, 'PROMOTION_RESULT')
    b.need(c.metadata(b.read(root, IDENTITY), 'HUMAN_OWNER') == DIRECTOR, 'IDENTITY_RESULT')
    decisions = re.findall(r'^\| (DEC-\d+) \|', b.read(root, b.DEC), re.M)
    b.need(len(decisions) == len(set(decisions)) == 3, 'DECISION_HISTORY_PRESERVED')
    b.need(b.snapshot(base / 'project') == c.data(base, 'project-before.json'), 'PRODUCT_MUTATION')
    before = b.snapshot(root)
    stops = []
    for name, check in [('implementation-without-assignment', lambda: c.implementation(root, t)),
                        ('initialization-qualification-reuse', lambda: preflight(base, root, c.data(base, 'designation-basis.json')))]:
        try: check()
        except b.Stop as exc: stops.append({'case': name, 'result': 'STOP_REQUIRED', 'reason': str(exc)})
        else: raise AssertionError('Missing ordinary stop: ' + name)
    b.need(b.snapshot(root) == before, 'ORDINARY_CHECK_MUTATED')
    save = {'status': 'PASS_ACTUAL_DISPOSABLE_SEQUENCE', 'classification': 'Agent-guided documented file actions, not independent QA or human-approval authentication',
            'initial_director_unresolved': True, 'registered_entry': 'Run Director intake', 'designation': c.data(base, 'designation-result.json'),
            'first_promotion': 'Registered SOURCE_TRUTH_V0.1 through bounded initial basis', 'first_context': b.PACK,
            'first_workcell': {'id': t['id'], 'files': c.files(t), 'all_15_present': True, 'no_implementation_assignment': True},
            'unique_decisions': decisions, 'ordinary_stop_checks': stops, 'project_unchanged': True,
            'final_state': b.state(root), 'final_instance_hashes': b.snapshot(root)}
    b.write(base, 'acceptance-result.json', json.dumps(save, indent=2))
    print('PASS_ACTUAL_DISPOSABLE_SEQUENCE; STOP')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage', choices=['scaffold', 'designation-input', 'designate', 'promotion-input', 'promote', 'first-context', 'onboarding-input', 'onboarding-context', 'onboarding-route', 'onboard', 'verify'])
    p.add_argument('--disposable', type=Path, required=True)
    args = p.parse_args(); base = args.disposable.resolve()
    local = b.FRAMEWORK.parent / '.adapt-local'
    b.need(base.is_relative_to(local) and base.is_dir(), 'WORKSPACE_LOCAL_DISPOSABLE_REQUIRED')
    root = base / 'acceptance/ADAPT'
    if args.stage == 'scaffold': scaffold(base)
    elif args.stage == 'designation-input': supply_designation(base, root)
    elif args.stage == 'designate': designate(base, root, c.data(base, 'designation-basis.json'))
    elif args.stage == 'promotion-input': promotion_inputs(base, root)
    elif args.stage == 'promote': b.promote(base, root, c.data(base, 'basis.json'))
    elif args.stage == 'first-context': b.context(base, root, c.data(base, 'basis.json'))
    elif args.stage == 'onboarding-input': c.fixture_inputs(base, root, 1)
    elif args.stage == 'onboarding-context': c.context(base, root, 1)
    elif args.stage == 'onboarding-route': c.route_fixture(root, 1)
    elif args.stage == 'onboard': c.onboard(base, root, 1)
    elif args.stage == 'verify': verify(base, root)
