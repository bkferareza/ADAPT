# Role Workcell Blueprints

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

This document is a reference for all supported roles in the ADAPT framework. For each role it lists: the role description, required agents, and key governance rules. This file is role-neutral and project-neutral — it describes the ADAPT role model, not a specific project's team composition.

When a workcell is onboarded, a DEFAULT_AGENT_BLUEPRINT.md is generated for that workcell. That file contains the full 8-section agent definition for every agent in the role, covering: Purpose, Trigger Condition, Inputs, Outputs, Execution Steps, Evidence Requirements, Handoff Conditions, and Guardrail Bindings.

---

## Role 1: Director

**Description:** The Director Lane is the governance control plane for the entire ADAPT instance. It owns intake, routing, source truth promotion, workcell assignment, gap and blocker management, certification of completed work, and consolidation of project state.

### Required Agents

- Director Intake Agent
- Source Truth Agent
- Lane Assignment Agent
- Dependency Mapping Agent
- Gap Routing Agent
- Blocker Routing Agent
- Certification Agent
- Consolidation Agent

### Key Governance Rules

- Must not mutate application source code under any circumstance.
- Controls all intake, routing, source truth promotion, assignment, blocker escalation, gap classification, consolidation, and certification — no other lane may perform these functions unilaterally.
- Routes execution to workcells rather than performing implementation directly; Director does not write code, schemas, or UI components.
- Must not produce QA signoff; QA independence is owned by the QA Engineer role.
- All work routing must be accompanied by an active handoff artifact; routing without a handoff is a governance violation.

> Note: DEFAULT_AGENT_BLUEPRINT.md generated at onboarding time will contain the full 8-section definition for each agent listed above.

---

## Role 2: Integrator

**Description:** The Integrator Lane manages cross-lane integration concerns — API contracts, UI/backend bindings, pipeline and build coordination, and merge readiness — ensuring that independently produced workcell outputs combine correctly.

### Required Agents

- Integration Intake Agent
- Contract Reconciliation Agent
- API/UI Binding Agent
- Pipeline/Build Agent
- Merge Readiness Agent
- Cross-Lane Gap Agent
- Integration Evidence Reporter
- Integration Handoff Preparer

### Key Governance Rules

- Must not silently rewrite feature logic to make integration work; logic conflicts must be surfaced as gaps or blockers and routed to the Director.
- Must not act as a QA signoff mechanism; integration validation is not a substitute for independent QA.
- Must not act as a Director approval mechanism; integration readiness does not grant release authority.
- Must route ownership gaps — when no workcell claims responsibility for an integration surface — rather than absorbing unowned work into the Integrator Lane.
- Contract-breaking changes identified during integration must be escalated to the originating workcell and Director before any merge proceeds.

> Note: DEFAULT_AGENT_BLUEPRINT.md generated at onboarding time will contain the full 8-section definition for each agent listed above.

---

## Role 3: Backend Developer

**Description:** The Backend Developer workcell is responsible for designing and implementing server-side logic, data models, API contracts, and architecture components within the scope assigned by the Director Lane.

### Required Agents

- Backend Requirement Analyst
- Backend API Contract Agent
- Backend Domain/Data Agent
- Backend Architecture Agent
- Backend Builder Agent
- Backend Dev Validator
- Backend Evidence Reporter
- Backend Handoff Preparer

### Key Governance Rules

- Backend Dev Validator performs developer self-validation only; it is not a substitute for independent QA signoff.
- Must not mutate frontend files, UI components, or styling; frontend concerns belong to the Frontend Developer workcell.
- Must not produce QA signoff under any circumstance, including for backend-only acceptance criteria.
- Must not invent API behavior, data structures, or business rules that are not grounded in accepted source truth; deviations must be raised as gaps.
- Any work that alters or establishes an API contract must be handed off to the Integrator Lane before it is considered complete.

> Note: DEFAULT_AGENT_BLUEPRINT.md generated at onboarding time will contain the full 8-section definition for each agent listed above.

---

## Role 4: Frontend Developer

**Description:** The Frontend Developer workcell is responsible for building user interface components, managing client-side state, and consuming backend APIs within the scope assigned by the Director Lane.

### Required Agents

- Frontend Requirement Analyst
- UI Flow Agent
- Component/State Agent
- API Consumption Agent
- Frontend Builder Agent
- Frontend Dev Validator
- Frontend Evidence Reporter
- Frontend Handoff Preparer

### Key Governance Rules

- Must not invent backend behavior, API response shapes, or business logic not present in accepted source truth or accepted API contracts; assumptions must be documented as gaps.
- Must document all API expectations explicitly so the Integrator Lane can validate binding correctness.
- Frontend Dev Validator performs developer self-validation only; it is not a substitute for independent QA signoff.
- Must not produce QA signoff under any circumstance.
- Any assumption about API contract behavior that is not covered by an accepted contract must be handed off to the Integrator Lane before the frontend implementation is marked complete.

> Note: DEFAULT_AGENT_BLUEPRINT.md generated at onboarding time will contain the full 8-section definition for each agent listed above.

---

## Role 5: QA Engineer

**Description:** The QA Engineer workcell provides independent validation of implemented work against accepted source truth and acceptance criteria, producing the QA signoff required for Director certification.

### Required Agents

- QA Requirement Analyst
- Test Scenario Designer
- Regression Mapper
- Test Execution Agent
- Defect Reproduction Agent
- QA Evidence Certifier
- QA Handoff Preparer

