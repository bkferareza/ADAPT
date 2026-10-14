# Lane Assignment Matrix

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
MILESTONE: {{ACTIVE_MILESTONE}}

## Purpose

Maps active business items and requirements to the workcells and lanes responsible for them. Director maintains this matrix to track assignment coverage and detect gaps.

## Assignment Matrix

| BI-ID | Title | Assigned To Workcell | Lane | Assignment Date | Handoff ID | Status | Notes |
|-------|-------|---------------------|------|-----------------|------------|--------|-------|
<!-- EXAMPLE: | BI-001 | User Login | BACKEND_ANA, FRONTEND_CARLOS | Backend + Frontend | {{DATE}} | HANDOFF-001 | IN_PROGRESS | API contract pending Integrator review | -->

## Status Values

- UNASSIGNED: Not yet assigned to a workcell
- ASSIGNED: Assigned; handoff emitted
- IN_PROGRESS: Workcell has accepted and started work
- BLOCKED: Cannot proceed; see BLOCKER_REGISTER.md
- COMPLETE: Work accepted by Director
- DEFERRED: Not scheduled for current milestone
