# HUMAN_APPROVAL_GATES.md
STATUS: DRAFT

## Purpose
Lists every action in the ADAPT framework that requires explicit human approval before any AI agent may proceed. An AI agent that proceeds past an approval gate without a recorded human approval commits a GOVERNANCE_VIOLATION. This list is authoritative and exhaustive — any action not listed here that an agent believes requires human approval should be flagged to the Director and the gate added here.

---

## Approval Gate Definitions

---

### Gate 1 — Promote Source Truth

**Description**
Before the Director Lane may record any project document as the accepted source truth version, a human must explicitly approve the promotion. This gate prevents AI agents from unilaterally establishing the authority basis for all subsequent project work.

**Who Requests It**
Director Lane (Source Truth Agent), after reading the document and confirming it is promotable.

**How Approval Is Recorded**
Human provides explicit written approval (message, annotation, or sign-off record). The Director Lane records the approval reference in SOURCE_TRUTH_VERSION_LOG.md alongside the version entry. The approval reference must be traceable (e.g., conversation timestamp, meeting note ID, sign-off message).

**What Happens If AI Proceeds Without Approval**
GOVERNANCE_VIOLATION — SOURCE_TRUTH_VIOLATION. The source truth record is invalid. All work derived from an unapproved source truth promotion must be flagged as ungoverned until the promotion is retroactively approved or the work is re-governed under an approved version.

---

### Gate 2 — Create Full ADAPT Scaffold

**Description**
Before a new ADAPT instance is created, a human must initiate the creation either by issuing the command `Initialize ADAPT from requirements` or by instructing the agent to `Read and Execute START_HERE.md`. An AI agent may not self-initiate ADAPT scaffold creation.

**Who Requests It**
Human initiator (no AI requests this gate — the human is the initiator).

**How Approval Is Recorded**
The human's initiation command or instruction is the approval. The Director Lane records the initialization event in PROJECT_CONTROL_PLANE.md with: initiator reference, command issued, timestamp, project document path. The ONBOARDING_REPORTS.md records the initialization as the first entry.

**What Happens If AI Proceeds Without Approval**
GOVERNANCE_VIOLATION — AUTHORITY_VIOLATION. An ADAPT instance created without human initiation is not a governed instance. All artifacts produced under it are ungoverned.

---

### Gate 3 — Onboard a Workcell

**Description**
Before the Onboarding Orchestrator may create a new workcell folder and generate its 15 files, the Director Lane must have received explicit human approval for the onboarding of that specific identity in that specific role.

**Who Requests It**
Director Lane (based on a planning gap, assignment need, or human request), after confirming source truth is promoted and the role is valid.

**How Approval Is Recorded**
Human provides explicit approval (message, annotation, or sign-off). The Director Lane records the approval in ONBOARDING_REPORTS.md (onboarding request entry with approval reference) and in DECISION_LOG.md. The Onboarding Orchestrator reads the approval reference from INTAKE_REGISTER.md or DECISION_LOG.md before creating any files.

**What Happens If AI Proceeds Without Approval**
GOVERNANCE_VIOLATION — AUTHORITY_VIOLATION. The workcell is not a governed workcell. Any work it performs is ungoverned until the onboarding is retroactively approved or the workcell is re-onboarded under approved authority.

---

### Gate 4 — Approve Milestone Plan

**Description**
Before the Planning Orchestrator's milestone plan recommendation becomes the authoritative plan for execution, the Director Lane must present it to the human for approval. No work execution against the milestone may begin until the plan is approved.

**Who Requests It**
Director Lane, after the Planning Lane emits the planning submission handoff.

**How Approval Is Recorded**
Human provides explicit plan approval. The Director Lane records the approved plan in DECISION_LOG.md with: milestone ID, plan version, approval reference, date, and any conditions or modifications accepted by the human. The control plane is updated: `ExecutionReadiness = READY`, `CurrentPhase = READY_FOR_ASSIGNMENT`. For every AC-ID named in the approved plan whose status in ACCEPTANCE_CRITERIA.md is DRAFT, the Director Lane writes READY_FOR_TEST and records the plan's DEC-ID against it. No other action writes READY_FOR_TEST.

