# Source Authority Policy

STATUS: DRAFT
VERSION: {{ADAPT_VERSION}}
PROJECT: {{PROJECT_NAME}}

## Purpose

Defines what constitutes source truth in this ADAPT instance, how it is promoted, and how it governs work.

## Source Truth Definition

Source truth is any document explicitly promoted and versioned by the Director Lane that governs ADAPT decisions, requirements, acceptance criteria, or architecture. Source truth is the authoritative input for all workcell work.

## Promotion Process

To promote a document as source truth:

1. Issue the command: `Promote {{DOCUMENT_NAME}} as {{SOURCE_TRUTH_VERSION}}`
2. Director Lane validates the document is readable and complete
3. Human approval is required (see HUMAN_APPROVAL_GATES.md)
4. Director records the promotion in SOURCE_TRUTH_VERSION_LOG.md
5. The document is assigned a version identifier: e.g., SOURCE_TRUTH_V0.1
6. All downstream work must trace to the promoted version

## First-Promotion Initial Context Basis

The existing `Promote {{DOCUMENT}} as {{SOURCE_TRUTH_VERSION}}` command has one
governed alternative to its ordinary context-pack prerequisite. This initial
basis is not an ordinary context pack or a general authorization token. It is
limited to preparation, recording, required extraction and completion evidence
for the FIRST promotion. All later promotions require valid ordinary context.

### Eligibility: all conditions required

- A valid canonical-derived instance with a known frozen framework version,
  source reference and hashes of the governing contracts; the full control plane
  passes CONTROL_PLANE_SCHEMA.md consistency rules.
- `SourceTruthVersion = NONE`, `CurrentPhase = INITIALIZED`; `ActiveWorkcell`,
  `ActiveHandoff`, `ActiveMilestone` and `ActiveCycle` all `NONE`. Actual registers
  and artifacts also show no active implementation workcell, execution lane,
  milestone, cycle or handoff. NONE alone never establishes eligibility.
- No prior promotion exists in the full source-version log, intake/decision
  evidence or retained archived/superseded history. Verify history completeness;
  missing or contradictory history is uncertainty, not evidence of absence.
  A pending scaffold document is not a promotion.
- The current human request identifies one exact source document and unused
  version label, with traceable applicable Gate 1 human approval. Bind that
  request and approval to the document identity, SHA256, version and scope.
  Scaffold initiation is not promotion approval; AI-written approval claims
  cannot substitute for the human evidence.
- The entire source is readable, nonempty and complete for this promotion. Its
  exact bytes and intended preservation location are bound to SHA256.
- The executor is the identified Director Lane / Source Truth Agent under the
  existing Director identity and permissions. CurrentAuthority must lawfully
  name Director Lane. No uncertain authority or unresolved eligibility conflict
  may be inferred away. Every failed check is STOP_REQUIRED.

### Procedure and exact mutation boundary

1. Record the initial basis in the promotion evidence report, referenced from
   INTAKE_REGISTER.md and an append-only DECISION_LOG.md attempt reservation.
   Make the durable reservation before other promotion writes. The basis
   contains the human request/approval references, document identity and original
   location/hash, unused version, frozen contract references/hashes, full initial
   control-plane snapshot, history search/results, Director identity/permissions,
   size and guardrail checks, exact allowed writes and before hashes, and stage
   attempts. A recorded incomplete attempt precludes a fresh attempt.
2. Preserve the source bytes at a new immutable path inside `01_SOURCE_TRUTH/`.
   Record that location and hash. Never edit the source. Compare both original
   and preserved bytes with the bound hash again immediately before registration.
3. Follow the existing Source Truth Agent extraction, duplicate comparison and
   verbatim-quote checks. Reuse matching scaffold candidate IDs; acceptance
   criteria remain DRAFT. No accepted work, milestone acceptance or QA signoff.
4. Register the approved version in SOURCE_TRUTH_VERSION_LOG.md, using its existing
   columns. Key Changes references the promotion evidence with exact document
   paths/hash, timestamp, approval and extraction summary. Registration consumes
   the initial basis immediately; only the declared completion evidence/state
   for this same promotion may still be finished under it.
5. Produce the evidence report and Context Delta, with all engaged stages and
   non-engaged agents/reasons, before/after SHA256 and exact permitted differences
   for every changed file. Governance evidence traces to the attempt and contracts;
   never fabricate a workcell, BI-ID or CP-ID to fill a template.
