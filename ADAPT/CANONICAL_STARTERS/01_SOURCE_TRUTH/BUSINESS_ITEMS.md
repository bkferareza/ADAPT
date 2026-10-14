# Business Items

STATUS: DRAFT
VERSION: {{ADAPT_VERSION}}
PROJECT: {{PROJECT_NAME}}
SOURCE_TRUTH_VERSION: {{SOURCE_TRUTH_VERSION}}

## Purpose

Business items, stories, and features derived from the promoted source truth. Each business item links to one or more requirements in REQUIREMENTS_INDEX.md.

## Business Items

| BI-ID | Title | Description | Linked REQ-IDs | Domain | Priority | Status | Notes |
|-------|-------|-------------|----------------|--------|----------|--------|-------|
<!-- EXAMPLE: | BI-001 | User Login | Allow users to authenticate with email and password | REQ-001, REQ-002 | Authentication | HIGH | ACTIVE | Frontend + Backend scope | -->

## Status Values

- DRAFT: Captured but not yet reviewed
- ACTIVE: Approved for implementation
- IN_PROGRESS: Assigned to one or more workcells
- DONE: Implementation complete and accepted
- DEFERRED: Not scheduled for current milestone
- BLOCKED: Cannot proceed due to a dependency or gap

## Domain Categories

Domains are project-specific. Populate with: {{DOMAIN_LIST}}
Examples: Authentication, User Management, API, UI, Data, Reporting, Integration, Infrastructure

## Notes

Business items are the unit of work that Directors assign to workcells. They must link to at least one accepted requirement. BI-IDs follow format BI-NNN.
