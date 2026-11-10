# Governance Rules

STATUS: DRAFT
VERSION: {{ADAPT_VERSION}}
PROJECT: {{PROJECT_NAME}}

## Purpose

These rules govern all ADAPT lanes, roles, and AI executions within this instance. Compliance is mandatory. A rule violation detected at runtime must be reported and must halt execution of the violating action.

## Core Rules

### Rule 1 — Director Authority
The Director Lane has intake, routing, source-truth promotion, assignment, gap classification, blocker routing, and certification authority. Director does not have implementation or application source code mutation authority.

### Rule 2 — Mutation Authority
No AI agent may mutate application source files without explicit workcell mutation authority assigned by the Director. Mutation authority is scoped to the workcell's assigned lane (backend files, frontend files, pipeline config, etc.) and must not exceed that scope.

### Rule 3 — QA Independence
QA validation must be performed independently of development. The same human or AI that developed a feature cannot produce QA signoff for that feature without a Director-granted CONSTRAINED exception recorded in the Decision Log. Developer self-validation is never equivalent to QA signoff.

A CONSTRAINED exception relaxes who validates. It never relaxes what the evidence must
rest on — see Rule 13.

### Rule 4 — Source Truth Promotion
Source truth must be explicitly promoted and versioned before it can be used as ground truth. The promotion command is: `Promote {{DOCUMENT_NAME}} as {{SOURCE_TRUTH_VERSION}}`. Promotion requires Director authority and human approval. Unpromoted documents are reference material, not source truth.

### Rule 5 — Evidence Requirement
Claims, completions, and acceptances require evidence traceable to a source requirement
or contract. Unverified claims are not accepted work. See EVIDENCE_STANDARD_BY_ROLE.md in
15_COMMANDS_AND_DRIVERS/.

Evidence has one of three classes, and must be labelled with it:

- **GROUNDED** — produced mechanically and preserved with what produced it: raw command
  or test-runner output with the command that ran, a file hash with the file and
  algorithm, a build log, a captured runtime response. Grounded evidence can be
  re-checked by re-running or re-reading, without trusting whoever recorded it.
- **REVIEWED** — assessed by an actor other than the one whose claim it supports. Review
  catches impossible or inconsistent claims — tests reported passing in a repository
  with no test harness. It does not reliably catch a plausible fabrication, and it does
  not make evidence grounded.
- **ASSERTED** — a statement by the claimant, including an AI summary of evidence. An
  assertion is never evidence of its own truth.

A summary or interpretation must be labelled as such and must reference the grounded
evidence it summarizes. It never replaces it.

No claim may exceed the class of evidence supporting it. A validation result resting on
ASSERTED evidence is not a validation result.

### Rule 6 — Context Traceability
Context packs must reference specific source truth versions and active handoff identifiers. Missing or untraced context must be recorded as GAP-T11 Context Gap before execution proceeds. Stale context from prior cycles must not be passed as current.

Sole first-promotion qualification: SOURCE_AUTHORITY_POLICY.md, First-Promotion
Initial Context Basis. All eligibility, scope, expiry and recovery conditions
apply together. This never validates an ordinary unversioned context pack.

### Rule 7 — Handoff Completion
A lane must emit a handoff before stopping. Silent continuation past the next handoff boundary is forbidden. If a handoff cannot be emitted (missing state, blocked, incomplete evidence), the lane must stop and record a blocker.

Only the eligible Initial Director designation stage in ACTION_PROMPT_DIRECTOR.md
returns its recorded completion to the human without a lane handoff; it writes
only identity/designation evidence, then STOP. Ordinary handoffs are unchanged.

### Rule 8 — Human Approval Gates
Certain actions require explicit human approval before proceeding. See HUMAN_APPROVAL_GATES.md in 15_COMMANDS_AND_DRIVERS/. Required approval gates include: source truth promotion, workcell onboarding, milestone plan approval, code mutation scope approval, release certification, and guardrail override.

