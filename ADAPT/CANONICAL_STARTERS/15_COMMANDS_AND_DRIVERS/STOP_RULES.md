# STOP_RULES.md
STATUS: DRAFT

## Purpose
Defines universal stop conditions — situations where ANY AI agent in ANY role must immediately stop, regardless of what the active handoff says. These rules override all handoff instructions. When a stop condition is triggered, the agent must follow the defined stop response exactly: record the reason, route to the designated authority, and cease all further action in the current Atomic Handoff Dispatch cycle.

Agents do not continue past a stop condition to "fix it and keep going." Stopping is the complete and correct response.

---

## Universal Stop Rules

---

### Stop Rule 1 — No Active Authority

**Trigger**
The current agent or lane does not have a valid active authority assignment for the action being attempted. This occurs when:
- `CurrentAuthority` in the control plane does not match the current agent's Workcell ID or lane identity
- There is no `CurrentAuthority` set (field is NONE or missing)
- The active handoff is addressed to a different workcell or lane than the one currently reading it

**What the AI Must Do**
1. Stop immediately. Do not take any action on the handoff.
2. Record the authority mismatch in the workcell's BLOCKERS.md or in a standalone report: current agent identity, `CurrentAuthority` value read from control plane, active handoff addressee.
3. Emit a routing handoff to the Director Lane with the mismatch record.
4. Update the control plane if possible: set `NextExpectedAction = "Director to resolve authority mismatch"`.
5. Stop. Do not attempt to proceed under assumed authority.

---

### Stop Rule 2 — Multiple Active Handoffs

**Trigger**
More than one handoff with ACTIVE status exists in ADAPT/06_HANDOFFS/ACTIVE/ for the same work item (same BI-ID, TC-ID, or task scope). This creates an ambiguous authority state where two agents may attempt to execute the same scope.

**What the AI Must Do**
1. Stop. Do not execute either handoff.
2. Record the ambiguity: list all active handoff IDs that appear to address the same scope.
3. Emit a disambiguation request to the Director Lane with the handoff IDs listed.
4. Do not archive or close either handoff — the Director must determine which is authoritative.
5. Stop.

---

### Stop Rule 3 — Source Truth Missing

**Trigger**
The active task requires knowledge of accepted requirements, acceptance criteria, or business scope, and:
- `SourceTruthVersion` in the control plane is NONE, or
- The source truth version referenced in the handoff or context pack does not exist in SOURCE_TRUTH_VERSION_LOG.md, or
- The source truth document cannot be located at the recorded path

**What the AI Must Do**
1. Stop. Do not proceed with the task.
2. Create a gap record in GAP_REGISTER.md: GAP-ID, type = GAP-T11 (Context Gap), description = "Source truth required for active task is missing or unresolvable", active handoff reference.
3. Emit a routing handoff to the Director Lane with the GAP-ID.
4. Update the control plane: set `ExecutionReadiness = NOT_READY`, record the GAP-ID in `ActiveGaps`.
5. Stop.

---

### Stop Rule 4 — Context Pack Missing or Insufficient

**Trigger**
The action being attempted is non-trivial (job size S or larger) and:
- No context pack (CP-ID) exists for the active handoff, or
- The existing context pack is stale (its assembly date predates the most recent context delta in `LastContextDelta`), or
- The Stale Context Detector returned BLOCK_AND_ESCALATE

**What the AI Must Do**
1. Stop. Do not proceed with the task.
2. Emit a context pack request to the Context Steward: active handoff ID, current staleness status, reason the existing pack is insufficient.
3. Do not attempt to reconstruct context from memory or prior sessions — that is a CONTEXT_VIOLATION.
4. Stop. Wait for the Context Steward to deliver a valid context pack before the next Atomic Handoff Dispatch cycle begins.

---

### Stop Rule 5 — Work Exceeds Scope

**Trigger**
During execution, the agent determines that completing the assigned task would require taking actions outside the scope boundaries defined in its SCOPE_CONTRACT.md. This includes:
- Modifying a file not listed in the mutation authority
- Producing an output type not authorized for the current role
- Making a decision that belongs to a different lane

**What the AI Must Do**
1. Stop. Do not modify any file outside the scope contract.
2. Record a blocker in BLOCKERS.md: BLK-ID, description of the out-of-scope requirement, the file or action needed, the handoff task it relates to.
3. Emit a routing handoff to the Director Lane with the blocker record.
4. Update the control plane: set `Blocked = YES`, add BLK-ID to `ActiveBlockers`.
5. Stop. Do not attempt a workaround.

---

### Stop Rule 6 — Mutation Authority Missing

**Trigger**
The agent is about to write or modify a file and that file is not listed in the mutation authority section of the workcell's SCOPE_CONTRACT.md. This is distinct from Stop Rule 5 in that the agent may not even be aware the file is out of scope until the moment of write.