6. Emit a canonical handoff in ACTIVE/ addressed to Context Steward, referencing
   the registered version, evidence and CD-ID. Explicit Director routing permits
   only first ordinary context assembly for promotion review. Stop at Step 13.

Allowed file writes: the immutable source copy; intake, append-only decision/
attempt evidence; SOURCE_TRUTH_VERSION_LOG.md, REQUIREMENTS_INDEX.md,
BUSINESS_ITEMS.md, ACCEPTANCE_CRITERIA.md (DRAFT only), REQUIREMENT_SECTION_MAP.md
and OPEN_QUESTIONS.md as required for extraction; the declared promotion evidence,
Context Delta, handoff and named control-plane fields. Existing schemas apply.
No unrelated rows or files may change. Product code, implementation workcells,
framework edits, new scope approval, standing delegation and adjacent Director
operations are forbidden under this basis.

The Director may write `CurrentPhase = SOURCE_TRUTH_LOADING` and
`ExecutionReadiness = NOT_READY` during preparation. Completion writes only
`SourceTruthVersion = <registered version>`, `CurrentPhase = SOURCE_TRUTH_READY`,
`ExecutionReadiness = NEEDS_CONTEXT`, `LastAction`, `LastContextDelta` (actual CD-ID),
`NextExpectedAction`, and `CurrentAuthority = Context Steward` for this routing.
ActiveWorkcell, ActiveHandoff, ActiveMilestone and ActiveCycle remain NONE;
Identity fields and RoutingMode are unchanged. Existing State permissions still
record discovered stops and reconcile against registers. No READY transition is
permitted without the ordinary CP-C03 prerequisites.

### First ordinary context and termination

Context Steward uses its existing self-assembly rule with the registered version,
control plane and Director-issued handoff addressed to it in ACTIVE/. For this
lane-only assembly the routed request supplies scope; no workcell or scope
contract is invented and ActiveHandoff remains NONE. Verify the completed
promotion, source hash, approval and evidence, process the CD-ID, and create/index
the first ordinary CP-ID with scope, provenance, exclusions and staleness checks.
Name the active delivery handoff for Director review as the pack's task handoff;
retain the consumed assembly request as provenance. Discharge that request before
emitting the delivery handoff. Neither lane handoff becomes ActiveHandoff.
Context Steward writes no Authority field and never writes a CP-ID or PENDING_DELTA
into LastContextDelta. Its evidence/delta/delivery follow ordinary dispatch and
stop at the boundary. Pack creation alone authorizes no further Director action,
implementation or READY state; all ordinary context requirements resume.

Any promotion history permanently excludes bootstrap, even after resetting
SourceTruthVersion to NONE. Failed first-pack creation never reopens it.
Changed approval, document, hash, version or scope invalidates an attempt. Partial
writes fail closed: preserve reservation/history/evidence; no false completion,
history deletion or fresh retry. Only evidence-backed reconciliation of the SAME
recorded incomplete attempt is possible where existing recovery authority permits,
with unchanged bindings and the existing one-correction limit. SOURCE_TRUTH_LOADING
is never fresh eligibility. After registration, reconciliation may finish only
missing completion evidence/state, never promote again. Missing evidence or
authority requires a stop and human route; no new recovery permission is created.

### Post-Registration Completion Reconciliation

This bounded procedure applies only to the SAME recorded incomplete first-promotion
attempt whose approved version is already registered ACTIVE. It finishes missing
completion evidence and permitted completion state; it is not a new Promote command,
fresh intake, automatic resume or restoration of the consumed initial basis. It
defines no independent recovery authority. Existing governance, approval gates,
recovery contracts and release/adoption requirements remain mandatory. An external
recovery authorization or recovery-only pack alone cannot enable these writes or
ordinary handback; Purpose B's assembly-only write scope is unchanged.