### Rule 9 — Guardrail Enforcement
Before executing any bounded action, the AI must check the relevant guardrails in 07_GUARDRAILS/. A STOP_REQUIRED result halts execution of the bounded action. The AI must record the stop condition and route to the appropriate authority.

### Rule 10 — Memory Bank Restriction
Memory Bank documents in 14_MEMORY_BANK/ are reference-only. Memory Bank content must not be treated as live source authority. All authoritative state comes from the control plane, active handoffs, promoted source truth, and accepted contracts.

### Rule 11 — Workcell Identity
Every ADAPT execution must occur under a single, identified workcell identity. Executing under an ambiguous or missing identity is forbidden. See WORKCELL_ONBOARDING_CONTRACT.md for identity binding rules.

For only the eligible Initial Director designation stage of `Run Director intake`,
ACTION_PROMPT_DIRECTOR.md binds Director Lane to the actual Human Owner designation
before the identity is populated. That verified lane basis satisfies this rule
only for its two-file setup scope. It creates no workcell and authorizes no
other Director operation. A lane name or Driver assertion alone is insufficient.

For only the first promotion and its first ordinary context assembly under
SOURCE_AUTHORITY_POLICY.md, the identified Director Lane / Context Steward lane
identities satisfy this rule. No implementation workcell is created or implied.

For the existing Onboard command only, ACTION_PROMPT_ONBOARDING.md, Onboarding
lane identity and scope basis, governs identified Director intake/approval/routing,
Onboarding Orchestrator execution and associated Context Steward assembly.
Their verified lane identities satisfy this rule only within that bounded
procedure, with ordinary versioned context and Gate 3 intact. A claimed lane name
alone is insufficient. Development execution still requires an onboarded workcell,
its approved scope, effective workflow, assignment and handoff. No blanket lane
exception or product mutation authority is created.

### Rule 12 — No Workcell Self-Assignment
Workcells must not assign themselves new work. Work assignments come from the Director Lane via handoffs. A workcell that encounters unassigned work must record a gap or blocker and route to the Director.

### Rule 13 — Evidence Independence
The actor whose success depends on a claim must not be the sole producer and sole
authority for the evidence supporting that claim.

Where a second actor is available, the claim requires REVIEWED evidence at minimum, and
GROUNDED evidence wherever it concerns something mechanically checkable — tests, builds,
hashes, file contents, runtime output.

Where a second actor is not available — a CONSTRAINED exception under Rule 3, or a solo
operator — a mechanically checkable claim requires GROUNDED evidence. Independence that
cannot exist is replaced by evidence that does not depend on trusting the actor. If
grounded evidence cannot be produced — no harness, no environment, no captured output —
the claim is not made: it is recorded as unverified and routed to the Director. A claim
that is not mechanically checkable is recorded as the claimant's judgment, labelled
ASSERTED, and is not presented as verified.

This rule applies to every lane, not only QA.

### Rule 14 — Framework Evolution
The Framework Maintainer is a human authority outside every ADAPT instance, and the sole
authority to dispose framework-learning candidates, authorize changes to the generic
framework, authorize framework upgrades and backports, and declare or advance the
framework version recorded in the framework-root FRAMEWORK_LEARNING_REGISTER.md.

Framework-derived contract files in an instance — those in 00_FRAMEWORK/,
07_GUARDRAILS/, 08_TEMPLATES/ and 15_COMMANDS_AND_DRIVERS/ — change only through an
authorized framework upgrade or backport, recorded in that instance's DECISION_LOG.md.
No lane edits them to resolve a problem it encounters. Instance registers and state are
not affected by this rule.

Any lane may identify a framework-learning candidate. It qualifies when at least one of
these holds: a control failure occurred; a missing invariant was exposed; the situation
carries material governance or execution risk; or comparable friction recurred across at
least two independent cases. One control failure or missing invariant is sufficient. A
contract that is contradictory, incomplete, or permits an ungoverned path is raised as a
GAP-T14 Framework Gap; a qualifying lesson is routed from the Memory Bank. The Director
escalates either to the Framework Maintainer and never authorizes the change.