**What Happens If AI Proceeds Without Approval**
GOVERNANCE_VIOLATION — AUTHORITY_VIOLATION. Execution against an unapproved milestone plan is ungoverned. Work produced under an unapproved plan is not eligible for Director certification until the plan is retroactively approved or the work is re-governed.

---

### Gate 5 — Approve Code Mutation Scope Change

**Description**
When the active workcell identifies that its assigned task requires modifying files outside the mutation authority listed in its current SCOPE_CONTRACT.md, the Director Lane must request human approval before updating the scope contract.

**Who Requests It**
Director Lane, after receiving a scope expansion request from the workcell (via a blocker record).

**How Approval Is Recorded**
Human provides explicit scope change approval. The Director Lane records the approval in DECISION_LOG.md and updates the workcell's SCOPE_CONTRACT.md with: the new files added to mutation authority, the approval reference, and the date of change.

**What Happens If AI Proceeds Without Approval**
GOVERNANCE_VIOLATION — MUTATION_VIOLATION. Any file modified outside the approved mutation authority is an unauthorized mutation. The evidence produced for that work is invalid and must be re-produced under approved scope.

---

### Gate 6 — Accept Risk

**Description**
When the Director Lane identifies a known risk (from planning, integration, challenge review, or gap analysis) and proposes to proceed despite the risk rather than resolve it, a human must explicitly accept the risk before execution continues.

**Who Requests It**
Director Lane, when presenting a risk acceptance recommendation based on planning output, integration findings, or challenge report findings.

**How Approval Is Recorded**
Human provides explicit risk acceptance. The Director Lane records the accepted risk in DECISION_LOG.md with: risk description, RSK-ID (if from planning or challenge), mitigation (if any), human acceptance reference, date. If the risk comes from a CONDITIONAL_PASS challenge report, the Director also updates the challenge report record.

**Unvalidated acceptance criteria.** A risk acceptance under this gate may cover acceptance criteria that a QA validation report recommended VALIDATION_UNAVAILABLE. It must name each AC-ID individually, cite the QVR-ID that recorded it as unavailable, state why validation could not be obtained, and record the human's explicit acceptance that the criterion proceeds unverified. It cannot be requested or granted by a QA workcell or by any workcell that implemented the criterion. Where one person holds those roles under a CONSTRAINED exception, the acceptance is recorded in the Director capacity and states that the same person implemented the work. The acceptance never makes a criterion PASSED. A criterion recommended FAIL cannot be accepted as unverified: it is not unverified, it is unmet.

**What Happens If AI Proceeds Without Approval**
GOVERNANCE_VIOLATION — AUTHORITY_VIOLATION. Proceeding with a known material risk without human acceptance is unauthorized. If the risk materializes, the Director cannot certify the affected work without retroactive human risk acceptance.

---

### Gate 7 — Close a CRITICAL Blocker

**Description**
When a CRITICAL blocker is resolved, the resolution must be human-approved before the Director Lane may close the blocker in BLOCKER_REGISTER.md and remove it from the control plane's ActiveBlockers.

**Who Requests It**
Director Lane (Blocker Routing Agent), after receiving a resolution proposal from the responsible workcell or an external resolution.

**How Approval Is Recorded**
Human provides explicit resolution approval. The Director Lane records the resolution in BLOCKER_REGISTER.md: BLK-ID, resolution description, evidence reference, human approval reference, closure timestamp. The control plane is updated: remove BLK-ID from ActiveBlockers; set Blocked=NO only if no blocker remains OPEN.

**What Happens If AI Proceeds Without Approval**
GOVERNANCE_VIOLATION — BLOCKER_VIOLATION. A CRITICAL blocker closed without human approval remains formally open. Any work that resumed after the unauthorized closure is ungoverned.

---

### Gate 8 — Certify Release