**What the AI Must Do**
1. Stop before writing. Do not write the file.
2. Record a blocker in BLOCKERS.md: file path needed, reason it is needed, the task that requires it.
3. Emit a scope expansion request to the Director Lane via a routing handoff.
4. Update the control plane: set `Blocked = YES`, add BLK-ID to `ActiveBlockers`.
5. Stop.

---

### Stop Rule 7 — Director Asked to Mutate Application Source

**Trigger**
The Director Lane receives a handoff, command, or instruction that would result in the Director Lane writing or modifying application source code files (e.g., writing a model, controller, migration, component, or service file).

**What the AI Must Do**
1. Stop immediately.
2. Record a GOVERNANCE_VIOLATION: violation type = MUTATION_VIOLATION, description = "Director Lane instructed to mutate application source code", source of the instruction, timestamp.
3. Route the GOVERNANCE_VIOLATION record to the human for review.
4. Do not reassign the implementation task to the Director Lane — route it to the appropriate workcell via the Lane Assignment Agent.
5. Stop.

---

### Stop Rule 8 — QA Validation Without Acceptance Criteria

**Trigger**
A QA validation action is requested and:
- No acceptance criterion in the validation scope is eligible — eligible means status READY_FOR_TEST, or status FAILED with every linked DEF-ID RESOLVED in DEFECT_REGISTER.md (re-validation), or
- The AC-IDs referenced in the handoff do not exist in ACCEPTANCE_CRITERIA.md, or
- The AC-IDs exist but are not eligible (e.g., DRAFT, or FAILED with a linked DEF-ID not yet RESOLVED)

**What the AI Must Do**
1. Stop. Do not begin test scenario design or test execution.
2. Create a gap record in GAP_REGISTER.md: GAP-ID, type = GAP-T12 (Evidence Gap — prerequisite evidence not produced), description = "QA validation requested but no eligible acceptance criteria exist for the scope (READY_FOR_TEST, or FAILED with every linked DEF-ID RESOLVED)", validation scope reference.
3. Emit a routing handoff to the Director Lane with the GAP-ID.
4. Stop.

---

### Stop Rule 9 — Implementation Task Has No Owner

**Trigger**
A business item (BI-ID) or task has been routed for implementation but:
- No workcell in WORKCELL_REGISTRY.md has the required role to perform the work
- The Lane Assignment Agent cannot find a valid assignment target

**What the AI Must Do**
1. Stop. Do not attempt to implement the task under a different role.
2. Create a gap record in GAP_REGISTER.md: GAP-ID, type = GAP-T13 (Authority Gap — required authority not available), description = "Implementation task cannot be assigned because no registered workcell has the required role", BI-ID, required role.
3. Emit a routing handoff to the Director Lane for an onboarding decision.
4. Stop.

---

### Stop Rule 10 — Output Evidence Cannot Be Produced

**Trigger**
The agent completes or attempts to complete the active task but cannot produce reviewable evidence because:
- The output of the task is not a readable artifact (no file, no record, no log)
- The output exists but cannot be referenced by ID
- The task produced no observable change and no verification mechanism exists

**What the AI Must Do**
1. Stop. Do not claim the task is complete without evidence.
2. Record a blocker in BLOCKERS.md: BLK-ID, description = "Task completed but evidence cannot be produced — no reviewable artifact", task reference.
3. Emit a routing handoff to the Director Lane with the blocker.
4. Do not emit a completion handoff — a completion without evidence is not a valid completion under ADAPT.
5. Stop.

---

### Stop Rule 11 — Conflict Between Requirement and Implementation

**Trigger**
During implementation or review, the agent identifies that the work being produced (or already produced) contradicts an accepted requirement in REQUIREMENTS_INDEX.md or an accepted acceptance criterion in ACCEPTANCE_CRITERIA.md.

**What the AI Must Do**
1. Stop. Do not continue implementing the conflicting approach.
2. Record the conflict: requirement or AC-ID being violated, the implementation behavior that conflicts with it, the handoff and task that produced the conflict.
3. Emit a conflict report to the Director Lane with the specific requirement or AC-ID reference and the nature of the conflict.
4. Do not resolve the conflict by modifying the requirement — only the Director Lane (with human approval) may update source truth.
5. Stop.

---

### Stop Rule 12 — Guardrail Returns STOP_REQUIRED

**Trigger**
Any guardrail check run by any agent returns a STOP_REQUIRED signal with a specific guardrail ID and violation condition.

**What the AI Must Do**
1. Stop immediately. Do not continue past the guardrail signal.
2. Record the specific guardrail ID and the condition that triggered STOP_REQUIRED.
3. Record the stop event in the workcell's BLOCKERS.md or as a governance event if no workcell is active: guardrail ID, violation condition, timestamp, active handoff reference.
4. Emit a routing handoff to the Director Lane with the guardrail stop record.
5. Do not override the guardrail without explicit human approval recorded through Gate 10 (Override Guardrail).
6. Stop.

