# Blocker Register

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

Records execution blockers — conditions that prevent a bounded action from proceeding. Blockers must be escalated and resolved; workarounds that bypass governance are not permitted.

## Blockers

| BLK-ID | Severity | Title | Description | Blocked Item | Raised By | Raised Date | Assigned To | Status | Resolution | Resolved Date |
|--------|----------|-------|-------------|--------------|-----------|-------------|-------------|--------|------------|---------------|
<!-- EXAMPLE: | BLK-001 | HIGH | Missing API Contract | Backend cannot implement the payment endpoint until the API contract is accepted by Integrator | BI-005 Payment Flow | BACKEND_ANA | {{DATE}} | Integrator Lane | OPEN | — | — | -->

## Severity Values

- CRITICAL: Human approval required to resolve (Gate 7); all dependent work halted
- HIGH: Director must review before work resumes; workcell halts
- MEDIUM: Workcell may attempt resolution within scope; Director notified
- LOW: Workcell may attempt resolution within scope; Director notified

## Status Values

- OPEN: Blocker active; blocked item cannot proceed
- RESOLVED: Blocker lifted; blocked item may proceed
- DEFERRED: Blocked item deferred to a later milestone; blocker closed for now

Escalation is an action — an escalation handoff to the resolution authority — not a status. A blocker stays OPEN until it is RESOLVED or DEFERRED.

## Notes

Blockers differ from gaps: a gap is a missing decision or context; a blocker is an active execution obstacle. The same root cause may produce both. BLK-IDs follow format BLK-NNN.
