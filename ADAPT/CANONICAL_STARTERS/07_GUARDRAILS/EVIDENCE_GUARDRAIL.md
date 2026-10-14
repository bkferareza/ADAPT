# EVIDENCE_GUARDRAIL

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
GUARDRAIL_ID: {{GUARDRAIL_ID_EVIDENCE}}

## Enforcement Rule

All claimed completions, acceptances, and certifications must be backed by concrete, reviewable evidence traceable to source truth.

## Trigger Conditions

- Work is claimed complete (business item closed, handoff emitted as DONE) without at least one evidence artifact attached or referenced
- Evidence artifacts are not traceable to a specific acceptance criterion or requirement in 01_SOURCE_TRUTH/ACCEPTANCE_CRITERIA.md or 01_SOURCE_TRUTH/BUSINESS_ITEMS.md
- Evidence for a QA signoff was produced by the same lane that developed the feature, and no Director-granted independence exception exists
- Evidence references a superseded source truth version, making its acceptance criteria linkage invalid
- Acceptance or certification is recorded in 02_DIRECTOR_LANE/ACCEPTED_WORK_REGISTER.md without a corresponding evidence reference
- An evidence artifact is described but not linked (e.g., "tests pass" stated without a test run record or artifact path)

## Outcome Types

### PASS

Evidence is present, traceable to a current acceptance criterion or requirement, produced by the appropriate lane, and references a current source truth version. The claim of completion or certification is valid. Proceed.

### WARN

Evidence is present but may be incomplete — for example, some acceptance criteria are covered but others are not explicitly evidenced. The AI agent must document the specific limitation, record what criteria remain unevidenced, and include this in the handoff artifact. Proceed with documented limitation; do not close the business item as fully accepted until the limitation is resolved.

### STOP_REQUIRED

Evidence is missing entirely, untraceable to an acceptance criterion, produced by a disqualified party (same-lane self-certification without a Director exception), or references a superseded source truth version. Stop immediately. Do not record the completion, acceptance, or certification. Record a gap or blocker in the appropriate register. Route to the Director for resolution.

## AI Behavior When Fired

| Outcome | AI Must | Record In | Route To |
|---------|---------|-----------|----------|
| PASS | Proceed with completion or certification | — | — |
| WARN | Proceed; document unevidenced criteria; do not fully close the item | Active work log; handoff artifact in 06_HANDOFFS/ACTIVE/ | Director (informational) |
| STOP_REQUIRED | STOP. Do not record completion or certification. Record gap or blocker. | 02_DIRECTOR_LANE/GAP_REGISTER.md or 02_DIRECTOR_LANE/BLOCKER_REGISTER.md; 06_HANDOFFS/ACTIVE/ | Director lane |

## Override Requirements

- The Director may accept reduced evidence with explicit documented risk acceptance.
- The risk acceptance decision must be recorded in 02_DIRECTOR_LANE/DECISION_LOG.md, referencing the specific business item, the specific evidence gap, and the rationale.
- The accepted work entry in 02_DIRECTOR_LANE/ACCEPTED_WORK_REGISTER.md must note that acceptance was made under reduced evidence with the DECISION_LOG.md reference.
- No other role may authorize an evidence override.

## References

- `15_COMMANDS_AND_DRIVERS/EVIDENCE_STANDARD_BY_ROLE.md` — defines what constitutes valid evidence per role and action type
- `01_SOURCE_TRUTH/ACCEPTANCE_CRITERIA.md` — acceptance criteria that evidence must be traced to
- `01_SOURCE_TRUTH/BUSINESS_ITEMS.md` — business items whose completion claims require evidence
- `02_DIRECTOR_LANE/ACCEPTED_WORK_REGISTER.md` — where accepted completions are recorded
- `02_DIRECTOR_LANE/DECISION_LOG.md` — where Director risk acceptances (reduced evidence overrides) are recorded
- `02_DIRECTOR_LANE/GAP_REGISTER.md` — where evidence gaps are recorded
- `02_DIRECTOR_LANE/BLOCKER_REGISTER.md` — where evidence blockers are recorded
- `06_HANDOFFS/ACTIVE/` — where blocked handoffs are emitted
