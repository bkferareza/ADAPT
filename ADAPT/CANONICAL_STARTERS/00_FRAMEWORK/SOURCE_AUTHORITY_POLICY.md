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