Promoted changes apply prospectively: future scaffolds inherit them from the canonical
starters, and existing instances are never rewritten automatically — recovery does not
overwrite existing files (DEPLOYMENT_MODES.md).

#### Prospective amendment: bounded external recovery/escalation entry

FW-0006: FLC-005 promoted under Rule 14; release evidence is
VALIDATION/FW0006_RELEASE.md at framework source.
Use requires lawful candidate registration, Maintainer promotion and release;
existing instances additionally require separately authorized adoption. Presence
in an unreleased source tree or test scaffold is not activation or authority.

This entry is external Human Framework Maintainer maintenance, not an ordinary
Director dispatch, a registry command, or permission to execute under stale context.
After activation, the identified Human Director may submit directly to the Human
Framework Maintainer when verified failure prevents ordinary current context.
No ordinary context pack or completed 13-step dispatch is required for this
external submission and receipt alone. Rules 6/9/11 still govern instance work:
the verified human identities bind only this external entry, never a workcell.

Entry packet (all required, with inspectable references, not AI assertions):

- Exact instance identity and resolved root; effective framework version and
  adoption basis. Reject wrong-target, conflicting or inapplicable authority.
- Verified blocked-state evidence: affected state/artifact paths, before SHA256
  hashes, preserved raw diagnostics and failed attempts. Explain the verified
  failure and exactly why ordinary Director context/Steward assembly is unavailable.
- Actual Human Director provenance: original human input, identified Director
  and evidence of that person's applicable Director designation for this instance.
  A Driver, Maintainer or AI claiming Director authority is insufficient. A person
  holding both human roles must explicitly act in each capacity with its basis.
- Applicable Human Maintainer authority: original human direction, identified
  Maintainer, exact target, purpose and expressly approved mutation scope.
  General maintenance approval supplies neither Director provenance nor adoption.
- Exactly one purpose below, named recipient/executor, explicit permitted output
  paths and operations (including an explicit empty canonical-write set), before
  hashes for existing outputs, evidence preservation and completion/handback plan.

Missing, unverifiable, conflicting, changed or out-of-scope inputs require STOP
before any authorized output is written. Recheck identity, authority, hashes and
scope immediately before writing. Preserve the refusal externally; missing
instance write authority never permits inventing a canonical blocker/handoff.

Purpose A: FRAMEWORK_LEARNING_RECEIPT. The actual Human Director submits a
new, explicit framework-learning escalation identifying the qualifying GAP-T14
or Memory Bank lesson and separating instance evidence from the generic proposal.
The Maintainer may record its external receipt at the expressly permitted path.
Receipt must name both humans, input references/hashes, target, qualification,
purpose, scope and result: EXTERNAL_RECEIPT, ORDINARY_DISPATCH_NOT_PERFORMED.
This is a Director-origin escalation arrival for the register's Raising a
Candidate rule, subject to its remaining qualification and recording requirements;
receipt alone neither registers nor promotes an FLC. No canonical instance writes
are permitted. Earlier external reports remain evidence, never retroactively
completed Director handoffs. Complete by returning the receipt and disposition
or outstanding prerequisites to both humans, then STOP.

Purpose B: RECOVERY_BOOTSTRAP_AUTHORIZATION. The two human authorities may
establish a recovery-only task basis and record a bounded authorization externally.
The record must name the proposed recovery executor, exact inputs and before
hashes, future canonical paths/fields/operations, required gates, new recovery
context validation criteria and evidence return destination. This entry permits
only writing that authorization at its expressly permitted external path. It
does not itself assemble a canonical pack, repair state or run a Director/Steward
command. Execution requires a separately effective recovery assembly contract
covering schema, writer ownership, index/staleness handling and completion writes;
if unavailable, record AUTHORIZATION_ONLY / EXECUTION_STOP_REQUIRED and STOP.
Complete by returning the authorization and unmet prerequisites to both humans.

