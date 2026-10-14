# EVIDENCE_STANDARD_BY_ROLE.md
STATUS: DRAFT

## Purpose
Defines exactly what evidence each ADAPT role must produce for any completed action to be considered valid. Evidence standards are role-specific because what constitutes proof of work differs by authority and responsibility. Agents must not accept lower-quality evidence as a substitute for what is listed here as required.

---

## Evidence Standards

---

### Director Lane

**Required Evidence Artifacts**
1. **Decision log entries** (DECISION_LOG.md): one entry per Director decision, containing: decision ID, decision description, basis for the decision, any approval reference, date, and what action follows from the decision.
2. **Assignment records** (LANE_ASSIGNMENT_MATRIX.md): one entry per business item or task assigned, containing: BI-ID, assigned workcell ID, role, assignment date, scope contract reference.
3. **Control plane updates** (PROJECT_CONTROL_PLANE.md): after every Director action, the relevant fields must be updated. The update is itself evidence — the control plane must reflect the current state accurately.
4. **Gap routing records** (GAP_REGISTER.md): for every gap routed, one entry with: GAP-ID, type, routing authority, routing decision, timestamp.
5. **Blocker routing records** (BLOCKER_REGISTER.md): for every blocker routed, one entry with: BLK-ID, severity, affected work, routing decision, timestamp.
6. **Certification records** (ACCEPTED_WORK_REGISTER.md and DECISION_LOG.md): for every certification issued, one entry in each register with: scope, AC-IDs certified, QA report reference, evidence report references, date, Director identity.

**Optional Evidence Artifacts**
- Director handoff artifacts to specific orchestrators (when routing a command or task)
- Intake register entries (when processing via Director Intake Agent)
- Source truth version log entries (when promoting source truth)

**What Is NOT Accepted as Evidence for the Director Lane**
- Developer evidence (implementation reports, changed file lists) — that belongs to the workcell
- QA signoff records — that belongs to the QA Orchestrator
- Planning output that has not been approved by the Director — unapproved planning output is a recommendation, not evidence of a decision
- Verbal descriptions of decisions not recorded in DECISION_LOG.md
- Control plane updates that are not consistent with the actual governance state (fabricated readiness)

---

### Backend Workcell

**Required Evidence Artifacts**
1. **Requirement analysis notes**: for each BI-ID in scope, a written interpretation of the requirement and its acceptance criteria that confirms the workcell understood the scope before implementing.
2. **Implementation evidence** (changed files listed): a specific, itemized list of all files created or modified, with: file path, nature of change (created / modified / deleted), and the BI-ID or AC-ID the change addresses.
3. **API contract updates** (API_CONTRACTS.md, if applicable): if the task involves defining or modifying an API endpoint, the API contract must be updated with: endpoint path, method, request shape, response shape, error codes, version.
4. **Developer validation report** (using VALIDATION_REPORT_TEMPLATE.md): a self-verification that the implementation satisfies the AC-IDs in scope, including what was tested locally, what passed, and what could not be verified locally.
5. **Evidence report** (ER-ID): a structured evidence record stored in EVIDENCE_LOG.md containing: ER-ID, task reference, BI-ID, AC-IDs addressed, changed file list, developer validation report reference, timestamp.
6. **Handoff artifact**: a completion handoff addressed to the next agent (Director, Integrator, or QA as appropriate) containing: ER-ID, task summary, unresolved items, next action.

**Optional Evidence Artifacts**
- Unit test results (if unit tests were added or run as part of the task)
- Integration test results (if backend integration tests exist and were run)
- Notes on implementation decisions made during the task (design rationale)

**What Is NOT Accepted as Evidence for the Backend Workcell**
- Claims without artifact references ("I implemented the login endpoint" without a file path)
- QA signoff — that is the QA Orchestrator's output; the Backend Workcell's developer validation is not a QA signoff
- Evidence reports from prior cycles that were not re-run for the current task
- API contract references without a current, accepted version in API_CONTRACTS.md
- Assertions that a task is complete without a completion handoff

---

### Frontend Workcell

