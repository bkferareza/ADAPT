# ADAPT Operator Tooling v1

Self-contained Python 3.9+ standard-library distribution. Git is required only
for evidence. New scaffolds copy this directory verbatim; no development
repository, experiments, absolute developer paths or network services are needed.
The operator commands are optional and read-only; distribution is mandatory.

Proposed FW-0006 development scaffolds additionally distribute the three
`VALIDATION/recovery_*.py` modules declared in this manifest's `instance_files`.
Their relative imports use the sibling modules and this TOOLS distribution;
Python 3.9+ standard library is sufficient. They remain synthetic-only prototypes.
No production recovery, human authentication, release or instance adoption is
approved by distribution. Effective FW-0005 and real-instance execution refusal
remain in force. Preflight retains its historical NON_DISTRIBUTED_PROTOTYPE API
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


## Prospective recovery payload

Both scaffold modes install nine sibling VALIDATION modules: recovery_preflight,
recovery_assembly, recovery_runtime, recovery_structural, recovery_supervised,
recovery_authority, recovery_plan_review, recovery_execution and recovery_operational. They share the
existing operator/state reader and use only the Python 3.10+ standard library.
MANIFEST.json instance_files verifies their exact source bytes. These development
APIs do not grant production execution, publication or adoption. The default
contract is HUMAN_SUPERVISED: one separately reviewed and authorized plan per
action, then validation and STOP. Human authentication is the deployment
operator's responsibility. Installed prototypes retain fixed synthetic boundaries;
no machine-specific permission, historical approval or operational history ships.
The manifest framework_version identifies the original tooling baseline; the
learning register alone declares the effective framework version. Proposed
recovery metadata does not advance that version.


## Operational recovery operator instructions (prospective FW-0006)

`VALIDATION/recovery_operational.py` exposes `MaintenanceEntry(host)`; no default
host exists. `preview(request)` reads the exact instance and returns the plan,
raw before/after hex, unified diffs, current inventory, installation bindings and
SHA256. `execute(plan)` calls `host.authorize(plan)` to present that exact review,
requires both explicit capacity decisions, rechecks `host.current(plan)` before
every mutation, validates actual results and returns STOP. `audit(claim)` checks
persisted completion/journal consistency; it never resumes an operation.

The host belongs in the organization's existing operator-controlled maintenance
process/account. That process must protect its Python interpreter and imports,
host code/configuration, current human input and withdrawal channel, original
role/designation evidence, published-release/installation/adoption evidence and
fixed external ledger from ordinary agent access. Only the separately authorized
operator may launch it. Reuse existing deployment permissions. No identity
provider, new service, GitHub approval infrastructure or Windows TrustedHost is
required. A shared interpreter/account, terminal prompt, OS username, JSON file
or `agent_access=EXCLUDED` declaration does not establish this boundary. The
host contract assumes independently established controls; it does not verify ACLs
or authenticate people. A deployment without those controls is INELIGIBLE.
This source workspace has no demonstrated protected entry. Do not use its shared
agent session to create real approval records or claim genuine consent acceptance.

Host interface (operator integration, never recovery-packet configuration):

- `ledger`: fixed resolved external directory on the same local volume as targets;
  preserve it for the full adoption lifetime. Never rotate it to permit replay.
- `evidence_class`: HUMAN_SUPERVISED for actual protected human input;
  TECHNICAL_TEST exclusively for disposable acceptance with simulated decisions.
- `installation(target)`: independently read current adopted release and exact
  installation, returning target, version, release_reference, adoption_reference,
  installation_reference, installed_hashes, evidence_class, scope and conditions.
  The source module docstring/API lists exact required fields. Installed hashes
  cover all manifest files, manifest itself and six governing contracts. References
  point to original existing release/adoption decisions; packet claims cannot
  replace them. `scope` is the existing SupervisedVerifier configuration.
- `authorize(review)`: show the full exact review including changes, fingerprints,
  target, sources, gates, risks and completion to the human. Return separately
  captured existing `{maintenance_scope, human_authorization}` evidence only after
  both Human Director and Human Framework Maintainer explicitly approve. The same
  human may make the two separate decisions. Never generate that evidence on behalf
  of a human. Bind `review.authorization_binding` exactly. Refusal returns no grant.
- `current(review)`: reread current approval/withdrawal state and return the existing
  authorization shape; missing, expired, changed or withdrawn decisions STOP.

Supported conditions are LOCAL filesystem, exclusive operator access, excluded
ordinary agent access and no unresolved power-loss uncertainty. The host declares
these as `{filesystem: LOCAL, exclusive_operator: true,
power_loss_uncertainty: false, agent_access: EXCLUDED}` only after verifying the
actual deployment. Network/multi-host filesystems, concurrent outside writers,
untrusted interpreters, aliases/reparse/hardlinked files and uncertain power-loss
recovery are unsupported. File fsync and local exclusive create are used; Windows
directory-entry persistence on power failure is not guaranteed. There is no
multi-file atomicity, hostile-OS protection or automatic recovery from power loss.

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
arrive later through the protected host, bound to the rendered exact plan. The
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
installed bytes and contracts, then establish the protected host. A version header
or this proposed payload alone cannot substitute for publication or adoption.