For both purposes the only allowed mutations are the selected external receipt
or authorization record within its approved paths and operations. Unrelated
mutation, canonical state/framework writes, FLC registration and operational
execution are rejected by this entry. Other procedures require their own authority.
Preserve historical artifacts, failed attempts and retry counters unchanged;
never reset counters, resolve blockers, consume/rebind handoffs or resume work.
Entry does not validate stale context or override CONTEXT_GUARDRAIL or Gate 10.
Ordinary execution remains blocked until independently valid current context,
registered blocker resolution with required sign-off, and separately authorized
operational handback satisfy all ordinary gates. Resolution alone grants no
assignment or retry. Recovery assembly/execution is a separate bounded step.

Future scaffolds inherit this single definition through this canonical file;
they receive no historical blocker, OPEN gap, approval or recovery task. Release
and adoption prerequisites above apply even when testing prospective scaffolds.

##### Human-supervised recovery authorization contract

FW-0006 human-governed recovery contract. FLC-005: PROMOTED.
DEFAULT AUTHORIZATION: HUMAN_SUPERVISED.
RECOVERY_MODEL: HUMAN_GOVERNED. This is the sole recovery model.
Autonomous privileged recovery is removed, including optional or future modes.
The 2026-11-02 Rule 14 Maintainer scope correction is recorded prospectively in
FRAMEWORK_LEARNING_REGISTER.md and VALIDATION/FW0006_HUMAN_GOVERNED_SCOPE.md
at framework source; historical FLC-005 evidence remains intact.
This cleanup grants no recovery permissions and leaves real execution disabled.
All existing Rule 14 entry, assembly, mutation, gate and handback safeguards
remain mandatory. Ordinary ADAPT workflows remain unchanged.

FW-0008 recovery ledger continuity correction (FLC-007, promoted for prospective release):
Historical completion validation and current admission are separate. A completed
recovery remains historically valid after a separately approved framework adoption.
Current admission requires the complete ordered chain from every prior completed
inventory to the next reviewed baseline and today's independently verified installation.
Only hash-bound installation-supplied adoption references qualify: original separate
Maintainer response and exact review, issued-source bytes, full backup and inventories,
exact approved images, append-only decision insertion, installation intents, completion
and distribution validation must all agree. Multiple successive upgrades are supported;
unexplained changes or missing, corrupt, mismatched or incomplete evidence require STOP.
Bind and recheck all dependencies through the existing plan and authorization fields.
Version declarations and Decision Log entries alone confer no continuity or authority.
Audit every contiguous fixed-ledger slot first; interrupted recovery always blocks entry.
Preserve original claims, journals, outcomes, approvals, ownership and replay protections.
Never reconstruct or rewrite historical evidence. Historical-only audit is diagnostic
and cannot authorize execution. Every new recovery action still requires its own exact
plan and applicable human approvals. Release and instance adoption remain separate.

Governance states are distinct: NORMAL OPERATION, RECOVERY REQUEST,
RECOVERY PLAN REVIEW, BOUNDED RECOVERY EXECUTION, RECOVERY VALIDATION,
BLOCKER RESOLUTION and OPERATIONAL HANDBACK. A recovery result never implies
ordinary readiness, Director or Maintainer approval, blocker resolution, retry
reset, context activation, handoff consumption, framework publication or adoption.
One recovery action requires one explicitly reviewed, scoped plan; separate
operations require separate authorization and operation references. Missing or
conflicting evidence requires STOP. Existing workcell identities and roles apply.

Recovery follows this sequence:

1. Detect error or deadlock and stop the affected action.
2. Capture available evidence and report the failure, scope, known cause or uncertainty.
3. Recommend the smallest supported bounded action and generate the exact plan.
4. Present issue, cause, impact, recommended action, files, expected result and risk.
5. Capture explicit human approval for this exact plan in each applicable capacity.
6. Execute only the approved action with current-byte and scope checks.
7. Independently validate the final state and preserve journal/evidence.
8. Report the result and STOP. Blocker resolution and handback remain separate.