**Required Evidence Artifacts**
1. **UI flow evidence**: a description of the user flow implemented, referencing the acceptance criteria it satisfies. Where possible, include component file paths and the user actions they support.
2. **API expectation evidence**: documentation of what API endpoints the frontend consumes, what request shapes it sends, and what response shapes it expects — with references to the accepted API contract version.
3. **Implementation evidence** (changed files listed): itemized list of all files created or modified with the same standard as Backend Workcell.
4. **Developer validation report** (using VALIDATION_REPORT_TEMPLATE.md): self-verification that the UI behavior satisfies the AC-IDs in scope, including what was verified visually or through frontend tests.
5. **Evidence report** (ER-ID): structured evidence record with ER-ID, task reference, BI-ID, AC-IDs addressed, changed file list, developer validation report reference, API contract version reference, timestamp.
6. **Handoff artifact**: completion handoff with ER-ID, task summary, unresolved items, next action.

**Optional Evidence Artifacts**
- Component test results (if frontend component tests were added or run)
- Accessibility check results (if in scope)
- UI state diagram or screen flow description (for complex flows)

**What Is NOT Accepted as Evidence for the Frontend Workcell**
- Backend behavior assumptions without a documented API contract reference — if the frontend expects a specific response shape, the API contract must be cited
- QA signoff — the Frontend Workcell's developer validation is not a QA signoff
- Claims without artifact references
- API expectation evidence that contradicts the accepted API contract without a recorded reconciliation decision

---

### Integrator

**Required Evidence Artifacts**
1. **Contract reconciliation record** (API_CONTRACTS.md updates): for each reconciled contract, an entry recording what was reconciled, which discrepancies were resolved, which are pending, and the reconciliation path for each BLOCKING item.
2. **Integration report** (IR-ID): structured report with contract check results, binding findings, build status, merge readiness assessment, cross-lane gaps, and integration recommendation.
3. **Pipeline/build status**: specific build run ID or timestamp, pass/fail status, failing components (if any), and responsible workcell per failure.
4. **Merge readiness assessment**: explicit status (READY / NOT_READY / READY_WITH_CONDITIONS) with the basis for the assessment and any conditions listed.

**Optional Evidence Artifacts**
- Binding check details (per-endpoint binding findings)
- Cross-lane gap records (if new gaps were identified during integration)

**What Is NOT Accepted as Evidence for the Integrator**
- Feature logic rewrites not covered by a reconciliation decision — the Integrator's evidence is about reconciliation and assessment, not feature implementation
- QA signoff — the Integrator produces integration readiness evidence, not QA signoff
- Merge readiness assessments produced without build status evidence
- Integration reports that omit BLOCKING discrepancies

---

### QA Workcell

**Required Evidence Artifacts**
1. **Test cases** (TC-IDs linked to AC-IDs): for each acceptance criterion in the QA scope, one or more test cases with: TC-ID, AC-ID, test scenario (positive/negative/boundary/permission/recovery/user-flow), preconditions, steps, expected result, test data.
2. **Execution evidence** (TC result per test case): for each TC-ID, the actual execution result: PASS / FAIL / BLOCKED / NOT_RUN, actual behavior observed, environment details (version, timestamp, test data used).
3. **Defect reports** (DEF-IDs linked to TC-IDs): for each FAIL result, a defect record with: DEF-ID, TC-ID, AC-ID, severity, reproduction steps, expected vs. actual behavior, environment details.
4. **QA validation report** (QVR-ID): structured report with execution summary, defect summary, coverage summary, per-criterion anchoring, independence confirmation, conditions (if CONDITIONAL_PASS), and QA recommendation (PASS / CONDITIONAL_PASS / FAIL / VALIDATION_UNAVAILABLE).
5. **QA recommendation**: explicit PASS / CONDITIONAL_PASS / FAIL / VALIDATION_UNAVAILABLE with rationale.

**Optional Evidence Artifacts**
- Regression scope document (which prior AC-IDs were checked for regression)
- Test data setup records
- Environment configuration records

