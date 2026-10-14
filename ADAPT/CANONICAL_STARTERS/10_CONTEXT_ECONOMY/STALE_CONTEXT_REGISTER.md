# Stale Context Register

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

This register records context items detected as stale within this ADAPT instance. Stale context must not be used in ADAPT actions. Detection may be performed by the Context Steward, the Janitor Lane, or any workcell that identifies outdated context during an action.

## Status Values

- OPEN — stale item detected; context pack has not yet been rebuilt or resolved
- RESOLVED — context pack has been rebuilt using current source truth; stale item is retired
- ACCEPTED_RISK — Director has acknowledged the stale item and accepted the risk of proceeding; must be documented with Director confirmation

## Register

| SC-ID | Context Pack ID | Stale Item | Why Stale | Detected By | Date Detected | Impact | Status | Notes |
|-------|----------------|------------|-----------|-------------|---------------|--------|--------|-------|
<!-- EXAMPLE: | SC-001 | CP-003 | REQUIREMENTS_INDEX.md v1.1 | Source truth promoted to STV-004 after pack assembly | CONTEXT_STEWARD | {{DATE}} | M — affects scope of BI-009 action | RESOLVED | Context pack rebuilt as CP-007 referencing STV-004 | -->