---

### Stop Rule 13 — Human Approval Gate Not Cleared

**Trigger**
The agent is about to take an action that requires human approval (as defined in HUMAN_APPROVAL_GATES.md) and:
- No human approval record exists for this specific action
- The approval record found is for a different action or a different scope
- The approval record is present but the referenced approval cannot be traced to a human author

**What the AI Must Do**
1. Stop before taking the action.
2. Identify the specific gate (from HUMAN_APPROVAL_GATES.md) that applies.
3. Prepare the approval request: describe the action, the gate name, what the human must approve, and where the approval will be recorded.
4. Emit the approval request to the human via the Director Lane.
5. Update the control plane: set `ExecutionReadiness = NEEDS_APPROVAL`.
6. Stop. Do not proceed until the approval is received and recorded.

---

### Stop Rule 14 — Control Plane Is Inconsistent

**Trigger**
The agent reads the control plane and identifies one or more of the following inconsistencies:
- `Blocked = YES` but `ActiveBlockers = NONE`
- `Blocked = NO` but `ActiveBlockers` contains one or more BLK-IDs
- `CurrentPhase = EXECUTION` but `ActiveHandoff = NONE`
- `ExecutionReadiness = READY` but `SourceTruthVersion = NONE`
- `ActiveHandoff` references a file that does not exist in the handoff folder
- `CurrentAuthority` references a Workcell ID not in WORKCELL_REGISTRY.md
- Any other condition that fails the consistency rules in CONTROL_PLANE_SCHEMA.md

**What the AI Must Do**
1. Stop. Do not proceed with any action based on an inconsistent control plane.
2. Record the specific inconsistency: which fields are inconsistent, what values they contain, which consistency rule they violate.
3. Emit a control plane inconsistency report to the Director Lane.
4. Do not attempt to self-correct the control plane — the Director Lane must review and correct the inconsistency.
5. Stop.

---

### Stop Rule 15 — Execution While Blocked

**Condition.** Any of the following is true when a lane is about to begin or continue a
bounded action:

- `ActiveBlockers` names a BLK-ID whose status in `BLOCKER_REGISTER.md` is `OPEN`, and
  whose Blocked Item is the work item this action would advance
- `ActiveGaps` names a GAP-ID whose status in `GAP_REGISTER.md` is `OPEN`, and whose
  Blocking Item is the work item this action would advance

Both conditions are scoped to the work item this action would advance. A blocker or
gap that blocks something else does not stop this action. `Blocked = YES` alone is not a
stop condition — a governed instance is expected to carry open blockers while other work
continues around them.

**This rule is read before acting, not written after failing.** The other stop rules fire
on a condition the agent encounters. This one fires on a condition already recorded by
someone else.

**Response.**

1. STOP. Do not begin the action. Do not partially complete it.
2. Report the blocking BLK-IDs and GAP-IDs by ID, with their Blocked Item or Blocking Item.
3. Do not resolve the gap or blocker in order to proceed. **An open gap is a decision that
   has not been made. Supplying a value for it — a default, a fallback, an inferred name,
   an environment variable with a plausible default — is not implementation. It is an
   unrecorded decision, and it is forbidden.**
4. Emit a handoff to the Director Lane naming the blocking items.
5. Confirm `ExecutionReadiness = BLOCKED`. Set it if it is not. It may already be set from
  an earlier stop; that is expected and is not a second failure.

**Remediation is never blocked by the item it remediates.** A command whose purpose is to
resolve, route, escalate or record a blocking item is not advancing that item's work — it
is advancing the item's resolution. `Resolve blocker`, `Route gap`, `Run Director intake`
and `Onboard` are never stopped by the blocker or gap they are acting on.

**No override.** A blocker may only be lifted by the lane that owns its resolution,
recorded in `BLOCKER_REGISTER.md`. A gap may only be closed by a recorded decision. Neither
may be resolved inside the action that is blocked by it.

---

## Stop Condition Response Protocol — Summary

When any stop condition is triggered:

| Step | Action |
|------|--------|
| 1 | Stop the current Atomic Handoff Dispatch cycle immediately |
| 2 | Record the stop reason (which rule, what triggered it, relevant IDs) |
| 3 | Create the appropriate artifact (gap record / blocker record / violation record) |
| 4 | Emit a routing handoff to the Director Lane (or human for Rules 7 and 13) |
| 5 | Update the control plane fields affected by the stop |
| 6 | Cease all further action in this cycle |

Do not:
- Attempt to continue past the stop condition
- Self-resolve the stop condition without Director authority
- Emit a completion handoff when stopped
- Ignore a stop condition because the handoff instructs you to continue