1. **Identify and verify, read-only.** Resolve exactly one original attempt from
   its durable decision reservation, intake and promotion evidence. Verify its
   request, attempt identity, original Gate 1 approval/reference, source document
   identity and location, original and preserved SHA256, registered version and
   scope against the original bindings. Verify governing contract references and
   any separately authorized adoption without rebinding old approvals. Require
   the matching ACTIVE registration and current SourceTruthVersion, valid existing
   extraction/quote/duplicate evidence, readable consistent control plane, full
   stage/correction history and no unexplained mutations. Inventory related deltas
   and handoffs, including consumed/archived history. Missing required admission
   evidence, changed bindings, conflicting history or exhausted/uncertain correction
   allowance requires STOP and human routing. Only specifically identified missing
   completion outputs may be supplied below; admission evidence cannot be invented.
2. **Preserve history and verify existing outputs.** Retain all permission denials,
   BLOCKED records, timestamps, attempts, approvals, journals and partial outputs.
   Historical findings remain historical; a later artifact is not proof that the
   denied operation was authorized. Verify actual creation authority/provenance for
   the existing Director handoff, its unique ID, ACTIVE location/status, sender,
   Context Steward recipient, source version, scope and evidence/CD references.
   Uncertain handoff creation authority, a conflicting or consumed handoff, missing
   handoff or unexplained later write requires STOP. Later approval cannot
   retroactively authorize a denied write. An interrupted recovery-ledger claim
   also requires STOP; never skip a slot, delete ownership or change ledgers.
3. **Obtain exact prospective authority.** The executor must be the identified
   Director Lane / Source Truth Agent lawfully authorized for this completion task;
   a lane name, CurrentAuthority value or filesystem access is insufficient.
   Prepare the exact remaining write plan with target/root, attempt, executor,
   paths/fields/operations, before hashes (ABSENT for a declared missing output),
   constrained after images, evidence destination and validation criteria. Obtain
   explicit human approval for that exact plan under applicable governance,
   retaining the original promotion approval and every applicable gate. Rule 14
   recovery requires both applicable human capacities and named delegation; its
   approval is separate from adoption and original Gate 1 approval. Verify current
   execution authority for the exact executor, operations, paths and scope through
   the legitimate platform approval flow, including Assisted Permissions where
   applicable, and preserve its authoritative result/reference. A local approval
   flag, AI assertion, verifier consistency PASS or successful earlier write is
   insufficient. Missing, denied, ambiguous, expired, withdrawn or out-of-scope
   authority requires STOP before mutation and human routing. Do not probe by
   writing, bypass a denial or switch execution paths to evade platform approval.
4. **Reserve the one correction and apply only the bounded plan.** Record the
   authorized correction against the original attempt before other correction
   writes. It consumes the existing one-correction allowance; it does not create
   a new intake attempt or reset any stage/retry counter. The complete possible
   canonical write scope, each item requiring exact authorization, is:
   - Append-only reconciliation evidence in the declared promotion evidence,
     append-only DECISION_LOG.md entries and an INTAKE_REGISTER.md Notes annotation
     linked to the original intake/attempt. Preserve existing record content,
     statuses and timestamps; do not replace the historical BLOCKED disposition.
   - Create specifically declared missing completion evidence or Context Delta
     at its bound, unused path; append missing completion evidence to an existing
     declared evidence report. Reuse valid existing evidence and the actual CD-ID;
     never overwrite/reissue a delta or allocate a replacement for a valid one.
   - Complete only the originally permitted control-plane fields where needed:
     SourceTruthVersion = the already registered version,
     CurrentPhase = SOURCE_TRUTH_READY, ExecutionReadiness = NEEDS_CONTEXT,
     LastAction, LastContextDelta = actual CD-ID, NextExpectedAction and
     CurrentAuthority = Context Steward for the verified existing routing.
   Reuse the existing registration, immutable source, extraction IDs/artifacts and
   handoff unchanged. No new source version, source copy, extraction, promotion,
   intake attempt or handoff is permitted. No other file, row or field may change.
   ActiveWorkcell, ActiveHandoff, ActiveMilestone and ActiveCycle remain NONE;
   identity and RoutingMode remain unchanged. No blocker closure, counter reset,
   READY transition, framework edit or application mutation is authorized.
   Recheck current hashes, bindings, permission and withdrawal immediately before
   each write; serialize the action and STOP on changed bytes or another writer.
   Preserve exact diffs and before/after hashes in append-only audit evidence,
   with final output hashes external to avoid circular evidence hashes.