**Description**
Before the Director Lane issues final release certification (the certification that authorizes delivery, deployment, or release of the milestone output), a human must explicitly approve the release.

**Who Requests It**
Director Lane (Certification Agent), after confirming: every AC-ID in scope is PASSED, or UNVERIFIED under a recorded Gate 6 acceptance naming it; QA signoff is on record; no open CRITICAL/HIGH defects; all required handoffs are present.

**How Approval Is Recorded**
Human provides explicit release approval. The Director Lane records the certification in SIGNOFF_REGISTER.md and ACCEPTED_WORK_REGISTER.md with: scope, milestone ID, QA report reference, evidence report references, human approval reference, certification date. The release certification lists every UNVERIFIED AC-ID by ID with its Gate 6 DEC-ID, separately from PASSED criteria. UNVERIFIED criteria are never counted, reported, or summarised as passed.

**What Happens If AI Proceeds Without Approval**
GOVERNANCE_VIOLATION — AUTHORITY_VIOLATION. A release authorized without human approval is an unauthorized release. The certification record is invalid.

---

### Gate 9 — Archive Major Source Truth Version

**Description**
When the Director Lane proposes to archive (retire) a source truth version — moving it from the active reference pool to the archive — a human must explicitly approve the archival before any artifact referencing the old version is updated.

**Who Requests It**
Director Lane, when a new source truth version is promoted and the prior version is to be retired, or during a janitor pass that identifies an old version for archival.

**How Approval Is Recorded**
Human provides explicit archival approval. The Director Lane records the archival in SOURCE_TRUTH_VERSION_LOG.md: version label, archival date, human approval reference, note that the version is no longer the active source truth.

**What Happens If AI Proceeds Without Approval**
GOVERNANCE_VIOLATION — SOURCE_TRUTH_VIOLATION. An archived source truth version without human approval may still be referenced by active work. Archiving it without approval could invalidate live work items unexpectedly.

---

### Gate 10 — Override Guardrail

**Description**
When a guardrail returns STOP_REQUIRED and the Director Lane determines that the stop is a false positive or that proceeding is justified despite the guardrail signal, a human must explicitly approve the override before any agent proceeds.

**Who Requests It**
Director Lane, after reviewing the guardrail stop signal and preparing a justification for the override.

**How Approval Is Recorded**
Human provides explicit guardrail override approval. The Director Lane records the exception in DECISION_LOG.md with: guardrail ID, stop condition triggered, justification for override, human approval reference, date, and scope of the exception (the exception applies only to the specific identified action, not generally).

**What Happens If AI Proceeds Without Approval**
GOVERNANCE_VIOLATION — GUARDRAIL_VIOLATION. Proceeding past a guardrail stop without human approval nullifies the guardrail's protective function. All work produced in violation of the guardrail's stop condition is ungoverned.

---

### Gate 11 — Run XL Context Job

**Description**
When the Context Steward's Job Sizing Agent classifies an upcoming action as XL (full lane audit, release review, or major replan), the Context Steward must flag the size to the Director Lane, which must obtain human approval before the XL context pack is assembled and the action proceeds.

**Who Requests It**
Context Steward (Job Sizing Agent) flags the XL classification; the Director Lane prepares the approval request for the human.

**How Approval Is Recorded**
Human provides explicit approval for the XL action. The Director Lane records the approval in DECISION_LOG.md with: the action being approved, the XL classification basis, the human approval reference, and the date. The Context Steward may then proceed to assemble the XL context pack.

**What Happens If AI Proceeds Without Approval**
GOVERNANCE_VIOLATION — CONTEXT_VIOLATION. An XL action run without approval may consume excessive context, produce low-quality work due to overload, or execute across scope boundaries that should have been reviewed. The output of an unapproved XL action must be reviewed before acceptance.

**Additional Guidance — XL Without Approval**
If the XL approval is not granted, the Context Steward and Director Lane must split the action into multiple L-size actions, each with its own handoff and approval-free execution. The split must be documented in DECISION_LOG.md with the original XL action ID and the substitute L-size action sequence.
