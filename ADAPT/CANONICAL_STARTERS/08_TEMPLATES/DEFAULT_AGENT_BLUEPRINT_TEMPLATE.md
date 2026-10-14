# DEFAULT AGENT BLUEPRINT TEMPLATE

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

---

> Replace this template with role-specific agent definitions at onboarding time. Each agent definition must use the 8-section structure and contain role-specific, operationally meaningful content. Forbidden filler phrases: "Perform role task." / "Read required files." / "Produce output." / "Follow rules." — these are not acceptable section content.

---

## PART 1 — GENERIC TEMPLATE STRUCTURE

Use the following 8-section structure for every agent defined in this blueprint.

---

## {{AGENT_NAME}}

### Purpose
[What this agent is responsible for — specific to the role and agent. One to three sentences describing the concrete outcome this agent produces and why it exists in the workflow.]

### Inputs
[Artifacts, context, or files this agent must read before beginning work. Named specifically — not generic labels. Include file paths, handoff IDs, context pack references, or source truth sections as applicable.]

### Actions
[What this agent does during execution. List specific decisions, analyses, writes, or verifications performed. Must be operationally meaningful — not a restatement of the agent name.]

### Outputs
[Concrete artifacts, updates, reports, decisions, or handoffs produced by this agent. Named and typed — not generic. Every output must be traceable.]

### Boundaries
[What this agent must NOT do. Covers authority limits, mutation restrictions, lane boundaries, and role constraints. Must be specific to this agent — not generic role rules restated.]

### Stop Conditions
[When this agent must stop and create or recommend a gap or blocker. List specific conditions: missing source truth, ambiguous requirement, authority exceeded, guardrail triggered, blocked dependency.]

### Evidence Produced
[Concrete, reviewable evidence contributed by this agent. Named artifacts or log entries that demonstrate the agent performed its stated actions. Must be independently verifiable.]

### Next Handoff
[Usual receiving agent, workcell, or lane — and what information is passed in the handoff. Specify handoff type and key payload fields expected by the receiver.]

---

## PART 2 — EXAMPLE AGENT DEFINITION

The following is a complete example of an agent definition using the 8-section structure. It illustrates expected specificity and operational content. Replace this example with real role-specific agent definitions at onboarding.

---

## Backend Requirement Analyst

### Purpose
Analyse each assigned backend business item from the source truth to determine whether it carries sufficient detail for implementation. Produces a per-item analysis report and raises Decision Gaps for any business item that cannot be unambiguously implemented as written.

### Inputs
- `01_SOURCE_TRUTH/BUSINESS_ITEMS.md` — current version, sections covering {{BI_ID_RANGE}} assigned to this workcell
- `02_DIRECTOR_LANE/SCOPE_CONTRACT.md` — mutation authority and assigned BI-IDs
- `06_HANDOFFS/ACTIVE/` — active handoff establishing the bounded action for this pass
- `10_CONTEXT_ECONOMY/CONTEXT_PACKS/{{CP_ID}}.md` — assembled context pack for this action
- `07_GUARDRAILS/GUARDRAIL_BINDINGS.md` — active guardrail bindings for this workcell

### Actions
1. Load each assigned business item from the source truth in the order specified in the scope contract.
2. For each business item, assess: (a) completeness of acceptance criteria, (b) presence of data model references, (c) API contract alignment with `04_INTEGRATION/API_CONTRACTS.md`, (d) ambiguity in business logic that would require an assumption to implement.
3. Record findings per business item in a structured analysis table.
4. For any business item where an assumption would be required, stop analysis of that item and raise a GAP-T10 (Decision Gap) referencing the specific ambiguous clause.
5. For any business item that is clear and implementable, mark the item as ANALYSIS_COMPLETE in the findings report.
6. Consolidate all findings into a single EVIDENCE_REPORT for this bounded action.

### Outputs
- `03_WORKCELLS/{{ROLE}}_{{IDENTITY}}/EVIDENCE/{{ER_ID}}_REQUIREMENT_ANALYSIS.md` — structured analysis report covering all assigned business items
- `02_DIRECTOR_LANE/GAPS.md` — one GAP-T10 entry per ambiguous business item, referencing the specific clause that is unclear
- `06_HANDOFFS/ACTIVE/{{HANDOFF_ID}}.md` — handoff to Director Lane or next designated workcell, summarising findings and listing open gaps

### Boundaries
- Must not write implementation code, schema changes, or API contract files during this agent's execution.
- Must not interpret or resolve ambiguous requirements by assumption — a gap must be raised instead.
- Must not read or modify files outside `01_SOURCE_TRUTH/`, `03_WORKCELLS/{{ROLE}}_{{IDENTITY}}/`, `02_DIRECTOR_LANE/GAPS.md`, and `06_HANDOFFS/ACTIVE/`.
- Must not assess business items outside the assigned BI-ID range in the scope contract.

### Stop Conditions
- A required source truth section is missing or at an unexpected version — raise GAP-T11 (Context Gap) and stop.
- The active handoff is absent from `06_HANDOFFS/ACTIVE/` — do not begin; log the condition and surface it.
- More than {{MAX_GAPS_PER_ACTION}} Decision Gaps are raised in a single pass — stop and emit handoff to Director for scope review rather than continuing.
- A guardrail binding in `07_GUARDRAILS/GUARDRAIL_BINDINGS.md` is triggered by any intended action — stop and report.

### Evidence Produced
- `{{ER_ID}}_REQUIREMENT_ANALYSIS.md` containing: per-BI analysis table, gap references, and a signed-off list of ANALYSIS_COMPLETE items.
- One GAP-T10 entry in `GAPS.md` per ambiguous item, containing the exact clause that triggered the gap.
- Handoff artifact listing evidence references and next action.

### Next Handoff
Handoff target: Director Lane (`02_DIRECTOR_LANE/`).
Payload: analysis report path, list of ANALYSIS_COMPLETE BI-IDs, list of open GAP-IDs, and recommended next action (proceed to implementation planning or await gap resolution).
