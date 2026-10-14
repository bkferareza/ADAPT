# CONTRACT_GUARDRAIL

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
GUARDRAIL_ID: {{GUARDRAIL_ID_CONTRACT}}

## Enforcement Rule

All implementation must comply with accepted integration contracts; no lane may deviate from an accepted contract without triggering reconciliation.

## Trigger Conditions

- An implementation action would change an endpoint path, request payload, response payload, error behavior, or data schema that is defined in an accepted contract in 04_INTEGRATION/API_CONTRACTS.md or 04_INTEGRATION/INTEGRATION_CONTRACTS.md
- A new contract dependency is discovered during implementation that has not been reviewed and accepted by the Integrator role
- An accepted contract is missing for a cross-lane dependency that the current implementation relies on (i.e., no contract covers the interface being consumed or produced)
- An implementation diverges from a contract definition even if the divergence appears locally benign (e.g., adding an optional field, changing a default)
- A contract is referenced in the implementation but its version in 04_INTEGRATION/API_CONTRACTS.md or 04_INTEGRATION/INTEGRATION_CONTRACTS.md has been superseded

## Outcome Types

### PASS

The implementation is consistent with all accepted contracts. Every interface being produced or consumed has a current, accepted contract. No new unreviewed contract dependencies are present. Proceed with implementation.

### WARN

A potential contract impact is detected — the implementation may affect a contracted interface, but the impact is ambiguous (e.g., an optional field addition, a behavioral change that may or may not be within contract tolerance). The AI agent must stop the specific action, document the potential impact, and validate with the Integrator before proceeding. Do not implement the change without Integrator confirmation.

### STOP_REQUIRED

A direct contract violation is detected — the implementation would change a contracted interface without a reconciled and accepted updated contract. Stop immediately. Do not merge, accept, or apply the change. Route to the Integrator for contract reconciliation. Record the violation as a blocker.

## AI Behavior When Fired

| Outcome | AI Must | Record In | Route To |
|---------|---------|-----------|----------|
| PASS | Proceed with implementation | — | — |
| WARN | Pause the specific action; document potential contract impact; await Integrator validation | Active work log; handoff artifact in 06_HANDOFFS/ACTIVE/ | Integrator role |
| STOP_REQUIRED | STOP. Do not implement, merge, or accept the change. Record blocker. | 02_DIRECTOR_LANE/BLOCKER_REGISTER.md; 06_HANDOFFS/ACTIVE/ | Integrator role; Director lane |

## Override Requirements

- Only the Integrator role can approve a contract deviation.
- Approval requires formal reconciliation: the deviation must be reviewed, its impact assessed across all consuming lanes, and a new contract version produced.
- The new contract version must be recorded in 04_INTEGRATION/API_CONTRACTS.md or 04_INTEGRATION/INTEGRATION_CONTRACTS.md with a version increment and acceptance notation.
- The Director must be notified of the contract version change via a handoff or decision log entry.
- No implementation lane may self-authorize a contract deviation under any circumstance.

## References

- `04_INTEGRATION/API_CONTRACTS.md` — accepted API contracts; primary reference for endpoint and payload compliance
- `04_INTEGRATION/INTEGRATION_CONTRACTS.md` — accepted integration contracts; reference for cross-lane behavioral agreements
- `04_INTEGRATION/UI_BE_CONTRACTS.md` — UI-to-backend interface contracts where applicable
- `02_DIRECTOR_LANE/BLOCKER_REGISTER.md` — where contract violation blockers are recorded
- `06_HANDOFFS/ACTIVE/` — where blocked or warning handoffs are emitted
- `00_FRAMEWORK/GOVERNANCE_RULES.md` — framework-level contract compliance rules