Read-only reporting requires no special approval or valid ordinary context.
Unsupported recovery yields a diagnostic report and human resolution instructions;
never fabricate a generic fixer. Reports distinguish DIAGNOSTIC_ONLY,
READY_FOR_HUMAN_REVIEW, APPROVED_FOR_EXACT_ACTION, RECOVERY_VALIDATED,
RECOVERY_REFUSED and RECOVERY_INTERRUPTED using existing result fields.

**Normal human interaction.** ADAPT prepares plan and approval evidence; humans
review readable changes and explicitly approve or reject through normal ADAPT
interaction. No separate application, terminal, OS account, operator isolation,
TrustedHost, approval server, GitHub trust chain, identity provider, cryptographic
ceremony, manually composed JSON or manual hash calculation is required.
ADAPT records the actual response; a model may capture it but must never invent it.
Missing approval: STOP, no mutation. Ambiguous approval: STOP, request clarification.
Changed plan: STOP, new review required. The organization owns human identity and
access to the normal interaction. Conversational approval is not independently
authenticated. This design claims no cryptographic provenance or protection
against a hostile agent with unrestricted filesystem and approval-record access.

A recovery packet must never authorize itself. A packet, Decision Log entry,
local approved=true value, filesystem access or version header cannot enable
canonical writes. The maintenance entry must receive explicit human input
separately; it must never extract authorization from the recovery packet or
manufacture approval records. Missing authorization requires STOP.

**Required binding and safeguards.** Bind the exact resolved instance/root and
identity, recovery workcell or external lane, named executor, explicit purpose
and task, approved paths/fields/operations, current source and before-image
SHA256 hashes, applicable approved gates, evidence references, completion
destination, operation reference and preserved audit. Preserve human authority
and role/designation evidence for each applicable capacity, validity and current
withdrawal checks. One human may exercise both capacities in one interaction with explicit records
for each, sharing the original response reference. Distinct actual authorities
require distinct approvals and response references. A local declaration establishes neither identity nor permission to write.

Missing, conflicting, expired, withdrawn or out-of-scope authorization, missing
evidence/gates, or changed source/before-image hashes requires STOP. Review the
bounded plan with the human; obtain separate authorization for its exact changes
and recheck current evidence and hashes immediately before any future lawful
write. Context guardrails, canonical allowlists, mutation permission enforcement,
journaling and interruption detection remain mandatory. Preserve refusals and
history. Blocker resolution and operational handback remain separately governed.

**Read-only development API.** `VALIDATION/recovery_supervised.py` exposes
`SupervisedVerifier(maintenance_scope).verify(packet, human_authorization=...)`.
The separate maintenance scope binds `target`, `workcell`, `executor`,
`required_gates` and `authorities` (Human Framework Maintainer and applicable
Human Director). The current Purpose B contract requires both capacities.
The request binds `target`, `workcell`, `purpose`, `task`, `executor`, `writes`,
`inputs`, `evidence`, `ids`, `completion`, `gates`, `operation_reference` and
`audit_reference`. Separately supplied authorization must bind all those values.

Authorization includes `binding`, `synthetic`, `approved_at`, `checked_at`,
`not_before`, `expires_at`, `withdrawn`, `audit_reference`,
`audit_preservation_reference` and explicit capacity `approvals`. Each approval
names `role`, `human`, `approved`, `approved_at`, `role_basis_reference` and an
`approval_reference`; Director approval also names `designation_reference`.
These are human-controlled declarations and evidence references, not an ADAPT
authentication protocol. The operator remains responsible for authenticating
the human under its normal access policy and ensuring the entry captures their actual instruction.

