# ADAPT Operator Tooling v1

Self-contained Python 3.9+ standard-library distribution. Git is required only
for evidence. New scaffolds copy this directory verbatim; no development
repository, experiments, absolute developer paths or network services are needed.
The operator commands are optional and read-only; distribution is mandatory.

FW-0006 scaffolds additionally distribute all nine `VALIDATION/recovery_*.py`
modules declared in this manifest's `instance_files`. Their relative imports use
the sibling modules and this TOOLS distribution; recovery requires Python 3.10+.
Original prototype APIs retain their synthetic-only boundaries. The separate
HUMAN_GOVERNED operational entry requires verified release/installation evidence,
separately governed existing-instance adoption and exact human action approval.
Distribution itself grants no execution authority or human authentication. Preflight retains its historical NON_DISTRIBUTED_PROTOTYPE API
label; this is not capability evidence. Windows file fsync does not establish
directory-entry durability on power loss. Hash chains do not authenticate humans.
Use the framework's `VALIDATION/distribute_tools.py --framework <source>
--instance <instance> --verify` to check both TOOLS and recovery files against
trusted source hashes. Doctor checks file presence, not payload hashes. The
development verifier and tests are not shipped; module imports and ordinary
operator commands do not need a framework repository or PYTHONPATH.

```powershell
python TOOLS/adapt.py state --instance . --json
python TOOLS/adapt.py doctor --instance . --json
python TOOLS/adapt.py prompt next --instance . --json
python TOOLS/adapt.py evidence --instance . --repo ../PROJECT --file src/example.py --json
```

Run these inside the ADAPT directory, or provide explicit paths from elsewhere.
`--instance` directly contains `02_DIRECTOR_LANE`; `--repo` is the exact Git root.
`--file` is repeatable and repo-relative. Omit `--json` for human output.

## Inputs, outputs and permissions

| Command | Inputs | Outputs |
|---|---|---|
| state | Control-plane Markdown table | Exactly 21 strings in schema order; cell padding trimmed |
| doctor | Packaged inventory, instance schema, control plane, handoff and registers | Stable ID/status/message/source diagnostics; unchecked conditions explicit |
| prompt next | Recorded control-plane, registry, identity, scope, handoff, member action prompt, decisions, approvals, version log, context hashes and incoming evidence | Bound operator invocation preview or BLOCKED; never executes or grants approval |
| evidence | Explicit instance/repo roots and bounded declared files | Git root/branch/HEAD/status/changed paths, artifact existence and SHA256 hashes |

The decision contract is `15_COMMANDS_AND_DRIVERS/TOOLING_DECISION_CONTRACT.md` in
the instance. Populate its handoff binding table from existing authoritative
records only. Do not write binding rows to obtain a desired output. NextExpectedAction
and Next Action Suggested never choose or authorize execution. Supported previews
are Director-bound atomic dispatch to exact Backend Developer or Frontend
Developer identities. Other roles/commands/direct lane invocations are BLOCKED.

Context File Integrity declares bounded artifact hashes; mismatch is BLOCKED.
LastContextDelta must be NONE in the supported subset; later deltas require a
Context Steward review that v1 cannot deterministically establish.
Recorded ACTIVE decisions and approval references are checked as pointers, not
authenticated signatures. The invocation preview explicitly retains semantic
scope, adequacy, guardrail and human authenticity checks for the receiving agent.
Any open/unresolved blocker or gap is conservatively refused when work-item
applicability is unknown; this does not change Stop Rule 15's scoped behavior.

## Failure and evidence semantics

- Exit 0: output without a failed check, not readiness or certification.
- Exit 1: invalid/missing data, failed diagnostic, unsupported or BLOCKED preview.
- Exit 2: argparse usage error on stderr.

JSON failures contain stable diagnostic IDs with explicit source references.
PASS/WARN/FAIL describe checks. UNVERIFIED and applicability outcomes
NOT_CHECKED/NOT_EXERCISED are never implicit passes. Doctor checks required
inventory, the 21-field schema, enum/version/date values, active reference/binding
and CP-C01–06/09–11 where mechanically available. CP-C07 activity history and
semantic CP-C08 routing authorization are not certified. Templates and legitimate
instructional placeholders are retained; required live fields are populated at
scaffold completion. Doctor does not infer Lite module activation from absence.

Absolute artifact references, URLs, traversal and escaping symlinks fail. Each
artifact is limited to 2 MiB; references are bounded and never scan unrelated
roots. Evidence runs only rev-parse, status and branch queries, with optional
locks/fsmonitor/untracked cache disabled, submodule internals excluded and a
20-second timeout. No shell, hooks, fetch, commit, push, repairs or network calls.
No file contents, patches, credentials or raw process errors are dumped. Paths
and hashes themselves may be sensitive metadata; choose shared references carefully.

No hidden database/cache, no bytecode writes, no second control plane. Concurrent
writes and symlink races are not atomic. Git status size is not bounded; hashes
cover declared files only. Cross-platform absolute root output varies by OS.

## Distribution and evolution

MANIFEST.json names every shipped runtime/documentation file and its SHA256.
The source repository pins TOOLS to LF with .gitattributes so checkout newline
settings do not invalidate the distribution hashes.
supporting_modules/instance_inventory.json is a versioned structural inventory,
not a second state representation. New scaffolds execute the framework's narrow
copy/verifier; existing TOOLS targets are never overwritten automatically.

The sole implementations are supporting_modules/operator.py and state_reader.py.
Experimental entry paths in the development repository are compatibility shims.
Tests and the development distribution helper are not shipped to instances.
Changes require the existing Framework Maintainer process and explicit authorized
upgrade/backport for old instances. No command grants human approval, QA signoff,
release certification or action execution authority.


## FW-0006 recovery payload

Both scaffold modes install nine sibling VALIDATION modules: recovery_preflight,
recovery_assembly, recovery_runtime, recovery_structural, recovery_supervised,
recovery_authority, recovery_plan_review, recovery_execution and recovery_operational. They share the
existing operator/state reader and use only the Python 3.10+ standard library.
MANIFEST.json instance_files verifies their exact source bytes. These
APIs do not grant action approval, publication or adoption. The default
contract is HUMAN_SUPERVISED: one separately reviewed and authorized plan per
action, then validation and STOP. Human authentication is the deployment
operator's responsibility. Installed prototypes retain fixed synthetic boundaries;
no machine-specific permission, historical approval or operational history ships.
The manifest framework_version identifies the original tooling baseline; the
learning register alone declares the effective framework version. The manifest
release_framework_version identifies this distribution. Release evidence is
VALIDATION/FW0006_RELEASE.md at framework source; distribution grants no adoption.


## Operational recovery operator instructions (FW-0006)

`VALIDATION/recovery_operational.py` exposes the existing `MaintenanceEntry`.
The sole model is HUMAN_GOVERNED; HUMAN_SUPERVISED remains the compatible API
label. ADAPT detects and stops, diagnoses, proposes an exact action, presents
readable review, captures human approval, executes, validates, reports and STOPs.
`diagnose(instance, failure_id=..., failed_action=..., observed_error=...,
evidence=..., cause=..., request=...)` is read-only. It works without an entry
or valid ordinary context. Unsupported actions produce diagnostic-only human
resolution guidance; failed bounded prerequisites produce RECOVERY_REFUSED.

Normal integration constructs `MaintenanceEntry(installation=record,
ledger=external_directory, interaction=capture_actual_human_responses)`.
ADAPT prepares the record from existing release/adoption, inventory and role
records. Humans do not compose JSON or hashes. `preview(request)` produces the
readable summary, exact diffs, before/after bytes and fingerprints automatically.
`execute(plan)` presents that exact review through the callback. The callback
captures actual human input in the normal ADAPT interaction as a list of decisions
with `decision=APPROVE_EXACT_ACTION`, the presented `plan_sha256`, `human`, explicitly
exercised `capacities`, and `source_reference` to the original response. Rejection,
ambiguity, silence and wrong capacity yield no mutation. A changed plan requires
new review. Never infer approval from packet content or an AI-created claim.

The existing scope binds target, workcell, executor, required_gates, authorities;
normal integration also supplies `role_evidence` by capacity with existing
role_basis_reference and Director designation_reference. The adapter prepares
validity timestamps, each capacity record, exact binding and audit references.
One actual human may explicitly exercise both capacities in one response; distinct
authorities require distinct responses. Original responses are preserved with
authorization in the existing claim. `current(plan)` rechecks the captured decision;
`withdraw()` records a withdrawal and stops subsequent writes. Existing host
integrations can still provide installation/authorize/current using the same
verifier/writer. No extra approval subsystem or dispatcher is introduced.

There is no requirement for process isolation, protected OS accounts, a separate
terminal or application, TrustedHost, GitHub trust infrastructure, approval
servers or identity providers. Organization access policies own human identity.
Conversational approval is not independently authenticated, cryptographically
proven or tamper-proof. This design does not protect against a hostile agent with
unrestricted filesystem and approval-record access. This is the explicit reduced
assurance selected by the Maintainer, not a completed authentication test.

The installation record still binds target, version, release_reference,
adoption_reference, installation_reference, installed_hashes, scope,
evidence_class and conditions. Hashes cover manifest payload, manifest and six
governing contracts. Publication/adoption decisions are not inferred from local
headers. Evidence class HUMAN_SUPERVISED denotes captured human declarations;
TECHNICAL_TEST (constructor `synthetic=True`) labels simulated acceptance fixtures.
Neither label authenticates identity or authorizes release/adoption.

Use a fixed, resolved external ledger on the same local volume, preserved for the
adoption lifetime. Conditions are exactly `{filesystem: LOCAL,
exclusive_operator: true, power_loss_uncertainty: false}`. Exclusive ownership,
source/byte checks, aliases/reparse/hardlink refusals, fsynced evidence and replay
refusal remain mandatory. Concurrent outside writers and network filesystems are
unsupported. File fsync does not promise identical directory durability on every
OS; Windows power-loss directory persistence and multi-file atomicity are not
guaranteed. Interrupted evidence must be preserved for human assessment.

Request envelope: kind STRUCTURAL or CONTEXT, request (the existing supervised
BINDING_KEYS), evidence_root (disjoint current evidence), parameters. STRUCTURAL
parameters select either `{blocker: BLK-nnn}` for the existing eleven-column Notes
to Blockers relocation, or `{register: CONTEXT_INDEX, operation: NORMALIZE_TABLE_PLACEMENT}`
for contiguous placement of complete unique eight-column Index rows. The latter
preserves all row values, prose and comments; it cannot change lifecycle status.
No other structural operation is supported. Bind the complete current inventory
and exactly the blocker-register placement write. CONTEXT parameters are the
existing six-path assembly packet plus gates. Its assembly selection uses
`format=operational-v1`; its authorization evidence is only a task basis containing
purpose, target, task, executor and gates. It grants no authority. Human decisions
arrive later through the normal human interaction, bound to the rendered exact plan. The
recovery pack links the durable operation reference to those original decisions.
Original diagnostic history and current source/inventory must be hash bound.
The only supported size selection is the existing justified XL tier and byte
ceiling. Recovery output remains DRAFT/ARCHIVED with OPEN stale findings; it does
not activate ordinary context or consume a pending handoff.

Use `preview` immediately before review. Preserve the full returned plan; never
edit an approved plan. Each action needs a new task/operation reference, review
and authorization. Structural repair and context assembly are two invocations.
The second reads the repaired bytes after validated completion of the first.
A successful prior slot is retained, with its journal and outcome; a later slot
requires an exact audit and matching current prior final hashes. Any interrupted,
conflicting or mismatched slot blocks further entry for that target. Deployment-
wide exclusive operation-reference claims forbid reuse, including after refusal
following consumption. Never delete claims, outcomes, journals or locks, steal
ownership, change the ledger, resume, retry or roll back automatically.

Multi-file context assembly can stop after any prefix of seven writes. Preserve
actual partial bytes, pending external images, intent/completion journals and
interruption evidence and STOP for human assessment. This entry deliberately
provides no interrupted-instance continuation facility. It rejects that condition.
Completed execution publishes final hashes and journal/evidence return to both
capacities. Those returns grant no ordinary operational handback, blocker closure,
retry reset, publication or adoption. Use the existing separately governed
resolution, current ordinary context and handback procedures afterward.

Distribution never enables recovery. After lawful FW-0006 publication, install
through the existing exact-scope installation/adoption process, verify source and
installed bytes and contracts, then capture the exact human-approved action. A version header
or this payload alone cannot substitute for publication or adoption.
