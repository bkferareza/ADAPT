# Pipeline Status

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
LAST_UPDATED: {{DATE}}
UPDATED_BY: {{WORKCELL_ID}}

## Purpose

Tracks the current state of the integration pipeline — build, test, lint, and deployment stages.

## Pipeline Stages

| Stage | Status | Last Run | Result | Artifacts | Notes |
|-------|--------|----------|--------|-----------|-------|
<!-- EXAMPLE: | Build | PASSING | {{DATE}} | SUCCESS | build/app.zip | All units compile | -->
<!-- EXAMPLE: | Unit Tests | NOT_RUN | — | — | — | No tests written yet | -->
<!-- EXAMPLE: | Integration Tests | NOT_RUN | — | — | — | Awaiting API contracts | -->
<!-- EXAMPLE: | Lint/Static Analysis | NOT_RUN | — | — | — | — | -->
<!-- EXAMPLE: | Deployment — Staging | NOT_RUN | — | — | — | — | -->

## Stage Status Values

- PASSING: Last run succeeded
- FAILING: Last run failed; see Notes
- NOT_RUN: Not yet executed in this instance
- BLOCKED: Cannot run; see Notes for blocker
- SKIPPED: Intentionally skipped; reason in Notes

## Notes

Pipeline status is updated by the Integrator or the workcell that ran the stage. A FAILING or BLOCKED stage blocks merge readiness.
