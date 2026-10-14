# QA_INDEPENDENCE_GUARDRAIL

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
GUARDRAIL_ID: {{GUARDRAIL_ID_QA_INDEPENDENCE}}

## Enforcement Rule

QA signoff must be produced independently of development; the same human or AI that developed a feature cannot produce QA signoff for that feature without a Director-granted CONSTRAINED exception.

## Trigger Conditions

- QA signoff is about to be recorded for a business item where the QA workcell owner is the same human as the developer workcell owner, and no Director-granted CONSTRAINED exception exists in DECISION_LOG.md
- Developer-produced evidence (test runs, build logs, self-verification notes) is being presented directly as QA evidence without independent QA re-execution
- QA signoff is being issued without an independent test execution record — i.e., no artifact exists that demonstrates a test run was performed by the QA lane separately from the developer lane's own verification
- The QA_INDEPENDENCE_STATUS field in 05_VALIDATION/QA_STRATEGY.md is CONSTRAINED but no corresponding Director exception entry exists in 02_DIRECTOR_LANE/DECISION_LOG.md
- A QA signoff artifact references only artifacts that were produced during development (not during an independent QA execution pass)

## Outcome Types

### PASS

QA independence is confirmed. The QA signoff is being produced by a different human and/or AI lane from the developer. Independent test execution records exist and are referenced in the signoff. The signoff is valid. Proceed.

### WARN

QA independence is CONSTRAINED — the same human operates both the developer and QA workcells, but a Director-granted CONSTRAINED exception exists and is recorded in 02_DIRECTOR_LANE/DECISION_LOG.md and noted in 05_VALIDATION/QA_STRATEGY.md. The signoff is valid but limited. The AI agent must reference the exception in the signoff artifact and document the CONSTRAINED status explicitly. Proceed with documented limitation.

### STOP_REQUIRED

QA signoff would be produced without independence and without a Director-granted CONSTRAINED exception. The independence requirement is not met and has not been formally waived. Stop immediately. Do not record the signoff. Route to the Director for exception evaluation. The business item cannot be accepted as QA-certified until independence is established or a formal exception is granted.

## AI Behavior When Fired

| Outcome | AI Must | Record In | Route To |
|---------|---------|-----------|----------|
| PASS | Proceed with QA signoff | — | — |
| WARN | Proceed; reference CONSTRAINED exception in signoff; note limited status | QA signoff artifact; 06_HANDOFFS/ACTIVE/ (informational) | Director (informational) |
| STOP_REQUIRED | STOP. Do not record QA signoff. Emit blocked handoff. | 02_DIRECTOR_LANE/BLOCKER_REGISTER.md; 06_HANDOFFS/ACTIVE/ | Director lane |

## Override Requirements

- Only the Director may grant a CONSTRAINED exception to the QA independence requirement.
- The exception must be recorded in 02_DIRECTOR_LANE/DECISION_LOG.md, citing: the specific workcell configuration, the reason independence cannot be achieved (e.g., single-person team), the risk acceptance rationale, and the scope of the exception (which business items or work categories it covers).
- The exception must be reflected in the QA_INDEPENDENCE_STATUS field of 05_VALIDATION/QA_STRATEGY.md, set to CONSTRAINED with a reference to the DECISION_LOG.md entry.
- Every QA signoff produced under a CONSTRAINED exception must explicitly note the CONSTRAINED status and the DECISION_LOG.md reference in the signoff artifact.
- The CONSTRAINED exception does not permit self-certification without any independent verification step — at minimum, a structured self-review against acceptance criteria using a separate QA checklist is required, and the checklist must be evidenced.

## References

- `05_VALIDATION/QA_STRATEGY.md` — defines the QA Independence Model; contains the QA_INDEPENDENCE_STATUS field
- `02_DIRECTOR_LANE/DECISION_LOG.md` — where Director-granted CONSTRAINED exceptions are recorded
- `02_DIRECTOR_LANE/BLOCKER_REGISTER.md` — where QA independence blockers are recorded
- `15_COMMANDS_AND_DRIVERS/EVIDENCE_STANDARD_BY_ROLE.md` — defines what constitutes valid QA evidence
- `06_HANDOFFS/ACTIVE/` — where blocked handoffs are emitted
- `01_SOURCE_TRUTH/ACCEPTANCE_CRITERIA.md` — acceptance criteria that QA signoff must demonstrate coverage of
