# COMMAND_ROUTING_MATRIX.md
STATUS: DRAFT

## Purpose
This matrix maps every ADAPT command to its primary and secondary orchestrators, human approval requirements, and source code mutation authority. The Director Intake Agent reads this matrix when routing any incoming command.

---

## Routing Matrix

| Command | Primary Orchestrator | Secondary Orchestrator | Requires Human Approval | Can Mutate Source Code |
|---------|---------------------|----------------------|------------------------|------------------------|
| `Initialize ADAPT from requirements` | Director Lane | Onboarding Orchestrator | YES | NO |
| `Promote {{DOCUMENT}} as {{SOURCE_TRUTH_VERSION}}` | Director Lane | Source Truth Orchestrator | YES | NO |
| `Analyze requirements into source truth` | Source Truth Orchestrator | Director Lane | NO | NO |
| `Run Director intake` | Director Lane | Guardrail Orchestrators | NO | NO |
| `Onboard {{IDENTITY}} as {{ROLE}}` | Onboarding Orchestrator | Director Lane | YES | NO |
| `Plan milestone {{MILESTONE_ID}}` | Planning Orchestrator | Director Lane | YES (for output approval) | NO |
| `Approve milestone plan` | Director Lane | Planning Orchestrator | YES | NO |
| `Generate roadmap for {{WORKCELL_ID}}` | Planning Orchestrator | Director Lane | NO | NO |
| `Generate context pack for active handoff` | Context Steward | Director Lane | NO | NO |
| `Run atomic handoff dispatch` | Workcell Orchestrator | Context Steward | NO | YES (within scope contract only) |
| `Route gap {{GAP_ID}}` | Director Lane | Guardrail Orchestrators | NO | NO |
| `Resolve blocker {{BLK_ID}}` | Director Lane | Workcell Orchestrator | YES (for CRITICAL blockers) | NO |
| `Run integration review` | Integrator Orchestrator | Director Lane | NO | NO |
| `Run QA validation` | QA Orchestrator | Director Lane | NO | NO |
| `Trigger challenge review for {{ITEM}}` | Challenge Lane | Director Lane | NO | NO |
| `Run janitor pass` | Janitor Orchestrator | Director Lane | NO (archiving); YES (deletions) | NO |
| `Director consolidate cycle` | Director Lane | Guardrail Orchestrators | NO | NO |
| `Prepare next cycle` | Director Lane | Planning Orchestrator | YES | NO |

---

## Routing Rules

### R-01 — Primary Orchestrator Has Exclusive Initial Authority
The Primary Orchestrator is the only entity authorized to begin processing a command. The Secondary Orchestrator is engaged only when the Primary explicitly routes work to it or when the Primary is blocked and escalation is required.

### R-02 — Human Approval Required Means Stop-Before-Execute
When "Requires Human Approval = YES", the Primary Orchestrator must halt after preparing the approval request and wait for a human approval record before taking any action that modifies ADAPT state or creates new artifacts.

### R-03 — Source Code Mutation Is Workcell-Exclusive
Only `Run atomic handoff dispatch` may result in application source code mutation, and only within the scope defined in the active workcell's SCOPE_CONTRACT.md. All other commands must not write to or modify application source files. Any other command that would require source code mutation must stop and route to the Director.

### R-04 — Guardrail Orchestrators Are Always Available as Secondary
Guardrail Orchestrators may be engaged as a secondary check by any Primary Orchestrator before or after execution. A guardrail returning STOP_REQUIRED overrides all orchestrators and requires immediate stop.

### R-05 — Director Lane Is the Default Escalation Path
If a command cannot be routed (Primary Orchestrator is unavailable, blocked, or unregistered), the Director Lane is the default routing target. The Director Lane records the failure and determines the next action.

### R-06 — Context Steward Is Always a Valid Secondary for Execution Commands
For `Run atomic handoff dispatch`, the Context Steward is automatically engaged before execution to confirm the context pack is current and sufficient. This is not optional.

---

## Orchestrator Reference

| Orchestrator ID | Description |
|----------------|-------------|
| Director Lane | Central governance authority. Routes work, approves milestones, certifies work, consolidates cycles. |
| Source Truth Orchestrator | Manages source truth promotion, extraction, and version tracking. |
| Planning Orchestrator | Generates milestone plans, work slices, roadmaps, and dependency sequences. |
| Onboarding Orchestrator | Creates workcell folders and files; registers identities and roles. |
| Context Steward | Assembles context packs, processes context deltas, detects stale context. |
| Workcell Orchestrator | Executes bounded tasks under assigned authority within the scope contract. |
| Integrator Orchestrator | Reconciles contracts, assesses merge readiness, runs integration reviews. |
| QA Orchestrator | Executes independent QA validation, produces test cases, defect reports, and QA signoff. |
| Janitor Orchestrator | Identifies stale artifacts, archives consumed handoffs, compacts resolved history. |
| Challenge Lane | Challenges decisions, milestones, and work items using evidence or testable failure modes. |
| Guardrail Orchestrators | Enforces governance rules; returns STOP_REQUIRED when a violation is detected. |
