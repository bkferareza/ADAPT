# WORKCELL IDENTITY

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
WORKCELL_ID: {{ROLE}}_{{IDENTITY}}

---

## Identity Card

| Field | Value |
|-------|-------|
| HumanOwner | {{IDENTITY}} |
| Role | {{ROLE}} |
| WorkcellType | {{WORKCELL_TYPE}} |
| Lane | {{LANE}} |
| OnboardedDate | {{ONBOARDED_DATE}} |
| ScopeContract | `02_DIRECTOR_LANE/SCOPE_CONTRACT_{{ROLE}}_{{IDENTITY}}.md` |
| Authority Summary | {{AUTHORITY_SUMMARY}} |
| MutationScope | {{MUTATION_SCOPE}} |
| QAIndependenceStatus | {{QA_INDEPENDENCE_STATUS}} |
| ActiveMilestone | {{ACTIVE_MILESTONE}} |
| CurrentStatus | {{CURRENT_STATUS}} |

**Authority Summary guidance:** State concisely what this workcell is authorised to decide and implement. Do not use vague terms — reference specific file types, directories, or decision domains.

**MutationScope guidance:** List the exact file paths or path patterns this workcell may write. All other paths are read-only.

**QAIndependenceStatus values:** `FULL` (no shared identity with any QA workcell) / `CONSTRAINED` (independence limitation documented in Director Lane).

**CurrentStatus values:** `ACTIVE` / `ON_HOLD` / `BLOCKED` / `COMPLETE` / `OFFBOARDED`

---

## Workcell History

| Date | Event | Notes |
|------|-------|-------|
| {{DATE}} | Onboarded | Initial scope: {{INITIAL_SCOPE_SUMMARY}} |
| {{DATE}} | {{EVENT}} | {{NOTES}} |
