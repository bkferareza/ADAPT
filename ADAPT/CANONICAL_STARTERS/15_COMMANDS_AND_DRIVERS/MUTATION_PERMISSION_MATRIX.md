# MUTATION_PERMISSION_MATRIX.md
STATUS: DRAFT

## Purpose
Defines exactly what each ADAPT role may and may not write, modify, or create. Every agent must check this matrix before taking any action that modifies an artifact. "NO" is an absolute prohibition. "LIMITED" requires reading the notes section for the specific constraint.

---

## Permission Matrix

| Role | Can mutate ADAPT control artifacts? (control plane, registers, logs) | Can mutate source truth? | Can mutate application source code? | Can mutate tests? | Can mutate pipeline/config? | Can create gaps? | Can create blockers? | Can certify accepted work? | Can produce QA signoff? |
|------|----------------------------------------------------------------------|--------------------------|-------------------------------------|-------------------|-----------------------------|-----------------|---------------------|---------------------------|------------------------|
| Director Lane | YES | LIMITED | NO | NO | NO | YES | YES | YES | NO |
| Integrator Workcell | LIMITED | NO | LIMITED | NO | LIMITED | YES | YES | NO | NO |
| Backend Workcell | LIMITED | NO | YES | LIMITED | LIMITED | YES | YES | NO | NO |
| Frontend Workcell | LIMITED | NO | YES | LIMITED | LIMITED | YES | YES | NO | NO |
| QA Workcell | LIMITED | NO | NO | YES | NO | YES | YES | NO | YES |
| Planning Orchestrator | LIMITED | NO | NO | NO | NO | YES | NO | NO | NO |
| Onboarding Orchestrator | LIMITED | NO | NO | NO | NO | YES | YES | NO | NO |
| Context Steward | LIMITED | NO | NO | NO | NO | YES | NO | NO | NO |
| Janitor | LIMITED | NO | NO | NO | NO | NO | NO | NO | NO |
| Challenge Lane | LIMITED | NO | NO | NO | NO | YES | NO | NO | NO |

---

## First-promotion boundary

Under SOURCE_AUTHORITY_POLICY.md, First-Promotion Initial Context Basis, the
Director's file and control-field permissions are restricted to that procedure's
declared allowlist. An exact immutable source copy is permitted, never source
editing. Context Steward retains its existing context/delta/handoff permissions
and schema class precedence. No product, framework, scope approval, certification,
QA signoff, delegation or adjacent Director authority follows from this basis.

## Memory Bank Write Authority

14_MEMORY_BANK/ (NOTES.md, REFERENCES_INDEX.md, and named reference documents within
it): any lane may write without Director approval. This content is explicitly
non-binding per its own contract text — "reference only," "does not govern" — and
carries none of the authority risk that gates writes to source truth or the control
plane. The risk here was never wrong authorship; it was that nothing prompted
authorship at all.

---

## Notes for LIMITED Entries

### Control-plane permission precedence

CONTROL_PLANE_SCHEMA.md Field Classes governs control-plane writes. Its explicit
Identity, Authority, State and Trace permissions apply before the restrictive
role summaries below. State may be written by a lane discovering the condition;
Trace only by the performer of the recorded activity. Neither grants assignment
or identity authority. Direct human registry commands permit only their named
CurrentAuthority recording and activity phase delegation; approval gates remain.
Role-specific prohibitions below prohibit additional control-plane writes, not
class permissions or explicit delegations. No toolkit command writes state.

### Onboarding Orchestrator — LIMITED

ACTION_PROMPT_ONBOARDING.md, Onboarding lane identity and scope basis, restricts
this permission to the approved target's declared files/rows and evidence paths.
It supplies pre-workcell executor scope, never implementation authority. Director
and Context Steward retain only their named preparation/context operations.

