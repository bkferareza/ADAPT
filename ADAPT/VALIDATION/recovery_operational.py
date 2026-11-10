"""Prospective FW-0006 HUMAN_SUPERVISED operational maintenance entry.

Human decisions arrive through the normal ADAPT interaction, separately from
packet data. MaintenanceEntry prepares the existing authorization evidence; the
interaction must capture an actual explicit human response. No independent human
authentication, protected account or malicious-agent resistance is claimed.

Local exclusive-create ownership and fsynced evidence; no network filesystems,
external concurrent writers, power-loss recovery, resume, retry or rollback.
Synthetic hosts exercise this identical writer but establish no human consent.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
import difflib
from pathlib import Path
import stat


def _load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


structural = _load('recovery_structural')
rt = structural.runtime
assembly, pre, op = rt.assembly, rt.pre, rt.op
supervised = _load('recovery_supervised')
VERSION = 'ADAPT-FW-0008'


def human_review(plan):
    structural = plan['request']['kind'] == 'STRUCTURAL'
    action = ('Repair the register table structure' if structural else
              'Prepare recovery-only context artifacts')
    return ('ISSUE: ' + ('The register table structure is invalid.' if structural else
            'Ordinary context cannot support the stopped action.') +
            '\nIMPACT: Ordinary execution remains blocked.\nRECOMMENDATION: ' + action +
            '.\nCHANGES: ' + str(len(plan['files'])) + ' file(s): ' +
            ', '.join(f['path'] for f in plan['files']) +
            ('. Row placement only; record contents and statuses stay unchanged.' if structural else
             '. Recovery artifacts only; ordinary context will not be activated.') +
            '\nRISK: A write may fail partway through; evidence will be preserved and execution stopped.'
            '\nThe existing blocker remains open.\nDECISION: APPROVE, REJECT or SHOW DETAILS.'
            '\nApproval requires the recorded Director and Framework Maintainer capacities;'
            ' one person holding both may approve once for both.'
            '\nDo you approve this exact action? Execution remains blocked until approval.'
            '\nReply here, or invoke the ordinary ADAPT entry again with your response. STOP.\n')


def human_outcome(result, plan=None, reporting_error=None):
    """Keep completed recovery distinct from a later reporting failure."""
    success = result.get('recovery_status') == 'RECOVERY_VALIDATED'
    status = 'SUCCEEDED' if success else ('PARTIAL' if result.get('status') == 'INTERRUPTED' else 'BLOCKED')
    reason = result.get('reason', 'Approval or prerequisites missing.')
    reason = {'HUMAN_APPROVAL_REFUSED': 'Required human approval is missing, withdrawn or invalid.',
              'PRECONDITION_OR_IO_FAILURE': 'An execution check or file operation failed; the exact cause is not established.'}.get(reason, reason)
    return ('STATUS: ' + status + '\nRECOVERY: ' + ('SUCCEEDED' if success else status) +
            '\nREPORTING: ' + ('FAILED' if reporting_error else 'SUCCEEDED') +
            '\nACTION: ' + (('Repair register structure' if plan['request']['kind'] == 'STRUCTURAL'
                              else 'Prepare recovery-only context artifacts') if plan else 'Bounded recovery') +
            '\nCHANGES: ' + (', '.join(f['path'] for f in plan['files']) if success and plan else
                              'Execution was interrupted; files may have changed. The exact completed write extent '
                              'has not been established; no unchanged-state claim is made.' if status == 'PARTIAL' else 'None.') +
            ('\nRESULT: Register rows are now in a readable contiguous table; record contents and statuses were preserved.'
             if success and plan and plan['request']['kind'] == 'STRUCTURAL' else
             '\nRESULT: Recovery-only context artifacts were prepared; ordinary context was not activated.'
             if success and plan else '') +
            '\nVALIDATION: ' + ('Recovery completed and validated.' if success else
                                  'Action stopped: ' + reason) +
            ('\nFinal reporting failed; the validated changes remain successful. Technical error evidence is preserved where available.' if reporting_error else '') +
            '\nREMAINING ISSUES: Existing blocker remains open; ordinary execution remains gated.' +
            '\nNEXT ACTION: ' + ('Review the reporting failure. No recovery retry is necessary.' if success and reporting_error else
                'Have the responsible human assess the interrupted writes and preserved evidence; do not retry or resume.' if status == 'PARTIAL' else
                'Request review of the next separate recovery action.' if success else 'Review the missing condition and preserved evidence.') +
            '\nAPPROVAL: A separate action requires its own applicable human decision. STOP.\n')


def reporting_fallback(outcome, error, *, reentry=False):
    """Report retained evidence without invoking the renderer or any writer.

    Outcome fields remain authoritative; reporting failure supplies no additional
    mutation or validation evidence. In particular, interruption can precede the
    writer's completion record even when replacement already changed bytes.
    """
    result = dict(outcome) if isinstance(outcome, dict) else {}
    recovery = result.get('recovery_status')
    recorded_validation = (isinstance(result.get('final_hashes'), dict) and bool(result['final_hashes']) and
                           all(result.get(key) for key in ('claim', 'claim_sha256', 'journal', 'journal_sha256')))
    validated = recovery == 'RECOVERY_VALIDATED' and recorded_validation
    status = ('SUCCEEDED' if validated else 'INTERRUPTED' if recovery == 'RECOVERY_INTERRUPTED'
              else 'REFUSED' if recovery == 'RECOVERY_REFUSED' else 'UNKNOWN')
    if validated:
        changes = 'The approved changes were completed.'
        validation = 'Recovery completed and validated.'
        explanation = ('The operation previously succeeded; its recorded validation passed. '
                       'The saved outcome remains authoritative. No recovery replay is necessary. '
                       if reentry else 'Recovery succeeded and passed validation. ')
        next_action = 'No recovery retry is necessary; do not retry recovery. Review the reporting failure.'
    else:
        changes = 'UNKNOWN. No unchanged-state claim is made.'
        validation = 'UNKNOWN; complete validation is not established by the available outcome.'
        explanation = ('The action may have partially changed the instance. The exact completed write extent '
                       'has not been established. ' if status == 'INTERRUPTED' else
                       'Recovery was refused. ' if status == 'REFUSED' else
                       ('ADAPT could not verify the previous operation because its saved execution '
                        'reference is incomplete or unreadable. The earlier action may have changed files. '
                        if reentry and not result.get('claim') else
                        'Available outcome evidence is missing or incomplete. The earlier action may have changed files. '))
        if reentry:
            explanation += ('No action was repeated. The operation remains stopped and its available '
                            'evidence must be inspected by the responsible human. ')
        next_action = ('Inspect the available evidence before any further action; '
                       'do not retry or resume, or automatically roll back.')
        if status == 'INTERRUPTED' and recorded_validation:
            changes = 'Writer-recorded final file hashes are available; recovery was interrupted.'
            validation = 'Recorded file validation passed; overall recovery was interrupted.'
    text = ('STATUS: ' + ('BLOCKED' if reentry else status) + '\nRECOVERY: ' + status +
            '\nREPORTING: FAILED\nCHANGES: ' + changes + '\nVALIDATION: ' + validation +
            '\n' + explanation + 'Reporting failed; the reporting renderer or check failed. '
            'Retained outcome evidence is not invalidated by reporting failure.' +
            '\nCLAIM: ' + str(result.get('claim', 'UNKNOWN')) +
            ('\nOPERATION: ' + str(result['operation_reference']) if 'operation_reference' in result else '') +
            ('\nREFERENCE: ' + str(result['reference']) if 'reference' in result else '') +
            '\nJOURNAL: ' + str(result.get('journal', 'Inspect the claim\'s recorded evidence directory.'
                                           if result.get('claim') else 'UNKNOWN')) +
            '\nREMAINING ISSUES: The existing blocker remains open; ordinary execution remains gated.' +
            '\nNEXT ACTION: ' + next_action +
            '\nAPPROVAL: A separate action requires its own applicable human decision. STOP.\n')
    result.update(reporting_status='FAILED', reporting_error=error, action='STOP', text=text)
    result.setdefault('status', 'BLOCKED')
    if reentry:
        result.update(status='BLOCKED', reason='DECISION_ALREADY_CONSUMED')
    return result


def need(condition, code):
    if not condition:
        raise ValueError(code)


def checked(value):
    path = Path(value)
    need(path.is_absolute() and path == path.resolve(), 'EXACT_PATH_REQUIRED')
    for entry in (path, *path.parents):
        if entry.exists() or entry.is_symlink():
            info = entry.lstat()
            need(not entry.is_symlink() and not getattr(info, 'st_file_attributes', 0) &
                 stat.FILE_ATTRIBUTE_REPARSE_POINT and
                 (not entry.is_file() or info.st_nlink == 1), 'ALIASED_PATH')
    return path


def snapshot(root):
    result = {}
    for path in sorted(checked(root).rglob('*')):
        checked(path)
        if path.is_file():
            ref = path.relative_to(root).as_posix()
            need(ref.casefold() not in {p.casefold() for p in result}, 'ALIASED_INVENTORY')
            result[ref] = pre.digest(path.read_bytes())
    return result


def file(root, ref):
    return checked(pre.safe(root, ref))


def framework_transition(reference, target, ledger, dependencies=None):
    """Read a hash-bound index of existing adoption evidence; never install.

    The index adds no approval authority. Original response, reviewed operations,
    issued bytes and completed installation must independently agree. All reads
    become exact plan dependencies, including backup and issued-source images.
    """
    dependencies = {} if dependencies is None else dependencies

    def read(path, digest=None):
        path = checked(path)
        need(not path.is_relative_to(checked(target['root'])) and
             not path.is_relative_to(checked(ledger)), 'TRANSITION_EVIDENCE_BOUNDARY')
        data = path.read_bytes()
        actual = pre.digest(data)
        need(digest is None or actual == digest, 'TRANSITION_EVIDENCE_CHANGED')
        key = path.as_posix().casefold()
        need(key not in dependencies or dependencies[key] == actual, 'TRANSITION_DEPENDENCY_CONFLICT')
        dependencies[key] = actual
        return data

    def record(ref):
        need(set(ref) == {'path', 'sha256'}, 'EXACT_TRANSITION_REFERENCE')
        return pre.load_json(read(ref['path'], ref['sha256']))

    index = record(reference)
    need(index['target'] == target and index['ledger'] == str(checked(ledger)), 'TRANSITION_TARGET_OR_LEDGER')
    review, approval, plan = (record(index[k]) for k in ('review', 'approval', 'plan'))
    bound = review['bound_artifacts']
    fingerprint = assembly.fingerprint(bound)
    need(review['fingerprint'] == approval['fingerprint'] == fingerprint and
         review['review_id'] == approval['review_id'] == plan['review_id'] and
         review['review_revision'] == approval['review_revision'] == plan['review_revision'],
         'TRANSITION_REVIEW_BINDING')
    review_root = checked(index['review']['path']).parent
    bound_paths = {}
    for ref, digest in bound.items():
        # Historical reviews may explicitly bind ../ evidence; resolve it once,
        # then apply the same alias, external-boundary and hash checks to it.
        path = checked((review_root / ref).resolve())
        need(str(path).casefold() not in bound_paths, 'ALIASED_TRANSITION_REVIEW')
        read(path, digest)
        bound_paths[str(path).casefold()] = digest
    need(bound_paths.get(str(checked(index['plan']['path'])).casefold()) == index['plan']['sha256'],
         'UNREVIEWED_TRANSITION_PLAN')
    response = read(index['response']['path'], index['response']['sha256']).decode('utf-8-sig')
    need(approval['decision'] == 'APPROVED' and approval['capacity'] == 'Human Framework Maintainer' and
         bool(approval['human_response_verbatim'].strip()) and
         response == approval['human_response_verbatim'] and bool(approval['source_reference'].strip()),
         'TRANSITION_HUMAN_APPROVAL')
    need(plan['target'] == target['root'] and set(approval['scope_paths']) == set(review['scope_paths']) ==
         {c['path'] for c in plan['changes']} and len(plan['changes']) == len(approval['scope_paths']),
         'TRANSITION_SCOPE')
    before, after = (record(index[k]) for k in ('before_inventory', 'after_inventory'))
    prefix = index['inventory_prefix']
    need(prefix in {'', 'ADAPT/'}, 'TRANSITION_INVENTORY_PREFIX')
    backup = checked(index['backup_root'])
    need(snapshot(backup) == before, 'TRANSITION_BACKUP_MISMATCH')
    for ref, digest in before.items():
        read(file(backup, ref), digest)
    # Validate complete inventory names, including paths not replaced.
    for inventory in (before, after):
        aliases = set()
        for ref, digest in inventory.items():
            path = file(backup, ref)
            need(ref == path.relative_to(backup).as_posix() and ref.casefold() not in aliases and
                 isinstance(digest, str) and len(digest) == 64, 'TRANSITION_INVENTORY_INVALID')
            aliases.add(ref.casefold())
    projected = dict(before)
    operation_root = checked(index['operation_root'])
    source_root = checked(index['source_root'])
    source_inventory, revision, release = (record(index[k]) for k in
                                         ('source_inventory', 'source_revision', 'release'))
    need(revision['version'] == index['to_version'] == release['tag_name'] ==
         plan['source']['tag'] and revision['commit'] == plan['source']['commit'] ==
         release['target_commitish'] and release['id'] == plan['source']['release_id'] and
         release.get('draft') is False and release.get('prerelease') is False,
         'TRANSITION_ISSUED_SOURCE')
    for key in ('source_inventory', 'source_revision', 'release'):
        need(bound_paths.get(str(checked(index[key]['path'])).casefold()) == index[key]['sha256'],
             'UNREVIEWED_ISSUED_SOURCE')
    need(snapshot(source_root) == source_inventory, 'TRANSITION_SOURCE_INVENTORY')
    for ref, digest in source_inventory.items():
        read(file(source_root, ref), digest)
    source_framework = file(source_root, 'ADAPT')
    source_manifest = pre.load_json(read(file(source_framework, 'TOOLS/MANIFEST.json')))
    need(source_manifest['release_framework_version'] == index['to_version'], 'TRANSITION_SOURCE_VERSION')
    for ref, digest in {**{'TOOLS/' + p: h for p, h in source_manifest['files'].items()},
                        **source_manifest['instance_files']}.items():
        need(pre.digest(read(file(source_framework, ref))) == digest, 'TRANSITION_SOURCE_MANIFEST')
    intent, completion, validation, distribution = (record(index[k]) for k in
                             ('intent', 'completion', 'validation', 'distribution'))
    need(intent['status'] == 'AUTHORIZED_ONE_SHOT' and intent['fingerprint'] == fingerprint and
         intent['changes'] == plan['changes'] and completion['status'] == 'COMPLETED' and
         completion['fingerprint'] == fingerprint and completion['installation_validation'] == 'PASS' and
         completion['issued_framework'] == index['to_version'] and
         completion['commit'] == revision['commit'] and completion['failures'] == 0 and
         completion['errors'] == 0 and validation['status'] == 'PASS' and
         distribution['verified'] is True and distribution['files'] == source_manifest['files'] and
         distribution['instance_files'] == source_manifest['instance_files'], 'TRANSITION_INCOMPLETE_INSTALLATION')
    images = {}
    for sequence, change in enumerate(plan['changes'], 1):
        ref = change['path']
        need(change['operation'] == 'replace' and projected.get(prefix + ref) == change['before_sha256'],
             'TRANSITION_BEFORE_IMAGE')
        old = read(file(operation_root / 'actual-before-images', ref), change['before_sha256'])
        new = read(file(operation_root / 'actual-after-images', ref), change['after_sha256'])
        need(read(file(review_root, change['after_image']), change['after_sha256']) == new,
             'TRANSITION_REVIEWED_IMAGE')
        one_intent = pre.load_json(read(file(operation_root, f'intent-{sequence:02d}.json')))
        done = pre.load_json(read(file(operation_root, f'completion-{sequence:02d}.json')))
        need(one_intent == change and done == dict(change, status='PASS',
             actual_before_sha256=change['before_sha256'], actual_after_sha256=change['after_sha256']),
             'TRANSITION_OPERATION_COMPLETION')
        need(pre.digest(old) == before[prefix + ref], 'TRANSITION_BACKUP_IMAGE')
        images[ref] = (old, new)
        if ref != '02_DIRECTOR_LANE/DECISION_LOG.md':
            canonical = ref.split('/')[0] in {'00_FRAMEWORK', '07_GUARDRAILS', '08_TEMPLATES',
                                              '15_COMMANDS_AND_DRIVERS'}
            need(canonical or ref == 'TOOLS/MANIFEST.json' or
                 ref in source_manifest['instance_files'] or
                 ref.removeprefix('TOOLS/') in source_manifest['files'] and ref.startswith('TOOLS/'),
                 'TRANSITION_NON_FRAMEWORK_WRITE')
            issued = read(file(source_framework, ('CANONICAL_STARTERS/' if canonical else '') + ref))
            def body(data):
                lines = data.decode('utf-8-sig').splitlines()
                for i in range(min(8, len(lines))):
                    if lines[i].partition(':')[0] in {'PROJECT', 'VERSION', 'INITIALIZED', 'LAST_UPDATED'}:
                        lines[i] = lines[i].partition(':')[0] + ': <instance header>'
                return lines
            need(body(new) == body(issued) if canonical else new == issued, 'TRANSITION_UNISSUED_IMAGE')
        projected[prefix + ref] = change['after_sha256']
    need(projected == after, 'TRANSITION_UNEXPLAINED_INVENTORY')
    decision = '02_DIRECTOR_LANE/DECISION_LOG.md'
    old, new = images[decision]
    row = read(index['decision_row']['path'], index['decision_row']['sha256'])
    need(bound_paths.get(str(checked(index['decision_row']['path'])).casefold()) == index['decision_row']['sha256']
         and row.startswith(b'| ' + plan['decision_id'].encode() + b' |') and row.endswith(b'\n') and
         len(row.splitlines()) == 1 and new.count(row) == 1 and new.replace(row, b'', 1) == old,
         'TRANSITION_DECISION_HISTORY')
    columns = ['DEC-ID', 'Decision', 'Rationale', 'Made By', 'Date', 'Affects',
               'Alternatives Considered', 'Status', 'Notes']
    prior_rows = op.table(old.decode('utf-8-sig'), 'Decisions', columns)
    final_rows = op.table(new.decode('utf-8-sig'), 'Decisions', columns)
    need(len(final_rows) == len(prior_rows) + 1 and
         [r for r in final_rows if r['DEC-ID'] != plan['decision_id']] == prior_rows and
         sum(r['DEC-ID'] == plan['decision_id'] for r in final_rows) == 1 and
         completion['adoption_decision'] == plan['decision_id'], 'TRANSITION_DECISION_BINDING')
    def version(data):
        return op.headers('\n'.join(data.decode('utf-8-sig').splitlines()), ['VERSION'])['VERSION']
    old_governance = read(file(backup, prefix + pre.GOVERNANCE))
    new_governance = images.get(pre.GOVERNANCE, (old_governance, old_governance))[1]
    need(version(old_governance) == index['from_version'] and version(new_governance) == index['to_version'] and
         index['from_version'].startswith('ADAPT-FW-') and index['to_version'].startswith('ADAPT-FW-') and
         int(index['to_version'][9:]) > int(index['from_version'][9:]), 'TRANSITION_VERSION_CHAIN')
    # Installed distribution includes unchanged payloads too, not just replacements.
    installed = {p[len(prefix):]: h for p, h in after.items() if p.startswith(prefix)}
    for ref, digest in {**{'TOOLS/' + p: h for p, h in source_manifest['files'].items()},
                        **source_manifest['instance_files']}.items():
        need(installed.get(ref) == digest, 'TRANSITION_INSTALLED_MANIFEST')
    need(installed['TOOLS/MANIFEST.json'] == pre.digest(read(file(source_framework, 'TOOLS/MANIFEST.json'))),
         'TRANSITION_INSTALLED_MANIFEST')
    return {'before': {p[len(prefix):]: h for p, h in before.items() if p.startswith(prefix)},
            'after': installed, 'from_version': index['from_version'], 'to_version': index['to_version']}


def recovery_continuity(before, after, installation, target, ledger, dependencies=None):
    """Fold exactly the supplied ordered transitions; equality is still required."""
    current, version, seen = dict(before), None, set()
    for reference in installation.get('framework_transitions', []):
        need(reference['sha256'] not in seen, 'DUPLICATE_FRAMEWORK_TRANSITION')
        seen.add(reference['sha256'])
        transition = framework_transition(reference, target, ledger, dependencies)
        need(current == transition['before'] and
             (version is None or version == transition['from_version']), 'FRAMEWORK_TRANSITION_CHAIN')
        current, version = transition['after'], transition['to_version']
    need(current == after, 'CURRENT_COMPLETED_STATE_MISMATCH')
    need(version is None or version == installation['version'], 'TRANSITION_INSTALLATION_VERSION')
    return {'status': 'CONTINUITY_VALID', 'transitions': len(seen), 'operational_authority': False}


def _checkpoint(event, sequence):
    """Test-only interruption seam, never an authority mechanism."""


def normalize_index(data):
    """Restore contiguous Index rows, preserving every row/prose/comment byte.

    This is a separate STRUCTURAL action, never an implicit context mutation.
    Only one exact eight-column Index table and complete unique CP rows qualify.
    """
    import re
    text = data.decode('utf-8-sig')
    need('```' not in text and '~~~' not in text and text.count('<!--') == text.count('-->'),
         'AMBIGUOUS_INDEX_STRUCTURE')
    visible = re.sub(r'<!--.*?-->', lambda match: re.sub(r'[^\r\n]', ' ', match[0]), text, flags=re.S)
    lines, raw = visible.splitlines(), data.splitlines(keepends=True)
    need(len(lines) == len(raw), 'UNSUPPORTED_LINE_BOUNDARIES')
    starts = [i for i,line in enumerate(lines) if line.strip() == '## Index']
    need(len(starts) == 1, 'UNIQUE_INDEX_SECTION_REQUIRED')
    start = starts[0]
    end = next((i for i in range(start+1,len(lines)) if re.match(r'^#{1,2} ',lines[i])),len(lines))
    table = [i for i in range(start+1,end) if lines[i].lstrip().startswith('|')]
    columns = ['CP-ID','Workcell','Handoff ID','Source Truth Version','Size','Date Assembled','Status','Notes']
    need(len(table) >= 2 and op.split_row(lines[table[0]]) == columns and
         table[1] == table[0]+1 and all(re.fullmatch(r':?-{3,}:?',cell)
         for cell in op.split_row(lines[table[1]])) and len(op.split_row(lines[table[1]])) == 8,
         'CANONICAL_INDEX_HEADER_REQUIRED')
    rows, ids = [], set()
    for index in table[2:]:
        fields = op.split_row(lines[index])
        need(len(fields) == 8 and re.fullmatch(r'CP-\d+',fields[0]) and
             int(fields[0].split('-')[1]) not in ids and fields[6] in
             {'ACTIVE','STALE','SUPERSEDED','ARCHIVED'} and raw[index].endswith(b'\n'),
             'INVALID_OR_DUPLICATE_INDEX_ROW')
        ids.add(int(fields[0].split('-')[1])); rows.append(dict(zip(columns,fields)))
    try:
        need(op.table(text,'Index',columns) == rows, 'INDEX_ROWS_MISMATCH')
        return data
    except op.Problem:
        pass
    destination = table[1]+1
    need(raw[destination-1].endswith(b'\n'), 'UNTERMINATED_INDEX_SEPARATOR')
    moved = set(table[2:])
    after = b''.join(raw[:destination] + [raw[i] for i in table[2:]] +
                     [raw[i] for i in range(destination,len(raw)) if i not in moved])
    need(op.table(after.decode('utf-8-sig'),'Index',columns) == rows, 'NORMALIZED_INDEX_INVALID')
    return after


class MaintenanceEntry:
    """One human-governed entry, usable in the normal ADAPT interaction.

    host.installation(target) returns an independently obtained deployment record:
    target, version, release/adoption references, installed immutable file hashes,
    scope (existing SupervisedVerifier configuration), evidence_class and runtime
    conditions. host.authorize(review) presents the exact review to the humans and
    returns the existing supervised authorization object. host.current(review)
    returns current approval/withdrawal state before every mutation.

    host.ledger is fixed deployment configuration, outside the instance/packet.
    host.evidence_class is TECHNICAL_TEST or HUMAN_SUPERVISED. Neither value
    authenticates a human. The organization owns identity and interaction access.
    """
    def __init__(self, host=None, *, installation=None, ledger=None,
                 interaction=None, synthetic=False):
        # Existing integrations remain compatible. The built-in adapter uses
        # the SAME verifier and writer; neither packets nor saved approvals are
        # an input channel for human decisions.
        need(host is None or all(v is None for v in (installation, ledger, interaction)),
             'ONE_INTERACTION_REQUIRED')
        need(type(synthetic) is bool, 'EVIDENCE_CLASS_REQUIRED')
        self.host = host if host is not None else (self if installation is not None else None)
        self._record = deepcopy(installation)
        self.ledger = ledger
        self.interaction = interaction
        self.evidence_class = 'TECHNICAL_TEST' if synthetic else 'HUMAN_SUPERVISED'
        self._authorization = None

    def installation(self, target):
        return deepcopy(self._record)

    def withdraw(self):
        """Capture withdrawal through the same interaction before any next write."""
        self._authorization = None

    def authorize(self, review):
        """Prepare evidence from explicit captured decisions, never invent consent.

        ADAPT supplies the callback. Humans review readable text and respond in
        the normal interaction; they need not compose JSON, hashes or timestamps.
        Responses name decision, plan_sha256, human, capacities and an original
        source_reference. Role evidence comes from existing installation scope.
        One response may exercise multiple capacities of the same actual human.
        """
        self.withdraw()
        need(callable(self.interaction), 'EXPLICIT_HUMAN_AUTHORIZATION_REQUIRED')
        responses = deepcopy(self.interaction(deepcopy(review)))
        need(isinstance(responses, list) and bool(responses), 'EXPLICIT_HUMAN_AUTHORIZATION_REQUIRED')
        scope = review['installation']['scope']
        now = datetime.now(timezone.utc)
        stamp = now.isoformat()
        approvals = []
        for response in responses:
            need(response['decision'] == 'APPROVE_EXACT_ACTION' and
                 response['plan_sha256'] == review['plan_sha256'] and
                 supervised._text(response['source_reference']), 'EXACT_HUMAN_DECISION_REQUIRED')
            capacities = response['capacities']
            need(isinstance(capacities, list) and bool(capacities) and
                 len(capacities) == len(set(capacities)), 'EXPLICIT_CAPACITIES_REQUIRED')
            for role in capacities:
                need(role in scope['authorities'] and
                     response['human'] == scope['authorities'][role], 'WRONG_GOVERNANCE_CAPACITY')
                basis = scope['role_evidence'][role]
                approvals.append({'role': role, 'human': response['human'], 'approved': True,
                    'approved_at': stamp, 'approval_reference': response['source_reference'],
                    'role_basis_reference': basis['role_basis_reference'],
                    'designation_reference': basis.get('designation_reference', '')})
        binding = deepcopy(review['authorization_binding'])
        self._authorization = {'maintenance_scope': deepcopy(scope), 'human_authorization': {
            'binding': binding, 'synthetic': self.evidence_class == 'TECHNICAL_TEST',
            'approved_at': stamp, 'checked_at': stamp, 'not_before': stamp,
            'expires_at': (now + timedelta(hours=1)).isoformat(), 'withdrawn': False,
            'audit_reference': binding['audit_reference'],
            'audit_preservation_reference': str(checked(self.ledger)),
            'approvals': approvals, 'interaction_responses': responses}}
        return deepcopy(self._authorization)

    def current(self, review):
        return deepcopy(self._authorization)

    def interact(self, request=None, *, response=None, human=None, source_reference=None,
                 action=None, interpreted_decision=None, reporting_check=None):
        """Ordinary ACTION_PROMPT pause/re-entry using the existing approval adapter.

        Installation/ledger and response provenance are supplied by the bound
        ADAPT interaction, never packet assertions. interpreted_decision is an
        optional model-assisted classification of the actual response, not consent
        or authentication. Ambiguous language must be classified CLARIFY.
        Persisted envelopes are decision context, never reusable authorization.
        """
        outcome, outcome_available, reentry = None, False, False
        try:
            need(self.host is self, 'BUILTIN_INTERACTION_ADAPTER_REQUIRED')
            # Validate the configured ledger boundary before persisting a review.
            self._installation(self._record['target'])
            ledger = checked(self.ledger)
            need(ledger.is_dir(), 'EXTERNAL_CONTROLLED_LEDGER_REQUIRED')
            pending = checked(ledger / 'pending-reviews')
            pending.mkdir(exist_ok=True)
            if request is not None:
                need(response is None, 'REVIEW_BEFORE_DECISION_REQUIRED')
                plan = self.preview(request)
                key = pre.digest(request['request']['operation_reference'].encode())
                path = checked(pending / (key + '.json'))
                need(not path.with_suffix('.used').exists(), 'DECISION_ALREADY_CONSUMED')
                if path.exists():
                    need(supervised._exact(pre.load_json(path.read_bytes()), plan), 'FRESH_REVIEW_REQUIRED')
                else:
                    rt._persist_new(path, rt._encoded(plan))
                return {'status': 'AWAITING_HUMAN', 'action': 'STOP', 'text': human_review(plan)}
            paths = [p for p in sorted(pending.glob('*.json')) if not p.with_suffix('.used').exists()]
            plans = [(p, pre.load_json(checked(p).read_bytes())) for p in paths]
            # Never bind a reply by conversational memory or by whichever plan is newest.
            if action is not None:
                plans = [(p, v) for p, v in plans if v['request']['request']['task'] == action]
            if not plans:
                consumed = [(p, pre.load_json(checked(p).read_bytes()))
                            for p in sorted(pending.glob('*.json')) if p.with_suffix('.used').exists()]
                if action is not None:
                    consumed = [(p, v) for p, v in consumed if v['request']['request']['task'] == action]
                if len(consumed) == 1:
                    path, plan = consumed[0]
                    # Consumption proves no prior mutation state. Enable the existing
                    # uncertainty fallback before inspecting any saved execution evidence.
                    outcome = {'status': 'BLOCKED',
                               'operation_reference': plan['request']['request']['operation_reference'],
                               'reference': str(ledger / (path.stem + '.reference.json'))}
                    outcome_available, reentry = True, True
                    decision = pre.load_json(checked(path.with_suffix('.used')).read_bytes())
                    if decision['decision'] == 'REJECT':
                        text = 'This reviewed action was rejected. No recovery was attempted. Request a new review if needed. STOP.'
                    else:
                        # Writer-owned evidence, not the response envelope, establishes success.
                        reference = checked(ledger / (path.stem + '.reference.json'))
                        record = pre.load_json(reference.read_bytes())
                        if isinstance(record, dict) and isinstance(record.get('claim'), str) and record['claim']:
                            outcome['claim'] = record['claim']
                        need(isinstance(record, dict) and isinstance(record.get('claim'), str) and
                             bool(record['claim']) and record.get('operation_reference') ==
                             outcome['operation_reference'], 'INCOMPLETE_EXECUTION_REFERENCE')
                        claim = checked(record['claim'])
                        outcome_path = claim.with_name(claim.name.replace('.claim.', '.outcome.'))
                        self.audit(claim)
                        saved = pre.load_json(checked(outcome_path).read_bytes())
                        outcome.update(saved)
                        error_path = checked(path.with_suffix('.reporting'))
                        reporting_error = (pre.load_json(error_path.read_bytes())['error']
                                           if error_path.exists() else None)
                        text = human_outcome(saved, plan, reporting_error)
                    return dict(outcome if isinstance(outcome, dict) else {}, status='BLOCKED',
                                action='STOP', reason='DECISION_ALREADY_CONSUMED', text=text)
            if not plans and not locals().get('consumed'):
                return {'status': 'BLOCKED', 'action': 'STOP', 'reason': 'NO_PENDING_REVIEW',
                        'text': 'There is no pending reviewed action to decide. No recovery was attempted '
                        'and no instance files changed. Start a bounded diagnostic or request a new '
                        'review before approving any action. Ordinary execution remains gated. STOP.'}
            if len(plans) != 1:
                return {'status': 'BLOCKED', 'action': 'STOP', 'reason': 'SELECT_ONE_REVIEWED_ACTION',
                        'text': 'Select exactly one reviewed action by task name before deciding: ' +
                        ', '.join(v['request']['request']['task'] for p, v in
                                  (plans or locals().get('consumed', []))) +
                        '. No recovery attempted. STOP.'}
            path, plan = plans[0]
            try:
                need(supervised._exact(self.preview(plan['request']), plan), 'FRESH_REVIEW_REQUIRED')
            except Exception as error:
                raise ValueError('FRESH_REVIEW_REQUIRED') from error
            if response is None:
                return {'status': 'AWAITING_HUMAN', 'action': 'STOP', 'text': human_review(plan)}
            need(isinstance(response, str) and response.strip(), 'EXPLICIT_HUMAN_RESPONSE_REQUIRED')
            literal = {'approve': 'APPROVE', 'reject': 'REJECT', 'show details': 'SHOW DETAILS',
                       'yes, approve this action': 'APPROVE', 'do not proceed': 'REJECT',
                       'please show the details': 'SHOW DETAILS'}
            decision = literal.get(response.strip().casefold().removesuffix('.'), interpreted_decision or 'CLARIFY')
            need(decision in {'APPROVE', 'REJECT', 'SHOW DETAILS', 'CLARIFY'}, 'CLARIFY_RESPONSE')
            if decision == 'SHOW DETAILS':
                return {'status': 'AWAITING_HUMAN', 'action': 'STOP',
                        'text': human_review(plan) + '\nRequested technical evidence follows. '
                        'No recovery attempted; the decision remains pending.\n' + plan['text']}
            if decision == 'CLARIFY':
                return {'status': 'AWAITING_HUMAN', 'action': 'STOP',
                        'text': 'Please clarify: approve this reviewed action, reject it, or show details. No files changed. STOP.'}
            need(supervised._text(human) and supervised._text(source_reference),
                 'HUMAN_AND_ORIGINAL_RESPONSE_REFERENCE_REQUIRED')
            if decision == 'REJECT':
                rt._persist_new(path.with_suffix('.used'), rt._encoded({'decision': decision,
                    'human': human, 'source_reference': source_reference, 'response': response}))
                return {'status': 'BLOCKED', 'action': 'STOP',
                        'text': 'STATUS: BLOCKED\nACTION: Reviewed recovery rejected.\nCHANGES: None.\n'
                        'VALIDATION: No recovery attempted.\nREMAINING ISSUES: Existing blocker remains open.\n'
                        'NEXT ACTION: Request a new review if needed.\nAPPROVAL: Required for a new action. STOP.'}
            scope = plan['installation']['scope']
            capacities = [role for role, owner in scope['authorities'].items() if owner == human]
            need(bool(capacities), 'MISSING_GOVERNANCE_CAPACITY')
            missing = [role for role in scope['authorities'] if role not in capacities]
            if missing:
                outcome = {'status': 'BLOCKED', 'action': 'STOP', 'reason': 'MISSING_GOVERNANCE_CAPACITY'}
                outcome_available = True
                return dict(outcome, text=human_outcome({'reason': 'Missing approval in the governance capacity: ' +
                    ', '.join(missing) + '. Obtain that human decision through the existing approval adapter.'}))
            captured = {'decision': 'APPROVE_EXACT_ACTION', 'plan_sha256': plan['plan_sha256'],
                        'human': human, 'capacities': capacities, 'source_reference': source_reference,
                        'response': response}
            old_interaction = self.interaction
            self.interaction = lambda review: [deepcopy(captured)]
            try:
                # Existing verifier checks every required capacity before consuming.
                self._authority(plan, initial=True)
                rt._persist_new(path.with_suffix('.used'), rt._encoded(captured))
                result = self.execute(plan)
                outcome, outcome_available = result, True
            finally:
                self.interaction = old_interaction
                self.withdraw()
            # Consumed before entering writer: reporting/process failures never replay.
            rt._persist_new(path.with_suffix('.result'), rt._encoded(result))
            if reporting_check is not None:
                reporting_check(deepcopy(result))
            return dict(result, text=human_outcome(result, plan))
        except Exception as error:
            if outcome_available:
                reporting_error = type(error).__name__ + ': ' + str(error)
                if reentry:
                    # Keep original reference, claim and reporting bytes untouched.
                    return reporting_fallback(outcome, reporting_error, reentry=True)
                try:
                    rt._persist_new(checked(path.with_suffix('.reporting')),
                                    rt._encoded({'error': reporting_error, 'claim':
                                        outcome.get('claim') if isinstance(outcome, dict) else None}))
                except Exception:
                    # Writer completion/ownership still bars replay if reporting storage fails.
                    reporting_error += ' (Reporting evidence could not be saved.)'
                return reporting_fallback(outcome, reporting_error, reentry=reentry)
            code = str(error) if isinstance(error, ValueError) else 'ENTRY_REVALIDATION_FAILED'
            messages = {'SELECT_ONE_REVIEWED_ACTION': 'Select exactly one reviewed action by its task name before deciding.',
                        'FRESH_REVIEW_REQUIRED': 'The reviewed plan or source changed. Request a fresh review.',
                        'HUMAN_APPROVAL_REFUSED': 'Required governance capacity approval is missing, withdrawn or invalid.',
                        'MISSING_GOVERNANCE_CAPACITY': 'Your recorded governance capacity does not authorize this action.',
                        'HUMAN_AND_ORIGINAL_RESPONSE_REFERENCE_REQUIRED': 'The interaction must capture the actual human and original response reference before proceeding.',
                        'DECISION_ALREADY_CONSUMED': 'This reviewed action was already decided. Inspect its saved outcome; do not retry it.',
                        'WRONG_INSTANCE': 'The current instance does not match the reviewed target.',
                        'INSTALLED_BYTES_CHANGED': 'Installed framework files changed. Verify the installation and request a fresh review.'}
            blocked = {'status': 'BLOCKED', 'action': 'STOP', 'reason': code}
            try:
                text = human_outcome({'reason': messages.get(code,
                    'The action could not be verified. Request technical details about the missing prerequisite.')})
            except Exception as rendering_error:
                return reporting_fallback(blocked, type(rendering_error).__name__ + ': ' + str(rendering_error))
            return dict(blocked, text=text)

    def diagnose(self, instance, *, failure_id, failed_action, observed_error,
                 evidence=None, cause='Cause not established', request=None):
        """Read-only reporting works even without valid ordinary context/entry."""
        report = {'status': 'DIAGNOSTIC_ONLY', 'action': 'STOP', 'failure_identifier': failure_id,
            'failed_action': failed_action, 'observed_error': observed_error,
            'relevant_evidence': deepcopy(evidence or []), 'root_cause_or_uncertainty': cause,
            'current_state': None, 'recovery_eligibility': 'UNSUPPORTED_OR_UNVERIFIED',
            'recommended_action': 'Preserve evidence and request human resolution',
            'proposed_mutation_scope': [], 'expected_result': 'Affected action remains stopped',
            'governance_restrictions': 'Release/adoption and applicable capacities remain required; '
                'no resolution, activation, retry or handback',
            'human_approval_requirement': 'Explicit approval of this exact plan before mutation',
            'stop_conditions': ['Missing, rejected or ambiguous approval', 'Changed plan or bytes',
                'Wrong scope/instance/capacity', 'Interrupted ownership or invalid journal']}
        try:
            root = checked(instance)
            report['current_state'] = op.state(root)
            report['diagnostics'] = op.doctor(root)
        except Exception as error:
            report['state_uncertainty'] = str(error)
        if request is not None:
            try:
                need(request['request']['target']['root'] == str(checked(instance)), 'WRONG_INSTANCE')
                plan = self.preview(request)
                report.update(status='READY_FOR_HUMAN_REVIEW', recovery_eligibility='BOUNDED_OPERATION',
                    recommended_action=request['kind'], proposed_mutation_scope=deepcopy(plan['operations']),
                    expected_result=plan['rendered'].get('completion', 'Recovery-only artifacts; STOP'),
                    plan=plan, review=human_review(plan))
            except Exception as error:
                report.update(status='RECOVERY_REFUSED', refusal=str(error))
        report['text'] = report.get('review',
            'ISSUE: ' + observed_error + '\nIMPACT: The affected action is stopped.\n'
            'RECOMMENDATION: Preserve evidence and request a bounded recovery review.\n'
            'CHANGES: None.\nRISK: Cause may be uncertain; ordinary context is unavailable.\n'
            'DECISION: No executable recovery plan is verified yet. STOP.')
        return report

    def _installation(self, target):
        need(self.host is not None, 'CONTROLLED_MAINTENANCE_ENTRY_REQUIRED')
        record = deepcopy(self.host.installation(deepcopy(target)))
        root = checked(target['root'])
        need(root.is_dir() and target == {'root': str(root), 'identity': op.state(root)['ProjectName']},
             'WRONG_INSTANCE')
        need(record['target'] == target and record['version'] == VERSION and
             op.headers(op.text(root, pre.GOVERNANCE), ['VERSION'])['VERSION'] == VERSION,
             'WRONG_RELEASE_OR_INSTALLATION')
        need(all(isinstance(record[k], str) and record[k].strip() for k in
                 ('release_reference', 'adoption_reference', 'installation_reference')),
             'EXPLICIT_RELEASE_INSTALLATION_ADOPTION_REQUIRED')
        need(record['scope']['target'] == target and record['evidence_class'] == self.host.evidence_class
             and self.host.evidence_class in {'TECHNICAL_TEST', 'HUMAN_SUPERVISED'}, 'DEPLOYMENT_BINDING')
        need(op.headers(op.text(root, pre.DIRECTOR), ['HUMAN_OWNER'])['HUMAN_OWNER'] ==
             record['scope']['authorities']['Human Director'], 'CURRENT_DIRECTOR_MISMATCH')
        need(supervised._exact(record['conditions'], {'filesystem': 'LOCAL', 'exclusive_operator': True,
             'power_loss_uncertainty': False}), 'UNSUPPORTED_DEPLOYMENT_CONDITION')
        manifest = pre.load_json(file(root, 'TOOLS/MANIFEST.json').read_bytes())
        expected = {'TOOLS/' + p for p in manifest['files']} | {'TOOLS/MANIFEST.json'} | set(manifest['instance_files'])
        expected |= {pre.GOVERNANCE, op.SCHEMA, '15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md',
                     '15_COMMANDS_AND_DRIVERS/STOP_RULES.md', '10_CONTEXT_ECONOMY/CONTEXT_RULES.md',
                     '07_GUARDRAILS/CONTEXT_GUARDRAIL.md'}
        need(set(record['installed_hashes']) == expected, 'INSTALLATION_INVENTORY_REQUIRED')
        for ref, digest in record['installed_hashes'].items():
            need(pre.digest(file(root, ref).read_bytes()) == digest, 'INSTALLED_BYTES_CHANGED')
        for ref, digest in {**{'TOOLS/' + p: h for p, h in manifest['files'].items()},
                            **manifest['instance_files']}.items():
            need(record['installed_hashes'][ref] == digest, 'INSTALLATION_MANIFEST_MISMATCH')
        ledger = checked(self.host.ledger)
        need(ledger.is_dir() and not root.is_relative_to(ledger) and not ledger.is_relative_to(root),
             'EXTERNAL_CONTROLLED_LEDGER_REQUIRED')
        need(root.stat().st_dev == ledger.stat().st_dev, 'SAME_LOCAL_VOLUME_REQUIRED')
        return root, record, ledger

    def _context(self, root, external, packet, scope, operation_reference):
        need(packet['target'] == scope['target'] and packet['purpose'] == pre.PURPOSE and
             packet['executor'] == scope['executor'], 'CONTEXT_IDENTITY')
        values = op.state(root)
        need(values['Blocked'] == 'YES', 'BLOCKED_RECOVERY_ONLY')
        need(not any(d['status'] in {'FAIL', 'UNVERIFIED'} for d in op.doctor(root)['diagnostics']),
             'CURRENT_STATE_INVALID')
        inputs, aliases = {}, set()
        for item in packet['inputs']:
            ref = item['path']
            source_path = file(root, ref)
            alias = str(source_path).casefold()
            need(ref == source_path.relative_to(root).as_posix() and alias not in aliases and
                 pre.digest(source_path.read_bytes()) == item['sha256'] and
                 item['class'] in {'CURRENT_CANONICAL', 'HISTORICAL_RECOVERY'} and
                 bool(item['reason'].strip()), 'CHANGED_OR_INVALID_INPUT')
            need(supervised._time(item['verified_at']) <= datetime.now(timezone.utc), 'INPUT_TIME')
            aliases.add(alias)
            inputs[ref] = item
        inventory = set(pre.REQUIRED)
        for folder in ('10_CONTEXT_ECONOMY', '06_HANDOFFS'):
            inventory |= {p.relative_to(root).as_posix() for p in (root / folder).rglob('*') if p.is_file()}
        need(inventory <= inputs.keys() and all(inputs[p]['class'] == 'CURRENT_CANONICAL'
             for p in pre.REQUIRED), 'CURRENT_INVENTORY_REQUIRED')
        active = [r for r in op.table(op.text(root, pre.VERSION_LOG), 'Version Log',
                  ['Version', 'Document Name', 'Status']) if r['Status'] == 'ACTIVE']
        need(len(active) == 1 and active[0]['Version'] == values['SourceTruthVersion'] and
             active[0]['Document Name'] in inputs and
             inputs[active[0]['Document Name']]['class'] == 'CURRENT_CANONICAL', 'REGISTERED_SOURCE_REQUIRED')
        pre._writes(root, packet, inputs, inventory, values)
        failure = assembly._record(external, packet, 'failure')
        blockers = {r['BLK-ID']: r['Status'] for r in op.table(op.text(root, pre.BLOCKERS), 'Blockers', ['BLK-ID', 'Status'])}
        need(failure['target'] == packet['target'] and failure['state'] == values and
             failure['blockers'] == blockers and 'OPEN' in blockers.values() and
             failure['ordinary_context_unavailable'] == packet['failure_reason'] and
             bool(packet['failure_reason'].strip()) and type(failure['retry_limit']) is int and
             failure['retry_limit'] > 0 and len(failure['attempts']) >= failure['retry_limit'], 'FAILURE_HISTORY_REQUIRED')
        seen = set()
        for attempt in failure['attempts']:
            need(attempt['result'] == 'FAILED' and attempt['evidence'] not in seen and
                 bool(assembly._record(external, packet, attempt['evidence'])['raw_diagnostic'].strip()),
                 'EXHAUSTED_ATTEMPTS_REQUIRED')
            seen.add(attempt['evidence'])
        completion = packet['completion']
        need(all(type(completion.get(k)) is type(v) and completion[k] == v for k,v in pre.COMPLETION.items())
             and completion['return_to'] == [scope['authorities']['Human Director'],
             scope['authorities']['Human Framework Maintainer']] and packet['freshness'] ==
             'STALE_ORDINARY_INVALID_RECOVERY_EVIDENCE_ONLY', 'RECOVERY_COMPLETION_REQUIRED')
        outputs = [file(external, completion[k]) for k in ('journal', 'manifest', 'return_destination')]
        need(len(set(outputs)) == 3 and not any(p.exists() for p in outputs), 'FRESH_OUTPUTS_REQUIRED')
        config = assembly._record(external, packet, 'assembly')
        need(config['format'] == 'operational-v1', 'OPERATIONAL_SELECTION_REQUIRED')
        # This is selection/task evidence, never an approval record. Human
        # approvals bind its hash and all rendered bytes only after plan review.
        delegation = assembly._record(external, packet, 'authorization')
        need(delegation == {'purpose': pre.PURPOSE, 'target': packet['target'],
             'task': packet['task'], 'executor': packet['executor'], 'gates': packet['gates']},
             'TASK_BASIS_MISMATCH')
        reference = str(checked(self.host.ledger) / (pre.digest(operation_reference.encode()) + '.reference.json'))
        return assembly._build(root, external, packet, operational=True, authority_reference=reference)

    def preview(self, request):
        """Read current bytes and return an exact unsigned plan; never writes."""
        request = deepcopy(request)
        need(set(request) == {'kind', 'request', 'evidence_root', 'parameters'}, 'EXACT_REQUEST_ENVELOPE')
        binding = request['request']
        need(set(binding) == set(supervised.BINDING_KEYS), 'EXACT_BINDING_REQUIRED')
        root, installation, ledger = self._installation(binding['target'])
        external = checked(request['evidence_root'])
        need(external.is_dir() and not external.is_relative_to(root) and not root.is_relative_to(external)
             and not ledger.is_relative_to(external) and not external.is_relative_to(ledger), 'DISJOINT_EVIDENCE_REQUIRED')
        evidence = {}
        for ref in binding['evidence'].values():
            path = file(external, ref['path'])
            need(ref['path'] == path.relative_to(external).as_posix() and
                 path.as_posix().casefold() not in evidence and pre.digest(path.read_bytes()) == ref['sha256'],
                 'CHANGED_EVIDENCE')
            evidence[path.as_posix().casefold()] = ref['sha256']
        need(supervised.SupervisedVerifier().verify(binding)['structural_status'] == 'PASS', 'INVALID_BINDING')
        before = snapshot(root)
        if request['kind'] == 'STRUCTURAL':
            scope = request['parameters']
            need(binding['ids'] == scope, 'STRUCTURAL_SCOPE')
            if set(scope) == {'blocker'}:
                path = pre.BLOCKERS
                transform = lambda data: structural._repair(data, scope['blocker'])[0]
            else:
                need(scope == {'register': 'CONTEXT_INDEX', 'operation': 'NORMALIZE_TABLE_PLACEMENT'},
                     'STRUCTURAL_SCOPE')
                path, transform = pre.INDEX, normalize_index
            data = file(root, path).read_bytes()
            after = transform(data)
            need(after != data, 'NO_REPAIR_REQUIRED')
            need(binding['writes'] == [{'path': path, 'operation': 'set_fields', 'fields': ['placement'],
                 'before_sha256': pre.digest(data)}] and len(binding['inputs']) == len(before) and
                 {i['path']: i['sha256'] for i in binding['inputs']} == before, 'STRUCTURAL_BINDING')
            operations = [{'sequence': 1, 'path': path, 'before_sha256': pre.digest(data),
                           'after_sha256': pre.digest(after), 'after_image_hex': after.hex()}]
            rendered = {'completion': 'Placement only; preserve every row value and history; STOP'}
        else:
            need(request['kind'] == 'CONTEXT', 'UNSUPPORTED_ACTION')
            packet = deepcopy(request['parameters'])
            need(all(packet[k] == binding[k] for k in ('target', 'purpose', 'task', 'executor',
                 'inputs', 'writes', 'evidence', 'ids', 'completion', 'gates')), 'CONTEXT_BINDING')
            rendered = self._context(root, external, packet, installation['scope'], binding['operation_reference'])
            operations = rendered['operations']
        need(snapshot(root) == before, 'SOURCE_CHANGED_DURING_PLAN')
        for reference in installation.get('framework_transitions', []):
            framework_transition(reference, binding['target'], ledger, evidence)
        # Bind the already existing ownership/evidence prefix into this review.
        # New slots remain exclusive-create; no historical record is rewritten.
        evidence.update(self._history_dependencies(root, ledger))
        files = []
        for ref in dict.fromkeys(o['path'] for o in operations):
            path = file(root, ref)
            original = path.read_bytes() if path.exists() else None
            final = bytes.fromhex([o for o in operations if o['path'] == ref][-1]['after_image_hex'])
            diff = ''.join(difflib.unified_diff(
                [] if original is None else original.decode('utf-8').splitlines(keepends=True),
                final.decode('utf-8').splitlines(keepends=True), fromfile=ref + ' (before)', tofile=ref + ' (after)'))
            files.append({'path': ref, 'before_image_hex': None if original is None else original.hex(),
                          'after_image_hex': final.hex(), 'diff': diff})
        body = {'request': request, 'baseline': before, 'installation': installation, 'files': files,
                'operations': operations, 'rendered': rendered, 'evidence_hashes': evidence}
        body['plan_sha256'] = assembly.fingerprint(body)
        approved_binding = deepcopy(binding)
        need('review' not in approved_binding['ids'], 'RESERVED_REVIEW_ID')
        approved_binding['ids']['review'] = {'plan_sha256': body['plan_sha256'],
                                            'review_sha256': assembly.fingerprint(body)}
        body['authorization_binding'] = approved_binding
        images = dict(before)
        descriptions = []
        for operation in operations:
            ref = operation['path']
            descriptions.append({k: operation[k] for k in ('sequence', 'path', 'before_sha256', 'after_sha256')})
            images[ref] = operation['after_sha256']
        body['text'] = ('# Technical details for the reviewed recovery action\n\n'
                        'ISSUE: ' + request['kind'] + ' recovery requested.\n'
                        'CAUSE: See original failure evidence; unestablished causes remain uncertain.\n'
                        'IMPACT: Affected action is stopped; ordinary execution remains gated.\n'
                        'RECOMMENDED ACTION: Execute only the following bounded operations.\n'
                        'FILES AFFECTED: ' + ', '.join(f['path'] for f in files) + '\n'
                        'EXPECTED RESULT: Validated placement or recovery-only assembly; STOP.\n'
                        'RISK: Partial completion or changed sources; preserve evidence and STOP.\n'
                        'APPROVAL REQUIRED: Approve this exact proposed action in each applicable capacity.\n\n' +
                        assembly.canonical(approved_binding) +
                        '\n\nExact operations and SHA256:\n' + json.dumps(descriptions, indent=2) +
                        '\n\n' + '\n'.join(f['diff'] for f in files) +
                        '\nExact before/after bytes are in files and operations of this plan.\n'
                        'Separate action approval required. Partial completion possible. No automatic retry, '
                        'resume, rollback, resolution, activation or handback. STOP.\n')
        return body

    def _authority(self, plan, *, initial=False):
        auth = deepcopy(self.host.authorize(deepcopy(plan)) if initial else self.host.current(deepcopy(plan)))
        need(set(auth) == {'maintenance_scope', 'human_authorization'}, 'SEPARATE_AUTHORIZATION_REQUIRED')
        need(auth['maintenance_scope'] == plan['installation']['scope'], 'DEPLOYMENT_SCOPE_MISMATCH')
        verified = supervised.SupervisedVerifier(auth['maintenance_scope']).verify(
            plan['authorization_binding'], human_authorization=auth['human_authorization'])
        need(verified['status'] == 'SUPERVISED_EVIDENCE_VALID', 'HUMAN_APPROVAL_REFUSED')
        need(auth['human_authorization']['synthetic'] is (self.host.evidence_class == 'TECHNICAL_TEST'),
             'AUTHORITY_CLASS_MISMATCH')
        return auth

    def execute(self, plan):
        """Review via host, execute one exact bounded action, preserve evidence, STOP."""
        result = {'status': 'REFUSED', 'recovery_status': 'RECOVERY_REFUSED',
                  'action': 'STOP', 'operational_authority': False,
                  'genuine_human_authority': 'NOT_TESTED'}
        owned, external = False, None
        try:
            plan = deepcopy(plan)
            need(supervised._exact(self.preview(plan['request']), plan), 'CHANGED_PLAN_OR_SOURCE')
            root, installation, ledger = self._installation(plan['request']['request']['target'])
            auth = self._authority(plan, initial=True)
            result['recovery_status'] = 'APPROVED_FOR_EXACT_ACTION'
            target_key = pre.digest(str(root).casefold().encode())
            target_ledger = checked(ledger / target_key)
            target_ledger.mkdir(exist_ok=True)
            slots = sorted(target_ledger.glob('*.claim.json'))
            # Every prior slot must have an exact completed, independently
            # auditable outcome. An uncertain prefix blocks all later actions.
            self._history(root, ledger, installation, plan['baseline'])
            history_dependencies = self._history_dependencies(root, ledger)
            need(all(plan['evidence_hashes'].get(p) == h for p, h in history_dependencies.items()),
                 'UNREVIEWED_RECOVERY_HISTORY')
            for path, digest in plan['evidence_hashes'].items():
                need(pre.digest(checked(path).read_bytes()) == digest, 'SOURCE_EVIDENCE_CHANGED')
            need(snapshot(root) == plan['baseline'] and
                 supervised._exact(self._installation(plan['request']['request']['target'])[1], installation),
                 'DEPLOYMENT_CHANGED')
            claim = checked(target_ledger / f'{len(slots):08d}.claim.json')
            # Fixed deployment-wide namespace: changing target/evidence directories
            # cannot make an operation reference reusable.
            ref = plan['request']['request']['operation_reference']
            reference = checked(ledger / (pre.digest(ref.encode()) + '.reference.json'))
            rt._persist_new(reference, rt._encoded({'claim': str(claim), 'operation_reference': ref}))
            external = checked(target_ledger / f'{len(slots):08d}')
            rt._persist_new(claim, rt._encoded({'plan': plan, 'authorization': auth,
                                               'reference': str(reference), 'evidence': str(external)}))
            owned = True
            external.mkdir()
            result['claim'] = str(claim)
            journal = external / 'journal.jsonl'
            journal_bytes = b''
            expected = dict(plan['baseline'])
            def append(event, **fields):
                nonlocal journal_bytes
                need(not journal.exists() if not journal_bytes else journal.read_bytes() == journal_bytes,
                     'JOURNAL_CHANGED')
                record = {'event': event, 'previous_sha256': pre.digest(journal_bytes), **fields}
                with journal.open('ab' if journal_bytes else 'xb') as stream:
                    stream.write(rt._encoded(record)); stream.flush(); os.fsync(stream.fileno())
                journal_bytes += rt._encoded(record)
            claim_bytes = claim.read_bytes()
            reference_bytes = reference.read_bytes()
            result['claim_sha256'] = pre.digest(claim_bytes)
            append('PLAN_VALIDATED', plan_sha256=plan['plan_sha256'])
            def recheck():
                need(claim.read_bytes() == claim_bytes and snapshot(root) == expected and
                     journal.read_bytes() == journal_bytes and reference.read_bytes() == reference_bytes,
                     'OWNERSHIP_SOURCE_OR_JOURNAL_CHANGED')
                need(supervised._exact(self._installation(plan['request']['request']['target'])[1], installation),
                     'DEPLOYMENT_CHANGED')
                self._authority(plan)
                need(sorted(target_ledger.glob('*.claim.json')) == slots + [claim], 'OWNERSHIP_SEQUENCE_CHANGED')
                # Revalidate full evidence inventories as well as the bound file
                # hashes: a newly added backup/source file is also drift.
                for transition in installation.get('framework_transitions', []):
                    framework_transition(transition, plan['request']['request']['target'], ledger)
                for prior in slots:
                    prior_record = pre.load_json(prior.read_bytes())
                    need(not (checked(prior_record['evidence']) / 'interruption.json').exists(),
                         'INTERRUPTED_OWNERSHIP')
                    for transition in prior_record['plan']['installation'].get('framework_transitions', []):
                        framework_transition(transition, plan['request']['request']['target'], ledger)
                for path, digest in plan['evidence_hashes'].items():
                    need(pre.digest(checked(path).read_bytes()) == digest, 'SOURCE_EVIDENCE_CHANGED')
            for operation in plan['operations']:
                seq, ref = operation['sequence'], operation['path']
                recheck()
                path = file(root, ref)
                need(expected.get(ref, 'ABSENT') == operation['before_sha256'], 'BEFORE_IMAGE_MISMATCH')
                append('BEFORE_WRITE_REVALIDATED', operation=operation)
                _checkpoint('after_intent', seq)
                recheck()
                data = bytes.fromhex(operation['after_image_hex'])
                need(pre.digest(data) == operation['after_sha256'], 'AFTER_IMAGE_MISMATCH')
                # Temp content stays in the external evidence directory; rename
                # requires the same volume and is refused across volumes.
                temporary = external / f'{seq:04d}.pending'
                rt._persist_new(temporary, data)
                _checkpoint('before_replace', seq)
                recheck()
                checked(path.parent)
                need(path.parent.is_dir(), 'MISSING_CANONICAL_PARENT')
                if operation['before_sha256'] == 'ABSENT':
                    # Exclusive create prevents an unexpected target being replaced.
                    rt._persist_new(path, data)
                else:
                    os.replace(temporary, path)
                    rt._sync_directory(path.parent)
                _checkpoint('after_replace', seq)
                expected[ref] = operation['after_sha256']
                need(snapshot(root) == expected and path.read_bytes() == data, 'RESULT_BYTES_INVALID')
                append('WRITE_COMPLETED', sequence=seq, after_sha256=operation['after_sha256'])
                _checkpoint('after_completion', seq)
            recheck()
            if plan['request']['kind'] == 'STRUCTURAL':
                parameters = plan['request']['parameters']
                final_path = pre.BLOCKERS if 'blocker' in parameters else pre.INDEX
                current_bytes = file(root, final_path).read_bytes()
                restored = (structural._repair(current_bytes, parameters['blocker'])[0]
                            if 'blocker' in parameters else normalize_index(current_bytes))
                need(restored == current_bytes, 'FINAL_STRUCTURE_INVALID')
            else:
                # Reuse the deterministic final schema/reference checks in a
                # private reader instance; no synthetic writer boundary changes.
                final_reader = _load('recovery_runtime')
                final_reader._snapshot = snapshot
                final_reader._file = file
                final_reader._final(root, plan['rendered'], plan['baseline'])
            append('FINAL_VALIDATED', final_hashes=expected)
            result.update(status='TECHNICAL_EXECUTION_ACCEPTED', recovery_status='RECOVERY_VALIDATED', final_hashes=expected,
                          journal=str(journal), journal_sha256=pre.digest(journal_bytes),
                          authorization_class=self.host.evidence_class)
            if self.host.evidence_class == 'HUMAN_SUPERVISED':
                result.update(genuine_human_authority='DEPLOYMENT_SUPPLIED_NOT_INDEPENDENTLY_CERTIFIED')
            if plan['request']['kind'] == 'CONTEXT':
                destinations = plan['request']['parameters']['completion']
                evidence_root = checked(plan['request']['evidence_root'])
                delivery = {'journal': journal_bytes,
                            'manifest': rt._encoded({'final_hashes': expected, 'plan_sha256': plan['plan_sha256']}),
                            'return_destination': rt._encoded({'return_to': destinations['return_to'],
                                'action': 'STOP', 'claim': str(claim), 'final_hashes': expected})}
                receipts = {}
                for name, data in delivery.items():
                    destination = file(evidence_root, destinations[name])
                    checked(destination.parent).mkdir(parents=True, exist_ok=True)
                    rt._persist_new(destination, data)
                    receipts[str(destination)] = pre.digest(data)
                result['delivery_hashes'] = receipts
            rt._persist_new(external / 'completion.json', rt._encoded(result))
            rt._persist_new(claim.with_name(claim.name.replace('.claim.', '.outcome.')), rt._encoded(result))
        except Exception as error:
            result.update(status='INTERRUPTED' if owned else 'REFUSED',
                          recovery_status='RECOVERY_INTERRUPTED' if owned else 'RECOVERY_REFUSED',
                          reason=str(error) if type(error) is ValueError else 'PRECONDITION_OR_IO_FAILURE')
            if owned and external is not None and external.is_dir():
                try:
                    rt._persist_new(external / 'interruption.json', rt._encoded(result))
                except Exception:
                    pass
        return result

    def _history_dependencies(self, root, ledger):
        dependencies = {}
        target_ledger = checked(ledger / pre.digest(str(root).casefold().encode()))
        for path in target_ledger.rglob('*') if target_ledger.exists() else []:
            if checked(path).is_file():
                dependencies[path.as_posix().casefold()] = pre.digest(path.read_bytes())
        for claim in target_ledger.glob('*.claim.json'):
            record = pre.load_json(claim.read_bytes())
            reference = checked(record['reference'])
            dependencies[reference.as_posix().casefold()] = pre.digest(reference.read_bytes())
            for path, digest in record['plan']['evidence_hashes'].items():
                need(pre.digest(checked(path).read_bytes()) == digest, 'HISTORICAL_EVIDENCE_CHANGED')
                dependencies[path] = digest
        return dependencies

    def _history(self, root, ledger, installation, current):
        target = {'root': str(root), 'identity': op.state(root)['ProjectName']}
        folder = checked(ledger / pre.digest(str(root).casefold().encode()))
        slots = sorted(folder.glob('*.claim.json'))
        # Outcomes without claims and noncontiguous ownership are never ignored.
        need({p.stem.split('.')[0] for p in folder.glob('*.outcome.json')} ==
             {p.stem.split('.')[0] for p in slots}, 'INCOMPLETE_OWNERSHIP')
        previous, consumed = None, []
        for sequence, claim in enumerate(slots):
            need(claim.name == f'{sequence:08d}.claim.json', 'OWNERSHIP_SEQUENCE_MISMATCH')
            record = pre.load_json(claim.read_bytes())
            plan = record['plan']
            need(plan['request']['request']['target'] == target and
                 record['reference'] == str(ledger / (pre.digest(
                 plan['request']['request']['operation_reference'].encode()) + '.reference.json')) and
                 record['evidence'] == str(folder / f'{sequence:08d}'), 'FIXED_LEDGER_OWNERSHIP')
            result = self.audit_historical(claim)
            if previous is not None:
                refs = plan['installation'].get('framework_transitions', [])
                if previous == plan['baseline']:
                    need(not refs or refs == consumed, 'UNEXPLAINED_FRAMEWORK_TRANSITIONS')
                else:
                    recovery_continuity(previous, plan['baseline'], plan['installation'], target, ledger)
            else:
                need(not plan['installation'].get('framework_transitions'), 'TRANSITION_WITHOUT_RECOVERY_ORIGIN')
            previous, consumed = result['final_hashes'], plan['installation'].get('framework_transitions', [])
        refs = installation.get('framework_transitions', [])
        if previous is None:
            need(not refs, 'TRANSITION_WITHOUT_RECOVERY_ORIGIN')
        elif previous == current:
            need(not refs or refs == consumed, 'UNEXPLAINED_FRAMEWORK_TRANSITIONS')
            for reference in refs:
                framework_transition(reference, target, ledger)
        else:
            recovery_continuity(previous, current, installation, target, ledger)
        return slots

    def audit(self, claim):
        """Default audit also proves every boundary through today's inventory."""
        result = self.audit_historical(claim)
        record = pre.load_json(checked(claim).read_bytes())
        target = record['plan']['request']['request']['target']
        root, ledger = checked(target['root']), checked(claim).parent.parent
        need(checked(claim).parent == ledger / pre.digest(str(root).casefold().encode()), 'FIXED_LEDGER_OWNERSHIP')
        installation = {'version': record['plan']['installation']['version']}
        if self.host is not None:
            actual_root, installation, actual_ledger = self._installation(target)
            need(actual_root == root and actual_ledger == ledger, 'FIXED_LEDGER_OWNERSHIP')
        self._history(root, ledger, installation, snapshot(root))
        result['current_state_checked'] = True
        return result

    def audit_historical(self, claim):
        """Diagnostic only: validate preserved completion, never current admission."""
        claim = checked(claim)
        claim_bytes = claim.read_bytes()
        record = pre.load_json(claim_bytes)
        outcome = pre.load_json(claim.with_name(claim.name.replace('.claim.', '.outcome.')).read_bytes())
        need(pre.digest(claim_bytes) == outcome['claim_sha256'], 'CLAIM_BYTES_CHANGED')
        plan = record['plan']
        unsigned = {k: v for k,v in plan.items() if k not in {'plan_sha256', 'authorization_binding', 'text'}}
        need(assembly.fingerprint(unsigned) == plan['plan_sha256'], 'PERSISTED_PLAN_MISMATCH')
        binding = deepcopy(plan['request']['request'])
        binding['ids']['review'] = {'plan_sha256': plan['plan_sha256'],
                                  'review_sha256': assembly.fingerprint(dict(unsigned, plan_sha256=plan['plan_sha256']))}
        need(binding == plan['authorization_binding'] and
             record['authorization']['human_authorization']['binding'] == binding and
             record['authorization']['maintenance_scope'] == plan['installation']['scope'],
             'PERSISTED_AUTHORIZATION_MISMATCH')
        external = checked(record['evidence'])
        need(not (external / 'interruption.json').exists(), 'INTERRUPTED_OWNERSHIP')
        need(outcome['status'] == 'TECHNICAL_EXECUTION_ACCEPTED' and outcome['claim'] == str(claim),
             'INTERRUPTED_OWNERSHIP')
        need(pre.load_json((external / 'completion.json').read_bytes()) == outcome, 'OUTCOME_MISMATCH')
        reference = checked(record['reference']).read_bytes()
        need(reference == rt._encoded({'claim': str(claim), 'operation_reference':
             plan['request']['request']['operation_reference']}), 'REFERENCE_MISMATCH')
        data = (external / 'journal.jsonl').read_bytes()
        need(pre.digest(data) == outcome['journal_sha256'] and data.endswith(b'\n'), 'JOURNAL_MISMATCH')
        rows, prefix = [], b''
        for line in data.splitlines(keepends=True):
            row = pre.load_json(line)
            need(row['previous_sha256'] == pre.digest(prefix), 'JOURNAL_CHAIN_MISMATCH')
            prefix += line; rows.append(row)
        expected = dict(plan['baseline'])
        wanted = [('PLAN_VALIDATED', {'plan_sha256': plan['plan_sha256']})]
        for operation in plan['operations']:
            need(expected.get(operation['path'], 'ABSENT') == operation['before_sha256'] and
                 pre.digest(bytes.fromhex(operation['after_image_hex'])) == operation['after_sha256'], 'INVALID_PLAN_IMAGES')
            expected[operation['path']] = operation['after_sha256']
            wanted += [('BEFORE_WRITE_REVALIDATED', {'operation': operation}),
                       ('WRITE_COMPLETED', {'sequence': operation['sequence'], 'after_sha256': operation['after_sha256']})]
        wanted.append(('FINAL_VALIDATED', {'final_hashes': expected}))
        need(len(rows) == len(wanted), 'INCOMPLETE_JOURNAL')
        for row, (event, fields) in zip(rows, wanted):
            need({k: v for k,v in row.items() if k != 'previous_sha256'} == {'event': event, **fields},
                 'JOURNAL_EVENT_MISMATCH')
        need(outcome['final_hashes'] == expected, 'FINAL_MANIFEST_MISMATCH')
        for path, digest in outcome.get('delivery_hashes', {}).items():
            need(pre.digest(checked(path).read_bytes()) == digest, 'DELIVERY_MISMATCH')
        for path, digest in plan['evidence_hashes'].items():
            need(pre.digest(checked(path).read_bytes()) == digest, 'HISTORICAL_EVIDENCE_CHANGED')
        return {'status': 'TECHNICAL_EXECUTION_ACCEPTED', 'final_hashes': expected,
                'current_state_checked': False, 'operational_authority': False, 'action': 'STOP'}
