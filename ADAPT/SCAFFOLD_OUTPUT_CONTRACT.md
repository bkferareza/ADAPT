# SCAFFOLD OUTPUT CONTRACT

## Purpose

This file defines the complete folder and starter-file contract for a generated external ADAPT instance.

Project-specific ADAPT state must be written under {{ADAPT_INSTANCE_PATH}}, not into ADAPT_FRAMEWORK and not into PROJECT_FOLDER by default.

## Required Instance Structure

The generated instance must include:

```text
{{ADAPT_INSTANCE_PATH}}/ADAPT/00_FRAMEWORK/
{{ADAPT_INSTANCE_PATH}}/ADAPT/01_SOURCE_TRUTH/
{{ADAPT_INSTANCE_PATH}}/ADAPT/02_DIRECTOR_LANE/
{{ADAPT_INSTANCE_PATH}}/ADAPT/03_WORKCELLS/
{{ADAPT_INSTANCE_PATH}}/ADAPT/04_INTEGRATION/
{{ADAPT_INSTANCE_PATH}}/ADAPT/05_VALIDATION/
{{ADAPT_INSTANCE_PATH}}/ADAPT/06_HANDOFFS/
{{ADAPT_INSTANCE_PATH}}/ADAPT/07_GUARDRAILS/
{{ADAPT_INSTANCE_PATH}}/ADAPT/08_TEMPLATES/
{{ADAPT_INSTANCE_PATH}}/ADAPT/09_CHALLENGE_LANE/
{{ADAPT_INSTANCE_PATH}}/ADAPT/10_CONTEXT_ECONOMY/
{{ADAPT_INSTANCE_PATH}}/ADAPT/11_ONBOARDING/
{{ADAPT_INSTANCE_PATH}}/ADAPT/12_JANITOR/
{{ADAPT_INSTANCE_PATH}}/ADAPT/13_PLANNING/
{{ADAPT_INSTANCE_PATH}}/ADAPT/14_MEMORY_BANK/
{{ADAPT_INSTANCE_PATH}}/ADAPT/15_COMMANDS_AND_DRIVERS/
```

## Required Starter Files

### 00_FRAMEWORK

* ADAPT_FRAMEWORK.md
* GOVERNANCE_RULES.md
* ROLE_MODEL.md
* ARTIFACT_STANDARDS.md
* GLOSSARY.md
* SOURCE_AUTHORITY_POLICY.md

### 01_SOURCE_TRUTH

* REQUIREMENTS_INDEX.md
* BUSINESS_ITEMS.md
* REQUIREMENT_SECTION_MAP.md
* ACCEPTANCE_CRITERIA.md
* OPEN_QUESTIONS.md
* SOURCE_TRUTH_VERSION_LOG.md

### 02_DIRECTOR_LANE

* DIRECTOR_IDENTITY.md
* PROJECT_CONTROL_PLANE.md
* INTAKE_REGISTER.md
* WORKCELL_REGISTRY.md
* LANE_ASSIGNMENT_MATRIX.md
* DEPENDENCY_MAP.md
* GAP_REGISTER.md
* BLOCKER_REGISTER.md
* DECISION_LOG.md
* ACCEPTED_WORK_REGISTER.md
* CARRY_OVER_REGISTER.md

### 03_WORKCELLS

If no onboarding command exists, create:

* README.md
* ROLE_WORKCELL_BLUEPRINTS.md

README.md must say:

```text
No real person-owned workcells have been onboarded yet.
Use: Onboard {{IDENTITY}} as {{ROLE}}.
```

Do not create a real person-owned workcell unless a valid onboarding command was provided.

Whenever onboarding creates a real workcell, its `DEFAULT_AGENT_BLUEPRINT.md` must satisfy the detailed blueprint contract below.

### 04_INTEGRATION

* INTEGRATION_CONTRACTS.md
* API_CONTRACTS.md
* UI_BE_CONTRACTS.md
* PIPELINE_STATUS.md
* MERGE_READINESS.md
* RELEASE_READINESS.md
* INTEGRATION_GAPS.md

### 05_VALIDATION

* QA_STRATEGY.md
* TEST_CASE_INDEX.md
* DEFECT_REGISTER.md
* VALIDATION_EVIDENCE.md
* REGRESSION_RISK_MAP.md
* SIGNOFF_REGISTER.md

### 06_HANDOFFS

* README.md
* ACTIVE/README.md
* CONSUMED/README.md
* ARCHIVE/README.md

### 07_GUARDRAILS

* SCOPE_GUARDRAIL.md
* CONTEXT_GUARDRAIL.md
* EVIDENCE_GUARDRAIL.md
* CONTRACT_GUARDRAIL.md
* MUTATION_GUARDRAIL.md
* QA_INDEPENDENCE_GUARDRAIL.md
* HANDOFF_GUARDRAIL.md

### 08_TEMPLATES

Include all required ADAPT templates, including:

* ACTION_PROMPT_ROLE_IDENTITY_TEMPLATE.md
* DEFAULT_AGENT_BLUEPRINT_TEMPLATE.md
* WORKFLOW_CUSTOMIZATION_TEMPLATE.md
* EFFECTIVE_WORKFLOW_TEMPLATE.md
* GUARDRAIL_BINDINGS_TEMPLATE.md
* WORKFLOW_CHANGE_REQUEST_TEMPLATE.md
* WORKFLOW_CHANGE_LOG_TEMPLATE.md
* WORKCELL_IDENTITY_TEMPLATE.md
* SCOPE_CONTRACT_TEMPLATE.md
* HANDOFF_TEMPLATE.md
* EVIDENCE_REPORT_TEMPLATE.md
* GAP_TEMPLATE.md
* BLOCKER_TEMPLATE.md
* CONTEXT_PACK_TEMPLATE.md
* CONTEXT_DELTA_TEMPLATE.md
* VALIDATION_REPORT_TEMPLATE.md