May create the approved identity's workcell artifacts and registry/onboarding
records after Director approval under Gate 3. A direct human Onboard command
permits CurrentAuthority recording under the schema's direct-command delegation;
otherwise authority is assigned by the Director. No self-assignment, milestone
assignment, source promotion, or other Authority/Identity edits are permitted.

### All Workcells — control plane discharge exception

A workcell may make exactly one control-plane update when its current bounded action
completes: discharge its own active handoff to CONSUMED/, clear `ActiveHandoff`, and set
`CurrentPhase = READY_FOR_ASSIGNMENT`. It may not update any other control-plane field
under this exception. Independent State and Trace permissions remain governed by
CONTROL_PLANE_SCHEMA.md; discharge does not restrict them or grant new authority.

### Director Lane — Can mutate source truth? — LIMITED
The Director Lane may promote a source truth version and record it in SOURCE_TRUTH_VERSION_LOG.md. This requires human approval before the promotion record is written. The Director Lane may NOT modify the content of the source truth document itself. Content modifications require a new version, human approval, and re-extraction. Writing an acceptance criterion's lifecycle status — the Status column of ACCEPTANCE_CRITERIA.md, by the agent and under the conditions that file names for each value — is governance state, not source-truth content, and is permitted. Changing a criterion's text is content modification and remains prohibited.

### Integrator Workcell — Can mutate ADAPT control artifacts? — LIMITED
The Integrator may update: API_CONTRACTS.md (reconciliation records), HANDOFFS.md (its own log), EVIDENCE_LOG.md (its own), CONTEXT_DELTAS.md (its own). The Integrator may NOT update: PROJECT_CONTROL_PLANE.md (except for the All Workcells discharge exception above), ACCEPTED_WORK_REGISTER.md (Director only), DECISION_LOG.md (Director only).

### Integrator Workcell — Can mutate application source code? — LIMITED
The Integrator may make narrowly scoped reconciliation changes that both the backend and frontend workcells have agreed to in writing (recorded in the reconciliation report). The Integrator must not rewrite feature logic, change business rules, or modify code outside the agreed reconciliation scope. Any reconciliation change that affects more than the agreed scope must be routed to the responsible workcell via Director.

### Integrator Workcell — Can mutate pipeline/config? — LIMITED
The Integrator may update CI/CD pipeline configuration when build failures are identified during integration review AND the specific configuration change is within the integration scope defined in its SCOPE_CONTRACT.md. Pipeline changes that affect production deployment configuration require Director and human approval.

### Backend Workcell — Can mutate ADAPT control artifacts? — LIMITED
The Backend Workcell may update: HANDOFFS.md (its own), EVIDENCE_LOG.md (its own), CONTEXT_DELTAS.md (its own), `02_DIRECTOR_LANE/GAP_REGISTER.md`, BLOCKERS.md (its own), TASK_REGISTER.md (its own). The Backend Workcell may NOT update: PROJECT_CONTROL_PLANE.md (except for the All Workcells discharge exception above), ACCEPTED_WORK_REGISTER.md, DECISION_LOG.md, WORKCELL_REGISTRY.md, LANE_ASSIGNMENT_MATRIX.md.

### Backend Workcell — Can mutate tests? — LIMITED
The Backend Workcell may write unit tests and integration tests for the server-side logic it is implementing, within its SCOPE_CONTRACT.md mutation authority. It may NOT write or modify QA acceptance tests or QA test plans — those belong to the QA Workcell.

### Backend Workcell — Can mutate pipeline/config? — LIMITED
The Backend Workcell may modify pipeline configuration files explicitly listed in its SCOPE_CONTRACT.md mutation authority (e.g., environment variable definitions for backend services, migration runner configuration). It may NOT modify the overall CI/CD deployment pipeline, shared build steps, or frontend pipeline configuration.

### Frontend Workcell — Can mutate ADAPT control artifacts? — LIMITED
Same as Backend Workcell. The Frontend Workcell may update only its own workcell-scoped ADAPT logs (HANDOFFS.md, EVIDENCE_LOG.md, CONTEXT_DELTAS.md, `02_DIRECTOR_LANE/GAP_REGISTER.md`, BLOCKERS.md, TASK_REGISTER.md), except for the All Workcells discharge exception above.

