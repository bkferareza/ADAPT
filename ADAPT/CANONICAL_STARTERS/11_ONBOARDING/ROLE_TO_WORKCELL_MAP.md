# Role to Workcell Map

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

This map records the relationship between defined roles and their onboarded workcells. It is updated each time an onboarding completes or a workcell is deactivated.

## Notes

- One human may own multiple workcells (e.g., one implementation workcell and one QA workcell).
- One execution may be under only one active workcell identity at a time. A human acting in two roles must use the correct workcell identity for each action.
- Folder Path is relative to the ADAPT root for this project.

## Status Values

- ACTIVE — workcell is onboarded and operating
- INACTIVE — workcell is suspended or the human owner is unavailable
- DECOMMISSIONED — workcell has been formally closed; work transferred or completed

## Map

| Role | Workcell ID | Human Owner | Folder Path | Status |
|------|-------------|-------------|-------------|--------|
<!-- EXAMPLE: | Implementation | IMPL_ALICE | Alice Reyes | ADAPT/03_WORKCELLS/IMPL_ALICE/ | ACTIVE | -->