5. **Validate, record disposition and STOP.** Independently validate the completed
   promotion evidence, registration/source/extraction integrity, delta, existing
   handoff references, control-plane consistency and unchanged excluded artifacts.
   Record the validation evidence and a later completion disposition linked to
   the original attempt, denial, exact recovery authorization, correction count
   and final hashes; distinguish it from the historical BLOCKED finding. Claim
   completion only after validation passes, then STOP at Director dispatch step 13.
   A partial write, new denial, failed validation or interruption preserves all
   actual outputs/history and requires STOP and human routing, never automatic
   retry, rollback, fabricated completion or a second correction under this rule.

Before subsequent ordinary consumption, Context Steward must verify the original
attempt/bindings and Gate 1 evidence, current registered source/hash, extraction,
the exact reconciliation authorization and platform permission evidence, correction
reservation/count, independent final validation and linked completion disposition.
It must verify that the original handoff remains unique, ACTIVE, unconsumed,
lawfully created and addressed to it with matching scope/evidence/CD, and that
current control-plane routing and its own current execution authority are valid.
Missing or conflicting evidence/authority requires STOP and human routing; Steward
cannot repair the promotion or infer authority from historical BLOCKED or ACTIVE
labels. Any actual registered blocker still requires its existing resolution and
sign-off; reconciliation does not clear it or substitute for operational handback.
Only after all applicable prerequisites pass may Steward follow the existing first
ordinary context procedure, consume the original request, retain its provenance,
index the first ordinary pack and emit its normal delivery handoff, then STOP.
No subsequent Director action, implementation or READY state is implied.

## Version Identifier Format

Source truth versions use: SOURCE_TRUTH_V{{MAJOR}}.{{MINOR}}

Examples: SOURCE_TRUTH_V0.1, SOURCE_TRUTH_V1.0, SOURCE_TRUTH_V1.1

## Authority Hierarchy

1. Promoted source truth documents (highest authority)
2. Accepted contracts and decisions recorded in DECISION_LOG.md
3. Workcell scope contracts (scoped to their lane)
4. Context packs (must reference one of the above)
5. Memory Bank (reference only — lowest authority)

## What Is NOT Source Truth

- Unpromoted documents (reference material only)
- Memory Bank content
- Application source code and runtime behavior — these are OBSERVED_EVIDENCE of what the system currently does, never source truth for what it should do (see Truth Classes)
- AI inference or training knowledge
- Prior-cycle ADAPT state not carried forward via CARRY_OVER_REGISTER.md

## Truth Classes

Every statement ADAPT records about a solution belongs to one class. The class decides
what the statement may govern.

| Class | What it is | What it may govern |
|---|---|---|
| PROMOTED_TRUTH | A statement in a promoted, versioned source truth document, or derived from one with its source quoted verbatim | Requirements, acceptance criteria, decisions, all workcell work |
| CANDIDATE_TRUTH | A statement ADAPT derived — from discovery, intake, or interpretation — that has not been promoted | Nothing. It may be proposed for promotion, questioned, or rejected |
| OBSERVED_EVIDENCE | Measured or read behavior of an existing system: code, runtime output, logs, configuration | What the system currently does. Never what it should do |

There is no separate class for a client document's external authority. A ticket or
specification gains authority in ADAPT only by promotion; who issued it is recorded as
its origin in SOURCE_TRUTH_VERSION_LOG.md, not as a class.

**The forbidden sequence.** Observed behavior must not become a requirement by being
described. The sequence observed implementation → AI interpretation → recorded
requirement → later work treating it as fact converts what a system does into what it
must do, with no decision in between. An observation enters source truth only as a
promoted statement that quotes it, names it as OBSERVED_EVIDENCE, and records who
decided it should become a requirement.

The existing implementation is authoritative evidence of current behavior. It is not
evidence of intended behavior. Where the two may differ, that difference is an open
question, not an inference to resolve.

## Conflict Resolution

If two promoted source truth versions conflict:
1. The conflict must be recorded as an OPEN_QUESTIONS.md entry
2. The Director must resolve the conflict and record the decision in DECISION_LOG.md
3. A new source truth version may be promoted to incorporate the resolution

## Consumption Rules

- Every workcell task must reference a source truth version
- Context packs must declare which source truth version they were built against
- Evidence must be traceable to source truth
- If the relevant source truth version has been superseded, the work must be re-validated against the current version