Templates must use double-brace placeholders and must not contain archived or test identities.

`DEFAULT_AGENT_BLUEPRINT_TEMPLATE.md` must encode the detailed per-agent structure and validity rules below. Any generated role-specific blueprint used to instantiate a workcell must meet the same depth requirement.

## Detailed Default Agent Blueprint Contract

Every generated `DEFAULT_AGENT_BLUEPRINT.md` must define every default agent required for its role by `WORKCELL_ONBOARDING_CONTRACT.md`.

A generated `DEFAULT_AGENT_BLUEPRINT.md` is invalid if it only lists agent names. The scaffold must produce full per-agent definitions.

Each agent definition must use this exact structure:

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

For every required agent:

* `Purpose` must state the agent's role-specific responsibility.
* `Inputs` must identify the accepted artifacts, context, contracts, evidence, or files needed by that agent.
* `Actions` must identify the analysis, decisions, checks, implementation, routing, or reporting performed by that agent.
* `Outputs` must identify concrete artifacts, updates, reports, decisions, or handoffs.
* `Boundaries` must include the authority and mutation limits that apply to the agent and role.
* `Stop Conditions` must identify missing source truth, context, authority, evidence, ownership, dependencies, or safe execution conditions that require a gap or blocker.
* `Evidence Produced` must identify concrete, reviewable evidence contributed by that agent.
* `Next Handoff` must identify the usual receiving agent, workcell, or governance lane and the information passed.

The generated text must be specific to both the role and the named agent. Do not use generic filler such as:

* `Perform role task.`
* `Read required files.`
* `Produce output.`
* `Follow rules.`

The generated blueprint must incorporate all role-specific agents, focus areas, boundaries, independence rules, routing requirements, and handoff requirements from `WORKCELL_ONBOARDING_CONTRACT.md`.

Before scaffold or onboarding completion, validate that every required agent has all eight populated sections and that the content is role-specific. If the AI cannot generate full role agent definitions, it must stop and report:

`ROLE_AGENT_BLUEPRINT_DEPTH_FAILURE`

### 09_CHALLENGE_LANE

* CHALLENGE_IDENTITY.md
* CHALLENGE_REGISTER.md
* CHALLENGE_REPORT_TEMPLATE.md

### 10_CONTEXT_ECONOMY

* CONTEXT_RULES.md
* CONTEXT_BUDGETS.md
* CONTEXT_INDEX.md
* STALE_CONTEXT_REGISTER.md
* CONTEXT_PACKS/
* CONTEXT_DELTAS/
* CONTEXT_SUMMARIES/

### 11_ONBOARDING

* ONBOARDING_RULES.md
* ROLE_TO_WORKCELL_MAP.md
* ONBOARDING_REQUESTS.md
* ONBOARDING_REPORTS.md

Onboarding behavior and generated workcell files must conform to WORKCELL_ONBOARDING_CONTRACT.md.

### 12_JANITOR

* JANITOR_RULES.md
* STALE_ARTIFACT_REGISTER.md
* ARCHIVE_CANDIDATES.md
* CLEANUP_REPORTS.md
* COMPACTION_SUMMARIES.md

### 13_PLANNING

* PLANNING_RULES.md
* MILESTONE_REGISTER.md
* CAPACITY_MODEL.md
* MILESTONE_PLANS.md
* WORKCELL_ROADMAPS.md
* OVEREXTENSION_RISK_REPORTS.md
* DEPENDENCY_SEQUENCES.md

### 14_MEMORY_BANK

* REFERENCES_INDEX.md
* NOTES.md

Memory Bank content is reference-only and is not live source authority.

### 15_COMMANDS_AND_DRIVERS

* COMMAND_REGISTRY.md
* COMMAND_SYNTAX.md
* COMMAND_ROUTING_MATRIX.md
* CONTROL_PLANE_SCHEMA.md
* ACTION_PROMPT_MASTER.md
* ACTION_PROMPT_DIRECTOR.md
* ACTION_PROMPT_CONTEXT_STEWARD.md
* ACTION_PROMPT_ONBOARDING.md
* ACTION_PROMPT_PLANNING.md
* ACTION_PROMPT_WORKCELL.md
* ACTION_PROMPT_INTEGRATOR.md
* ACTION_PROMPT_QA.md
* ACTION_PROMPT_JANITOR.md
* ACTION_PROMPT_CHALLENGE.md
* MUTATION_PERMISSION_MATRIX.md
* HUMAN_APPROVAL_GATES.md
* STOP_RULES.md
* CONTEXT_BUDGET_POLICY.md
* EVIDENCE_STANDARD_BY_ROLE.md
* MINIMAL_VIABLE_ADAPT_MODE.md

## Population Rules

* Populate project facts only from the project document or other explicitly accepted source truth.
* Record missing facts in OPEN_QUESTIONS.md and GAP_REGISTER.md.
* Do not invent identities, requirements, stack choices, approvals, or implementation state.
* Do not create application source code as an ADAPT starter artifact.
* Do not copy historical generated state into a new instance as current project truth.
* Ensure generated onboarding artifacts follow WORKCELL_ONBOARDING_CONTRACT.md.
