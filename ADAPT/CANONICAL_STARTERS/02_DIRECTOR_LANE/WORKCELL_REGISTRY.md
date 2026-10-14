# Workcell Registry

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

Registry of all workcells that have been onboarded in this ADAPT instance. Director maintains this registry. Each entry links to the workcell folder.

## Registry

| Workcell ID | Role | Human Owner | Folder Path | Onboarded Date | Status | Notes |
|-------------|------|-------------|-------------|----------------|--------|-------|
<!-- EXAMPLE: | BACKEND_ANA | Backend Developer | Ana {{LAST_NAME}} | ADAPT/03_WORKCELLS/BACKEND_ANA/ | {{DATE}} | ACTIVE | Scope: backend API layer | -->

## Status Values

- ACTIVE: Workcell is operational and receiving assignments
- PAUSED: Temporarily not receiving new assignments
- COMPLETED: Work finished; workcell will be archived
- ARCHIVED: Historical; folder preserved in ARCHIVE/

## Notes

Workcell IDs follow the pattern: {{ROLE_ABBREVIATION}}_{{IDENTITY_SHORTNAME}} (e.g., BACKEND_ANA, QA_CARLOS). Each workcell ID must be unique within this ADAPT instance.