Missing or conflicting declarations return AUTHORITY_UNVERIFIED. Consistent
ones return SUPERVISED_EVIDENCE_VALID (SYNTHETIC_VALID for fixtures, otherwise
DECLARED_HUMAN_APPROVAL). This means scope consistency only. Every result has
operational_authority=false. The verifier performs no file/network I/O and has
no writer link. `recovery_authority.py` separately checks local evidence bytes,
source/before-image hashes and governance capability claims; it authenticates
no humans and never grants writes. Preflight and assembly remain required.
The original plan-review and execution APIs retain their synthetic-only writer
boundaries. VALIDATION/recovery_operational.py separately provides a bounded
maintenance entry and writer. It prepares the existing authorization shape from
actual responses captured through normal ADAPT interaction. The existing host
interface remains an integration option for this same model, with no isolation
requirement. See distributed TOOLS/README.md for usage and preserve/STOP policy.
Acceptance fixtures simulate human responses and never establish actual consent.

**Release, adoption and scaffolds.** Lawful FLC-005 promotion, FW-0006 publication,
installation and separately governed existing-instance adoption remain required
before operational use. Local headers or evidence claims alone cannot satisfy
these gates. MODE_A and MODE_B inherit this contract through the
canonical starter and receive all nine recovery modules through verified distribution. They require no
approval provider infrastructure, host enrollment or external trust-policy
configuration. Never seed historical approvals, blockers or recovery tasks in
fresh scaffolds. Distribution grants no action approval or existing-instance adoption.

##### Purpose B completion: bounded recovery context assembly

FW-0006: This is the single normative assembly contract.
It becomes applicable only after lawful release and installation/adoption of
this capability in the exact target. FW-0005, a proposal copy, version text alone
or an external authorization alone cannot enable it. It cannot authorize its
own candidate registration, release or adoption. The separate operational entry implements bounded assembly, scope validation
and journaled writes: DEPLOYMENT_ACCEPTANCE_REQUIRED means applicable release,
installation/adoption and supported filesystem conditions, not human authentication
or a separate operator deployment. These mechanisms do not
authenticate human identity in a shared agent process. Multi-file atomicity and
unconditional power-loss durability are unsupported. The requirements below
remain mandatory for every separately authorized executor.

**Entry and executor.** All Slice 1 entry-packet requirements remain mandatory.
Bind exactly one resolved instance root and identity, one purpose
RECOVERY_BOOTSTRAP_AUTHORIZATION, one bounded assembly task and one explicit
path/field/operation allowlist. Verify installed governing contract hashes and
effective release/adoption evidence; original Human Maintainer direction and
Human Director designation/submission; the external authorization's path/SHA256;
current failure diagnostics and attempt history; and the documented recovery
reason ordinary Director context/Context Steward assembly is unavailable.
Approval must expressly authorize this canonical assembly, not merely the
external authorization's creation. Require all applicable human gates and the
completion/evidence destination before any canonical write.

The writer is the identified Human Framework Maintainer or the explicitly named
operator delegated by that human, acting solely in recovery Context Steward
capacity for this task. Record actual operator identity and original delegation
path/SHA256. An AI may carry out that delegation but cannot designate itself as
Human Maintainer or Human Director, approve gates, or expand its scope. This
verified recovery lane basis satisfies Rule 11 only for this bounded operation;
it creates no workcell. It is external maintenance, not ordinary Context Steward
dispatch or a new registered command. Do not set CurrentAuthority to acquire
authority, record fictitious intake/dispatch, or consume any pending handoff.
For Rule 6 only, the bound external authorization replaces an active task
handoff reference for this assembly; registered source traceability is unchanged.

