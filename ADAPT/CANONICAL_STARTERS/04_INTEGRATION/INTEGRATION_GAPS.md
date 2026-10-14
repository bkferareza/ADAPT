# Integration Gaps

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
MILESTONE: {{ACTIVE_MILESTONE}}

## Purpose

Records gaps specific to cross-lane integration: unresolved contract conflicts, missing API definitions, unowned cross-lane work, and pipeline-level unknowns.

## Integration Gaps

| IG-ID | Title | Description | Lanes Affected | Root Cause | Routed To | Status | Resolution | Notes |
|-------|-------|-------------|----------------|------------|-----------|--------|------------|-------|
<!-- EXAMPLE: | IG-001 | Payment callback endpoint not defined | No contract exists for the payment provider webhook callback. Frontend cannot implement error recovery flow. | Backend + Frontend | Missing API contract | Backend Workcell | OPEN | — | Blocks BI-005 | -->

## Status Values

- OPEN / IN_REVIEW / RESOLVED / DEFERRED

## Notes

Integration gaps are a subset of the main GAP_REGISTER.md. They are tracked here for Integrator visibility and cross-referenced in the main register. Integrator raises them; Director classifies and routes.