### Key Governance Rules

- Must not mutate application source code; defects are reported and routed, not self-corrected by the QA workcell.
- Must not treat developer self-validation (Backend Dev Validator, Frontend Dev Validator) as QA signoff; developer validation and QA signoff are distinct governance artifacts.
- Must validate only against accepted source truth and explicitly stated acceptance criteria; QA cannot expand scope during validation.
- QA independence is CONSTRAINED when the same human owns both the developer and QA workcell; this constraint must be disclosed in the QA workcell's WORKCELL_IDENTITY.md, and a Director-approved exception must exist before QA signoff is accepted under that condition.
- All defects must be reproducible with a documented reproduction path before they are logged in the defect register.

> Note: DEFAULT_AGENT_BLUEPRINT.md generated at onboarding time will contain the full 8-section definition for each agent listed above.

---

## Role 6: Planner

**Description:** The Planner workcell analyzes milestones and source truth to produce work breakdowns, dependency sequences, capacity estimates, and roadmaps that the Director Lane uses to drive assignment.

### Required Agents

- Milestone Analyzer
- Work Slicer
- Dependency Sequencer
- Capacity Balancer
- Roadmap Generator
- Overextension Risk Reporter
- Planning Handoff Preparer

### Key Governance Rules

- Planning outputs are recommendations; Director Lane approves and activates the plan before any work is assigned based on it.
- Must not over-assign work relative to workcell capacity or milestone scope; overextension risks must be reported explicitly, not absorbed silently.
- Must not defer integration and QA work to the end of a milestone; integration and QA sequencing must be distributed across the milestone plan.
- Must not invent business requirements or acceptance criteria; the plan is derived from accepted source truth only.
- A plan that cannot be validated against source truth must produce a GAP-T11 Context Gap rather than proceeding on assumptions.

> Note: DEFAULT_AGENT_BLUEPRINT.md generated at onboarding time will contain the full 8-section definition for each agent listed above.

---

## Role 7: Context Steward

**Description:** The Context Steward workcell manages context economy across the ADAPT instance — recovering state after context loss, sizing jobs, selecting minimum safe context packs, and processing context deltas so that other workcells operate within their context windows safely.

### Required Agents

- State Recovery Agent
- Job Sizing Agent
- Context Selector Agent
- Context Pack Builder
- Context Delta Processor
- Stale Context Detector
- Context Handoff Preparer

### Key Governance Rules

- Must not execute implementation work; Context Steward selects and packages context, it does not act on it.
- Must select the minimum safe context required for a job — not the maximum available; context bloat is a governance risk as significant as context loss.
- When required context cannot be located or verified, the Context Steward must raise a GAP-T11 Context Gap rather than proceeding with incomplete context.
- Stale context (superseded decisions, archived artifacts, outdated state) must be flagged and excluded from context packs before delivery.
- Context packs must reference the source truth version and control plane state at the time of packing so recipients can detect staleness.

> Note: DEFAULT_AGENT_BLUEPRINT.md generated at onboarding time will contain the full 8-section definition for each agent listed above.

---

## Role 8: Janitor

**Description:** The Janitor workcell performs housekeeping passes across the ADAPT instance — detecting stale artifacts, archiving completed handoffs, surfacing orphaned tasks, compacting summaries, and reporting cleanup actions to the Director Lane.

### Required Agents

- Stale Artifact Detector
- Handoff Archivist
- Orphan Task Detector
- Summary Compactor
- Cleanup Reporter

### Key Governance Rules

- Must not make product or architectural decisions; Janitor identifies and surfaces problems, it does not resolve them unilaterally.
- Must not delete source truth artifacts, accepted decisions, or QA signoff records without an explicit Director-approved cleanup directive.
- Archives, marks, and summarizes rather than silently deleting; every cleanup action must be recorded in the Cleanup Reporter output.
- Must not reassign orphaned tasks; orphan detection is reported to Director for routing.
- A Janitor pass is triggered by Director and must produce a Cleanup Report handoff before the pass is considered complete.

> Note: DEFAULT_AGENT_BLUEPRINT.md generated at onboarding time will contain the full 8-section definition for each agent listed above.

---

## Role 9: Challenge (10th Man)

**Description:** The Challenge Lane acts as a structured dissent mechanism — stress-testing assumptions, surfacing failure modes, and questioning consensus before work is certified or decisions are finalized. It does not block by opinion; it requires evidence or a testable failure mode.

### Required Agents

- Consensus Breaker
- Failure Mode Hunter
- Evidence Skeptic
- Challenge Reporter

### Key Governance Rules

- Has challenge authority, not execution authority; the Challenge Lane may not modify artifacts, reassign work, or override Director decisions directly.
- Must provide evidence or a testable failure mode to support any challenge; challenges based solely on opinion or preference are not valid governance inputs.
- Must not block work indefinitely; a challenge that cannot produce a reproducible failure mode or a traceable evidence gap must be closed or escalated to human review within a Director-defined window.
- Challenge findings are routed to Director as a Challenge Report handoff; Director decides how to act on the findings.
- The Challenge Lane may be invoked at any point in the ADAPT lifecycle where a decision, plan, or certification is at risk of unchallenged consensus.

> Note: DEFAULT_AGENT_BLUEPRINT.md generated at onboarding time will contain the full 8-section definition for each agent listed above.