Before writing, read current canonical PROJECT_CONTROL_PLANE.md, its schema,
DIRECTOR_IDENTITY.md, SOURCE_TRUTH_VERSION_LOG.md and registered source document,
relevant DECISION_LOG.md entries, GAP_REGISTER.md, BLOCKER_REGISTER.md,
CONTEXT_INDEX.md, STALE_CONTEXT_REGISTER.md, related packs/deltas and handoff
inventory/content. Use their actual instance-relative paths in the evidence.
Require a readable, schema-consistent control plane and a current registered
source version matching SourceTruthVersion. Missing/unregistered source,
unreadable state, ambiguous identity/history, inconsistent control plane or an
unmet gate requires STOP; this assembly contract cannot repair those conditions.
Verify the failure evidence against that current state, including exhausted
attempts. Historical findings remain historical, not present-state assertions.

**Recovery context schema and selection.** Use
08_TEMPLATES/CONTEXT_PACK_TEMPLATE.md with all existing sections/header fields.
STATUS remains DRAFT (the document status); index lifecycle is separate. Set
WORKCELL_ID to the verified recovery Context Steward lane identity, HANDOFF_ID
to NONE (external task basis), SOURCE_TRUTH_VERSION to the verified current
registered version, and CONTEXT_SIZE to a justified existing size tier within
the declared budget. Active Handoff Summary records NONE as the task handoff,
the external authorization reference, and pending handoffs as observed evidence
only. Scope Declaration carries the exact authorized operations and exclusions.
The Context Steward Note must identify recovery assembly and its delegated
writer rather than falsely claiming ordinary dispatch.

Add a Recovery Basis section containing target identity/resolved root, purpose,
task, original human authority references, executor/delegation, installed
capability/release/adoption references, failure reason, gates, input manifest,
allowlist, validation criteria and return destination. The input manifest has
one row per selected source: resolved path, artifact ID/version if any, SHA256
of raw bytes, verification time, evidence class, inclusion reason and use as
current canonical state or historical recovery evidence. External paths must be
explicitly approved; canonical paths must resolve within the exact instance.
Reject traversal, symlink/reparse redirection, alias collisions and wrong-target
paths. Required missing or unsupported prerequisites cannot be replaced by AI
inference. Verify history against originals; preserve all attempts and findings.

Explicitly verified failure logs, prior attempts, superseded packs and archived
handoffs may be selected as historical recovery evidence with their path/SHA256
and limitations. They never become current source truth, an active task or
ordinary executable context. Keep stale ordinary packs invalid. Current state
must be read directly from canonical artifacts, never reconstructed from a
stale pack. Record relevant decisions, open gaps/blockers, constraints, excluded
items and known limitations using the existing template sections.

**Canonical writes and allocation.** The complete possible write surface is:

| Path | Permitted operation, only when expressly authorized |
|------|---------------------------------------------------|
| 10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-{sequence}.md | Create one recovery-only pack; never overwrite a prior pack |
| 10_CONTEXT_ECONOMY/CONTEXT_INDEX.md | Append its row; update only authorized affected lifecycle/Notes cells |
| 10_CONTEXT_ECONOMY/STALE_CONTEXT_REGISTER.md | Append verified OPEN stale findings with fresh SC-IDs; append explanatory Notes to specifically authorized existing rows |
| 10_CONTEXT_ECONOMY/CONTEXT_DELTAS/CD-{sequence}.md | Create one actual assembly delta using CONTEXT_DELTA_TEMPLATE.md |
| 06_HANDOFFS/ACTIVE/HO-{sequence}.md | Create one recovery completion handoff to responsible Director using HANDOFF_TEMPLATE.md |
| 02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md | LastContextDelta = actual CD-ID; LastAction and appended Notes describing this operation only |

The authorization must enumerate exact paths, fields, before values/hashes,
after values or constrained append content, and operations within this table.
All other canonical writes are rejected, including governance registers,
application code, source promotion, framework files, blocker status/counters,
Authority/Identity/State fields and NextExpectedAction. Do not invent an
Authority field or put CP-ID/PENDING_DELTA in LastContextDelta. No change to
Blocked, ActiveBlockers, ActiveGaps or ExecutionReadiness is authorized.

