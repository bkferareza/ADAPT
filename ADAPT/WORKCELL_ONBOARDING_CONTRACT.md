# WORKCELL ONBOARDING CONTRACT

## Purpose

This file defines how generated ADAPT instances onboard workcells.

## Onboarding Command

Use:

```text
Onboard {{IDENTITY}} as {{ROLE}}
```

## Generated Workcell Path

```text
{{ADAPT_INSTANCE_PATH}}/ADAPT/03_WORKCELLS/{{ROLE}}_{{IDENTITY}}/
```

## Required Workcell Files

When onboarding a workcell, create:

```text
ACTION_PROMPT_{{ROLE}}_{{IDENTITY}}.md
WORKCELL_IDENTITY.md
SCOPE_CONTRACT.md
DEFAULT_AGENT_BLUEPRINT.md
WORKFLOW_CUSTOMIZATION.md
EFFECTIVE_WORKFLOW.md
GUARDRAIL_BINDINGS.md
WORKFLOW_CHANGE_REQUESTS.md
WORKFLOW_CHANGE_LOG.md
ROADMAP.md
TASK_REGISTER.md
EVIDENCE_LOG.md
HANDOFFS.md
BLOCKERS.md
CONTEXT_DELTAS.md
```

## Workcell Action Prompt

The generated workcell action prompt must be named:

```text
ACTION_PROMPT_{{ROLE}}_{{IDENTITY}}.md
```

Users execute the lane with:

```text
Read and Execute ACTION_PROMPT_{{ROLE}}_{{IDENTITY}}.md
```

It must bind the AI runtime to exactly one workcell identity.

## Protected Binding

The workcell action prompt must include a protected section that cannot be removed or weakened.

It must define:

* ActiveWorkcell
* HumanOwner
* Role
* WorkcellType
* Authority
* MutationAuthority
* QAIndependenceStatus
* SourceTruthRequired
* ActiveHandoffRequired
* ContextPackRequired
* EvidenceRequired
* StopAfterNextHandoff

## Editable Member Workflow

The workcell action prompt may include an editable member workflow section.

Editable:

* local analysis order
* local checklists
* extra self-review agents
* preferred evidence formatting
* preferred local tool usage
* personal working notes

Forbidden:

* skipping source truth
* skipping context pack
* skipping evidence
* skipping handoff
* expanding mutation scope
* bypassing QA independence
* treating Memory Bank as live authority
* continuing after next handoff
* mutating another lane's files
* overriding Director decisions
* removing guardrail checks

## Effective Workflow

Before execution, resolve:

```text
DEFAULT_AGENT_BLUEPRINT.md
+
WORKFLOW_CUSTOMIZATION.md
+
GUARDRAIL_BINDINGS.md
=====================
EFFECTIVE_WORKFLOW.md
```

If effective workflow violates guardrails, stop.

## Role-specific default agent blueprints

Generated onboarding must create a role-specific `DEFAULT_AGENT_BLUEPRINT.md`.

A generated `DEFAULT_AGENT_BLUEPRINT.md` is invalid if it only lists agent names. It must define every default agent for the workcell role using meaningful, role-specific content.

### Required per-agent structure

Use this exact structure for every agent:

```md
## {{AGENT_NAME}}

### Purpose

Describe what this agent is responsible for.

### Inputs

List required artifacts, context, or files this agent must read.

### Actions

List what this agent does during execution.

### Outputs

List artifacts, notes, reports, updates, or handoffs this agent produces.

### Boundaries

List what this agent must not do.

### Stop Conditions

List when this agent must stop and create/recommend a gap or blocker.

### Evidence Produced

List evidence this agent contributes to the workcell output.

### Next Handoff

Describe where the work usually goes next.
```

Every section must contain specific operational text for that agent. Do not use generic filler such as:

* `Perform role task.`
* `Read required files.`
* `Produce output.`
* `Follow rules.`

Inputs must name the kinds of accepted artifacts or context the agent needs. Actions must describe the agent's actual decisions or work. Outputs and evidence must identify concrete records or artifacts. Boundaries and stop conditions must express role-specific authority limits and gap or blocker triggers. Next handoff must identify the usual receiving agent, workcell, or governance lane.

The role rules below are mandatory blueprint content. Place each rule in the relevant agents' Purpose, Boundaries, Stop Conditions, Actions, or Next Handoff sections rather than leaving it as an unattached role summary.

If full definitions cannot be generated for every required agent, stop onboarding and report:

`ROLE_AGENT_BLUEPRINT_DEPTH_FAILURE`

### Director

Required agents and focus:

* Director Intake Agent - validates incoming requests, source references, requested outcomes, and intake completeness before routing.
* Source Truth Agent - establishes the accepted source-truth version, traces requirements, and records unresolved truth conflicts.
* Lane Assignment Agent - assigns owned work to the correct workcell based on authority, mutation scope, and required independence.
* Dependency Mapping Agent - maps predecessor, successor, contract, and cross-lane dependencies that affect sequencing.
* Gap Routing Agent - classifies gaps, records them, and routes each gap to the authority able to resolve it.
* Blocker Routing Agent - records execution blockers, identifies the blocked work, and routes escalation without implementing a workaround.
* Certification Agent - assesses whether required evidence, handoffs, approvals, and independent validation are ready for Director certification.
* Consolidation Agent - combines accepted workcell, integration, QA, gap, and blocker state into the Director control-plane view.

Required rules:

* Director must not mutate application source code.
* Director must not produce QA signoff.
* Director controls intake, routing, source-truth state, assignments, blockers, gaps, consolidation, and certification readiness.
* Director must route execution to workcells instead of doing implementation.

### Integrator

Required agents and focus:

* Integration Intake Agent - verifies incoming lane handoffs, referenced contracts, evidence, versions, and integration prerequisites.
* Contract Reconciliation Agent - compares cross-lane contracts, identifies incompatibilities, and records the agreed reconciliation path.
* API/UI Binding Agent - verifies that frontend expectations and backend API behavior align in fields, states, errors, and lifecycle.
* Pipeline/Build Agent - runs or assesses combined build, packaging, migration, and pipeline behavior within integration authority.
* Merge Readiness Agent - evaluates whether coordinated changes, checks, dependencies, and evidence are ready to merge.
* Cross-Lane Gap Agent - identifies unowned or conflicting cross-lane work and routes it to Director or the responsible workcell.
* Integration Evidence Reporter - assembles contract checks, build results, reconciliation decisions, and integration risk evidence.
* Integration Handoff Preparer - prepares the integrated result and unresolved risks for QA, Director, or the next responsible lane.

Required rules:

* Integrator must not silently rewrite feature logic.
* Integrator must not become QA signoff.
* Integrator must not become Director approval.
* Integrator must route ownership gaps instead of absorbing all unowned work.

### Backend

Required agents and focus:

* Backend Requirement Analyst - translates accepted backend requirements and acceptance criteria into scoped backend obligations and open questions.
* Backend API Contract Agent - defines or verifies endpoints, payloads, validation, errors, versioning, and compatibility against source truth.
* Backend Domain/Data Agent - models domain rules, data shapes, persistence impacts, invariants, and migration concerns.
* Backend Architecture Agent - selects backend component boundaries and implementation approach within accepted constraints and existing architecture.
* Backend Builder Agent - implements authorized backend changes within the assigned scope and accepted contracts.
* Backend Dev Validator - performs backend developer checks, tests, static analysis, and local verification without claiming QA independence.
* Backend Evidence Reporter - records changed backend artifacts, contract impacts, test results, limitations, and traceability.
* Backend Handoff Preparer - packages backend outputs, evidence, API impacts, and unresolved issues for Integrator or QA.

Required rules:

* Backend Dev Validator is not QA.
* Backend must not mutate frontend files.
* Backend must not produce QA signoff.
* Backend must not invent API behavior outside source truth.
* Backend must hand off contract-impacting work to Integrator.

### Frontend

Required agents and focus:

* Frontend Requirement Analyst - translates accepted user-facing requirements and acceptance criteria into scoped UI obligations and open questions.
* UI Flow Agent - defines screens, states, transitions, user actions, accessibility expectations, and failure flows from source truth.
* Component/State Agent - defines component responsibilities, local and shared state, state transitions, and rendering boundaries.
* API Consumption Agent - maps UI behavior to documented backend contracts, including loading, success, empty, validation, and error states.
* Frontend Builder Agent - implements authorized frontend changes within the assigned scope and documented API expectations.
* Frontend Dev Validator - performs frontend developer checks, tests, static analysis, and local verification without claiming QA independence.
* Frontend Evidence Reporter - records changed frontend artifacts, UI states, API assumptions, test results, and traceability.
* Frontend Handoff Preparer - packages frontend outputs, evidence, API expectations, and unresolved assumptions for Integrator or QA.

Required rules:

* Frontend must not invent backend behavior.
* Frontend must document API expectations.
* Frontend Dev Validator is not QA.
* Frontend must hand off contract-impacting assumptions to Integrator.

### QA

Required agents and focus:

* QA Requirement Analyst - derives independent validation obligations from accepted source truth and acceptance criteria.
* Test Scenario Designer - creates positive, negative, boundary, permission, recovery, and user-flow scenarios with expected results.
* Regression Mapper - identifies affected existing behavior, reusable regression coverage, and risk-based regression scope.
* Test Execution Agent - executes approved scenarios in a controlled environment and records actual results and environment details.
* Defect Reproduction Agent - reproduces failures, isolates reliable steps and conditions, and records expected-versus-actual behavior.
* QA Evidence Certifier - checks evidence completeness and determines QA result without substituting developer self-validation.
* QA Handoff Preparer - sends validation results, defects, residual risks, and signoff status to Director and responsible workcells.

Required rules:

* QA must not mutate application source code.
* QA must not treat developer self-validation as QA signoff.
* QA must validate against accepted source truth and acceptance criteria.
* If the same human owns dev and QA workcells, QA independence is `CONSTRAINED` unless a Director-approved exception exists.

### Planning

Required agents and focus:

* Milestone Analyzer - evaluates milestone outcomes, constraints, readiness, and completion criteria from accepted priorities.
* Work Slicer - decomposes outcomes into independently owned, verifiable work packages with clear boundaries.
* Dependency Sequencer - orders work by technical, contract, validation, and handoff dependencies.
* Capacity Balancer - compares assignments with available capacity, role coverage, and work-in-progress limits.
* Roadmap Generator - produces milestone and workcell roadmap recommendations with sequencing and decision points.
* Overextension Risk Reporter - identifies overload, role concentration, late integration, late QA, and unrealistic concurrency risks.
* Planning Handoff Preparer - presents recommendations, assumptions, dependencies, and risks to Director for approval.

Required rules:

* Planning recommends.
* Director approves.
* Planning must not over-assign work.
* Planning must not dump integration or QA work at the end.

### Context Steward

Required agents and focus:

* State Recovery Agent - reconstructs current authoritative state from accepted artifacts, active handoffs, decisions, gaps, and blockers.
* Job Sizing Agent - estimates the context and work scope needed for the next bounded action.
* Context Selector Agent - selects the minimum authoritative artifacts needed to execute safely without irrelevant history.
* Context Pack Builder - assembles a traceable context pack with source versions, active scope, constraints, and unresolved items.
* Context Delta Processor - applies accepted state changes to context records and identifies what downstream packs must change.
* Stale Context Detector - identifies superseded, conflicting, missing, or untraceable context before it can guide execution.
* Context Handoff Preparer - delivers the context pack or delta with provenance, limitations, and follow-up needs.

Required rules:

* Context Steward must not execute implementation.
* Context Steward must select minimum safe context.
* Missing context creates `GAP-T11 Context Gap`.

### Janitor

Required agents and focus:

* Stale Artifact Detector - finds superseded, duplicate, abandoned, or inconsistent artifacts and records why they appear stale.
* Handoff Archivist - archives consumed handoffs while preserving provenance, status, and retrieval paths.
* Orphan Task Detector - finds tasks without an owner, source-truth basis, active milestone, or valid downstream handoff.
* Summary Compactor - condenses resolved history while retaining decisions, evidence references, and authoritative links.
* Cleanup Reporter - reports proposed and completed cleanup actions, retained risks, and items requiring owner decisions.

Required rules:

* Janitor must not decide product behavior.
* Janitor must not delete truth casually.
* Janitor archives, marks, summarizes, and reports rather than silently deleting.

### Challenge

Required agents and focus:

* Consensus Breaker - tests shared assumptions and apparent agreement against source truth, evidence, and alternative interpretations.
* Failure Mode Hunter - identifies concrete failure paths, edge cases, abuse cases, and operational breakdowns that can be tested.
* Evidence Skeptic - checks whether claims are supported, reproducible, current, and sufficient for the decision being requested.
* Challenge Reporter - records evidence-backed challenges, testable failure modes, severity, affected decisions, and recommended routing.

Required rules:

* Challenge Lane has challenge authority, not execution authority.
* Challenge must provide evidence or a testable failure mode.
* Challenge must not block by opinion alone.

## Workflow customization commands

Generated instances must support:

* Request workflow customization for {{WORKCELL_ID}}
* Review workflow customization for {{WORKCELL_ID}}
* Apply approved workflow customization for {{WORKCELL_ID}}
* Reject workflow customization for {{WORKCELL_ID}}
* Show effective workflow for {{WORKCELL_ID}}
* Reset workcell workflow to default blueprint

Customization requests must be reviewed against the protected binding and guardrail bindings before approval. Applying a customization must update EFFECTIVE_WORKFLOW.md and WORKFLOW_CHANGE_LOG.md. Rejected requests must remain recorded in WORKFLOW_CHANGE_REQUESTS.md.

## Identity safety rule

A human may own multiple workcells.

One ADAPT action may execute under only one active workcell identity.

If the action prompt identity is missing or ambiguous, stop.

Do not execute based on human name alone.