**What Is NOT Accepted as Evidence for the QA Workcell**
- Developer self-validation as QA evidence — the developer's validation report is a development artifact; it does not satisfy the QA execution evidence requirement
- Test results from the developing workcell's local environment without Director approval for using that environment
- QA reports without TC-IDs linked to AC-IDs
- Test cases without expected results
- A QA recommendation that was produced by the same identity that developed the feature (unless a CONSTRAINED exception is on record)
- A PASS, CONDITIONAL_PASS or FAIL recommendation for an acceptance criterion with no anchored evidence — that criterion's only legal recommendation is VALIDATION_UNAVAILABLE

---

### Context Steward

**Required Evidence Artifacts**
1. **Assembled context pack** (CP-ID): a complete context pack document with: CP-ID, assembly date, job size, active handoff reference, source truth version, included artifacts list with IDs and paths, staleness check results, limitations disclosure.
2. **Context delta processing notes**: for each context delta processed, a processing record identifying: CD-ID, affected artifact IDs, stale context packs identified, refresh requests issued.
3. **Stale context detection record**: for each staleness check run, a record of: artifacts checked, staleness findings, recommendation (PROCEED_AS_IS / REFRESH_REQUIRED / BLOCK_AND_ESCALATE).

**Optional Evidence Artifacts**
- State recovery summary (SR-ID) when state recovery was performed
- Job size estimate rationale (when the size classification required judgment)

**What Is NOT Accepted as Evidence for the Context Steward**
- Assumptions about project state without control plane or handoff reference — all context must be artifact-traceable
- Context packs that do not disclose their limitations
- Context packs that include superseded source truth content without explicit disclosure

---

### Janitor

**Required Evidence Artifacts**
1. **Janitor report** (JR-ID): structured report with: scope of the pass, actions completed (archives, compactions), stale artifact register reference, orphan record list, items requiring Director decisions, risks retained.
2. **Stale artifact register entries** (SAR-ID): for each stale artifact detected, a record with: artifact path, type, stale reason, recommended action, detection timestamp.
3. **Archive candidates list**: list of handoffs archived, with source path, destination path, archival timestamp.
4. **Compaction summary** (if compaction occurred): list of records compacted, with original ID, compact summary, timestamp.

**Optional Evidence Artifacts**
- Orphan task detection records (if orphans were found)

**What Is NOT Accepted as Evidence for the Janitor**
- Silent deletions — any artifact removed or compacted without a corresponding janitor report entry
- Product decisions made without Director routing — the Janitor may not decide what to keep or discard from product artifacts
- Compaction of records not verified as fully resolved
- Archive actions taken on active handoffs (non-CONSUMED artifacts)

---

### Challenge Lane

**Required Evidence Artifacts**
1. **Challenge report** (CR-ID): structured report with: scope (item challenged), BLOCKING challenges (with evidence or testable failure mode), CONDITIONAL challenges, INFORMATIONAL findings, already-resolved items, and recommendation (PROCEED / PROCEED_WITH_CONDITIONS / HALT_FOR_RESOLUTION).
2. **Evidence or testable failure mode for each BLOCKING challenge**: every BLOCKING challenge must include either a specific artifact or decision reference that demonstrates the problem, or a step-by-step testable failure scenario with trigger conditions, expected behavior, and actual/predicted incorrect behavior.
3. **Severity classification**: for each finding, an explicit severity (CRITICAL / HIGH / MEDIUM / LOW) with rationale.

**Optional Evidence Artifacts**
- Failure mode records (FM-IDs) as supporting detail for complex failure scenarios
- Evidence assessment records (EA-IDs) as supporting detail for evidence sufficiency findings

**What Is NOT Accepted as Evidence for the Challenge Lane**
- Opinion-only challenges without concrete evidence or a testable failure mode — these are classified as INFORMATIONAL at most
- Challenges that re-litigate decisions already accepted in DECISION_LOG.md without new evidence
- Challenge reports that classify INFORMATIONAL findings as BLOCKING to force a halt
- Challenge reports that do not distinguish between BLOCKING, CONDITIONAL, and INFORMATIONAL findings