Allocate CP/CD/SC/HO sequences independently by inspecting actual records and
files in all relevant folders, including archived/consumed handoffs and prior
interrupted outputs. Ignore commented examples, never reuse an issued ID, and
choose the next unused numeric sequence above the maximum issued number,
preserving existing local padding. Stop on duplicate/conflicting IDs. Bind exact
allocated paths into authorization before writing; a collision or concurrent
allocation requires STOP and separately lawful reauthorization, not overwrite.

Index columns remain unchanged: use the verified recovery lane, Handoff ID NONE,
current source version, actual size/date and Notes explicitly stating
RECOVERY ONLY, task/authorization path and no ordinary execution authority.
During incomplete assembly use STALE; after validation retire the recovery pack
as ARCHIVED, retained for audit. It is never indexed ACTIVE for ordinary use.
Existing stale ordinary rows stay STALE (or SUPERSEDED only on verified version
supersession and explicit scope). Do not mark stale records RESOLVED or
ACCEPTED_RISK merely because a recovery pack exists. An ordinary replacement and
its own lawful procedure are required. No new lifecycle statuses are introduced.

The CD uses the recovery lane identity and PRECEDING_CONTEXT_PACK_ID = this new
CP-ID, the input for completion recording. State Changes and New Artifacts
Produced list actual authorized creations/field changes, with authorization
traceability; use existing OTHER for context artifacts where needed. Superseded
Items and Downstream Impact identify actual invalidations, or explicitly none.
Never claim blocker resolution, retry reset, source promotion or resumed work.
Record processing notes and attach the real CD-ID to the outgoing handoff.

**Validation, completion and interruption.** Stage proposed outputs externally.
Before any canonical write, validate the whole proposed write set, schemas,
references, budget, authority/gates, ID availability and source SHA256 bindings.
Missing or invalid authority/source evidence produces STOP without canonical
mutation. Changed input hashes produce STOP. Recheck all unchanged inputs and
expected before images immediately before each write; for authorized outputs
already written compare the journaled after hash. Reject out-of-scope writes.
Serialize the bounded operation; inability to exclude concurrent writers is STOP.

Preserve an external append-only operation journal at the authorized evidence
path: input manifest, planned writes, each completed write's before/after SHA256
(ABSENT for new paths), raw validation results and any interruption. The pack
describes the pre-write snapshot; final output hashes belong in the external
completion manifest, avoiding self-hash/circular references. Revalidate final
schema/index/stale/delta/handoff/control-plane consistency and all unchanged
inputs. Explicitly distinguish authorized trace/index changes from stale inputs.
No completion claim is permitted for a partial or invalid result. Keep the pack
STALE until validation; archive it only on successful bounded completion.

The completion handoff uses existing fields/sections, names recovery Context
Steward as sender and the responsible Director as recipient, references the
CP/CD and external evidence manifest, lists remaining blockers and all unmet
operational prerequisites. Source version remains current; no unrelated handoff
is consumed, moved, rebound or rewritten. Do not make the emitted HO the control
plane ActiveHandoff. Return the completion manifest, exact authorized mutation
diffs/hashes, validation evidence and HO path to the responsible Human Director
and Human Maintainer, then STOP. Delivery records evidence, not ordinary dispatch.

Interrupted recovery preserves all outputs, original evidence and counters;
record actual partial writes externally and STOP. Never roll back, overwrite,
reuse IDs or resume automatically. Continuation/correction requires a separately
lawful authorization bound to the observed partial state and fresh hashes;
requirements outside this table need another applicable procedure. No successful
handoff or archive transition may be fabricated for an interrupted operation.

Completion does not resolve any blocker, reset exhausted attempt counts,
consume unrelated pending handoffs, promote source truth, modify ordinary
application code, grant general execution authority, override unrelated human
gates, activate stale ordinary context, trigger automatic workcell execution or
launch the next registered command. Separate registered blocker resolution with
required sign-off, an independently current ordinary Context Steward pack and
separately authorized operational handback are mandatory before ordinary work.
The recovery pack is retained evidence only and cannot supply that handback.