### Frontend Workcell — Can mutate tests? — LIMITED
The Frontend Workcell may write component tests and frontend integration tests for the UI logic it is implementing, within its SCOPE_CONTRACT.md mutation authority. It may NOT write or modify QA acceptance tests or QA test plans.

### Frontend Workcell — Can mutate pipeline/config? — LIMITED
The Frontend Workcell may modify pipeline configuration files explicitly listed in its SCOPE_CONTRACT.md mutation authority (e.g., frontend build scripts, asset pipeline configuration). Same restrictions as Backend Workcell for shared and deployment pipeline steps.

### QA Workcell — Can mutate ADAPT control artifacts? — LIMITED
The QA Workcell may update: HANDOFFS.md (its own), EVIDENCE_LOG.md (its own), DEFECT_REGISTER.md (creating defect records). It may NOT update: PROJECT_CONTROL_PLANE.md (except for the All Workcells discharge exception above), ACCEPTED_WORK_REGISTER.md, DECISION_LOG.md, WORKCELL_REGISTRY.md. QA signoff is recorded in SIGNOFF_REGISTER.md — the QA Workcell creates this record (its own signoff record), but certification in ACCEPTED_WORK_REGISTER.md is created by the Director Lane.

### Planning Orchestrator — Can mutate ADAPT control artifacts? — LIMITED
The Planning Orchestrator may update: WORKCELL_ROADMAPS.md, DEPENDENCY_MAP.md, and its own planning artifacts (milestone briefs, work package lists). It may NOT update: PROJECT_CONTROL_PLANE.md directly (all control plane updates go through the Director), ACCEPTED_WORK_REGISTER.md, DECISION_LOG.md (Director records plan approvals), LANE_ASSIGNMENT_MATRIX.md (Director assigns after plan approval).

### Context Steward — Can mutate ADAPT control artifacts? — LIMITED
The Context Steward may update: `LastContextDelta` field in PROJECT_CONTROL_PLANE.md (this specific field only), context pack artifacts (CP-IDs in the context pack folder), staleness records. It may NOT update: any governance register, accepted work records, decision log, or source truth.

### Janitor — Can mutate ADAPT control artifacts? — LIMITED
The Janitor may: move consumed handoffs from CONSUMED/ to ARCHIVE/ when their milestone closes (adding archive header only), compact resolved register entries (summarize in-place without deleting original IDs and resolution status). The Janitor never moves handoffs out of ACTIVE/: the receiving lane discharges its own completed handoff to CONSUMED/. The Janitor may NOT: delete any record, modify accepted work records, modify decision log content, or alter any active artifact. All Janitor mutations are archive or compaction only.

---

## Absolute Prohibitions (All Roles)

Regardless of role, the following are prohibited for all AI agents:

| Prohibition | Applies To |
|-------------|-----------|
| Writing to application source code without active workcell authority and SCOPE_CONTRACT.md mutation permission | All roles except Backend/Frontend/Integrator Workcells within scope |
| Modifying ACCEPTED_WORK_REGISTER.md content (append-only) | All roles — Director may append; no role may modify existing entries |
| Modifying DECISION_LOG.md content (append-only) | All roles — Director may append; no role may modify existing entries |
| Promoting source truth without human approval | All roles |
| Producing QA signoff without QA independence | All roles except QA Workcell under independence requirement |
| Certifying accepted work without evidence review | All roles — this is Director Certification Agent authority only |
| Modifying a framework-derived contract file in an instance (00_FRAMEWORK/, 07_GUARDRAILS/, 08_TEMPLATES/, 15_COMMANDS_AND_DRIVERS/) other than through an authorized framework upgrade or backport | All roles — the Framework Maintainer authorizes; see GOVERNANCE_RULES.md, Rule 14 |
