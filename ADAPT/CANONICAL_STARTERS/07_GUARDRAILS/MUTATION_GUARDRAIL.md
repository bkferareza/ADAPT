# MUTATION_GUARDRAIL

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
GUARDRAIL_ID: {{GUARDRAIL_ID_MUTATION}}

## Enforcement Rule

No AI agent may mutate files outside its explicit mutation authority as defined in its workcell scope and the MUTATION_PERMISSION_MATRIX.

## Trigger Conditions

- An action would write, modify, or delete files not covered by the file paths declared in the workcell's SCOPE_CONTRACT.md or explicitly granted in the MUTATION_PERMISSION_MATRIX
- A Director-role agent attempts to write, modify, or delete application source code files
- A QA-role agent attempts to write, modify, or delete application source code files (test artifacts are permitted; source code is not)
- Any agent attempts to modify another lane's core governance artifacts — including 02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md, 02_DIRECTOR_LANE/DECISION_LOG.md, or any lane's SCOPE_CONTRACT.md — without explicit Director authority
- An agent attempts to delete or overwrite an artifact that is referenced as evidence in 02_DIRECTOR_LANE/ACCEPTED_WORK_REGISTER.md
- A mutation would affect a file that is currently locked or in use by another active workcell

## Outcome Types

### PASS

The planned mutation targets only files within the workcell's declared mutation authority per SCOPE_CONTRACT.md and MUTATION_PERMISSION_MATRIX. The mutation is valid. Proceed.

### WARN

The planned mutation targets a file in a boundary area — for example, a shared utility file, a configuration file referenced across multiple workcells, or a file adjacent to but not explicitly in the workcell's scope. The AI agent must confirm its scope interpretation before proceeding. Document the reasoning in the active work log and flag in the next handoff.

### STOP_REQUIRED

The planned mutation targets a file outside the workcell's mutation authority, targets a governance artifact without Director authorization, or falls into any other category of unauthorized mutation. Stop immediately. Do not perform the mutation. Record a blocker. Route to the Director for mutation authority expansion or explicit authorization.

## AI Behavior When Fired

| Outcome | AI Must | Record In | Route To |
|---------|---------|-----------|----------|
| PASS | Proceed with the mutation | — | — |
| WARN | Pause; confirm scope interpretation; document reasoning before proceeding | Active work log; handoff artifact in 06_HANDOFFS/ACTIVE/ | Director (informational) |
| STOP_REQUIRED | STOP. Do not perform the mutation. Record blocker. Emit blocked handoff. | 02_DIRECTOR_LANE/BLOCKER_REGISTER.md; 06_HANDOFFS/ACTIVE/ | Director lane |

## Override Requirements

- Only the Director role may authorize a mutation authority expansion.
- Expansion requires an updated SCOPE_CONTRACT.md at 03_WORKCELLS/{{WORKCELL_ID}}/SCOPE_CONTRACT.md that explicitly lists the newly authorized file paths or file categories.
- The updated SCOPE_CONTRACT.md must carry a new version entry.
- A Director-issued handoff must accompany the expansion and explicitly reference the updated SCOPE_CONTRACT.md.
- The workcell must not perform the mutation until the updated SCOPE_CONTRACT.md is in place.
- Governance artifact mutations (DECISION_LOG.md, PROJECT_CONTROL_PLANE.md, SCOPE_CONTRACT.md) may only be performed by the Director role or an agent explicitly delegated by the Director in a DECISION_LOG.md entry.

## References

- `15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md` — authoritative matrix of which roles and workcells may mutate which file categories
- `03_WORKCELLS/{{WORKCELL_ID}}/SCOPE_CONTRACT.md` — workcell-level mutation authority declaration
- `02_DIRECTOR_LANE/BLOCKER_REGISTER.md` — where unauthorized mutation blockers are recorded
- `02_DIRECTOR_LANE/DECISION_LOG.md` — where Director mutation delegations are recorded
- `06_HANDOFFS/ACTIVE/` — where blocked handoffs are emitted
- `00_FRAMEWORK/GOVERNANCE_RULES.md` — framework-level mutation rules
