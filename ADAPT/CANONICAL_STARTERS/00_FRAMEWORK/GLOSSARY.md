# Glossary

STATUS: DRAFT
VERSION: {{ADAPT_VERSION}}
PROJECT: {{PROJECT_NAME}}

## Purpose

Defines ADAPT terminology used throughout this instance. All AI agents and team members must use these definitions consistently.

## Terms

**ADAPT Instance**
The project-specific governance folder scaffolded from the ADAPT framework source. Contains all 16 governance folders for one project.

**Atomic Handoff Dispatch**
The core ADAPT operating rule: every ADAPT run recovers state, validates authority, executes one bounded action, produces evidence, emits a handoff, and stops. No silent continuation.

**Acceptance Criteria (AC)**
Verifiable conditions derived from source truth that define when a requirement is satisfied. Acceptance criteria are the basis for QA test scenarios.

**Blocked**
State in which a bounded action cannot proceed due to a missing dependency, authority, evidence, or source truth. Blocked state must be recorded in BLOCKER_REGISTER.md and routed to the Director.

**Canonical Starter**
 A project-neutral starter file in CANONICAL_STARTERS/ that the scaffold copies into a new ADAPT instance before populating with project-specific facts.

**Certification**
Director-issued confirmation that a body of work meets evidence, handoff, and acceptance criteria requirements. Required before release.

**Context Delta**
A structured record of the state changes produced by one ADAPT action. Consumed by the next action to update context without re-reading all history.

**Context Economy**
The system of context packs, deltas, budgets, and stale detection that governs what context an AI agent loads for each bounded action.

**Context Gap (GAP-T11)**
A missing required piece of context needed to safely execute a bounded action. Must be recorded in GAP_REGISTER.md and resolved before execution.

**Context Pack**
The minimum authoritative context bundle assembled for one bounded ADAPT action. Declares scope, references source versions, and lists what is excluded.

**Control Plane**
PROJECT_CONTROL_PLANE.md in 02_DIRECTOR_LANE/. The single source of current project state, active milestone, active handoff, and execution readiness.

**Decision Gap (GAP-T10)**
A technical or architectural decision not yet made that blocks or creates uncertainty for implementation. Must be recorded and routed to the appropriate authority.

**Director Lane**
The intake, routing, source-truth promotion, assignment, gap classification, blocker routing, and certification lane. Does not implement or produce QA signoff.

**Effective Workflow**
The resolved combination of DEFAULT_AGENT_BLUEPRINT.md + WORKFLOW_CUSTOMIZATION.md + GUARDRAIL_BINDINGS.md for a specific workcell. Governs how that workcell executes.

**Evidence**
Concrete, reviewable artifacts that demonstrate work was performed against source truth. Required for all accepted work. See EVIDENCE_STANDARD_BY_ROLE.md.

**Gap**
An unresolved missing decision (GAP-T10), missing context (GAP-T11), or other unresolvable item that blocks or risks execution. Gaps are classified, recorded, and routed.

**Guardrail**
An enforcement rule in 07_GUARDRAILS/ that checks whether a bounded action violates a governance constraint. A STOP_REQUIRED result halts the action.

**Handoff**
A structured artifact that transfers work, evidence, and state from one lane to another. Handoffs are stored in 06_HANDOFFS/ACTIVE/ until consumed.

**Human Approval Gate**
An action that requires explicit human approval before it can proceed. Defined in HUMAN_APPROVAL_GATES.md. AI agents must stop and request approval at these gates.

**Memory Bank**
Reference documents in 14_MEMORY_BANK/. Not live source authority. Cannot be used as the basis for governance decisions.

**QA Independence**
The requirement that QA validation is performed by a different agent or human than the one who developed the feature. Ensures unbiased validation.

**Source Truth**
An explicitly promoted, versioned document (requirements, design, contract) that governs ADAPT decisions. Must be promoted via the Director Lane.

**Workcell**
A person-role folder in 03_WORKCELLS/ with a scope contract, agent blueprint, task register, evidence log, and handoffs. Created at onboarding.

**Workcell Identity**
The binding of a human to a specific role within a specific workcell. Every ADAPT execution must occur under one active workcell identity.
