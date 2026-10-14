# Regression Risk Map

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
MILESTONE: {{ACTIVE_MILESTONE}}

## Purpose

Maps areas of the system that may be affected by current milestone changes and identifies regression risks. Used by QA to prioritize regression coverage.

## Regression Risk Entries

| RR-ID | Changed Area | Affected Existing Behavior | Risk Level | Regression Test Coverage | Status | Notes |
|-------|-------------|---------------------------|------------|-------------------------|--------|-------|
<!-- EXAMPLE: | RR-001 | Auth middleware refactor | All protected routes require re-validation | HIGH | TC-010 through TC-020 | AT_RISK | Any route regression will be caught by TC-010 suite | -->

## Risk Levels

- HIGH: Change is in a core shared component; regression likely affects multiple features
- MEDIUM: Change is in a semi-shared component; moderate regression risk
- LOW: Change is isolated; regression risk is minimal

## Coverage Status Values

- COVERED: Regression test cases exist and are PASSED
- AT_RISK: Regression test cases exist but have not been run against this change
- UNCOVERED: No regression test cases exist for this area
- WAIVED: Director has accepted the regression risk; reason in Notes
