# Defect Register

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

Records all defects discovered during QA validation. Defects reference the test case and acceptance criterion that revealed them and are routed to the responsible workcell for resolution.

## Defects

| DEF-ID | TC-ID | AC-ID | Title | Description | Severity | Steps to Reproduce | Expected | Actual | Assigned To | Status | Resolved Date | Notes |
|--------|-------|-------|-------|-------------|----------|-------------------|----------|--------|-------------|--------|---------------|-------|
<!-- EXAMPLE: | DEF-001 | TC-003 | AC-002 | Login fails with correct password on first attempt | User submits correct credentials; receives 401 error. Second attempt succeeds. | HIGH | 1. Navigate to login 2. Enter valid credentials 3. Submit | 200 + session token | 401 Unauthorized | BACKEND_ANA | OPEN | — | Possible race condition in token generation | -->

## Severity Values

- CRITICAL: System unusable; release blocked
- HIGH: Feature does not work; acceptance criterion failed
- MEDIUM: Feature works with degraded behavior
- LOW: Minor visual or non-functional issue

## Status Values

- OPEN: Defect filed; not yet resolved
- IN_PROGRESS: Assigned workcell is investigating or fixing
- RESOLVED: Fix implemented and submitted; awaiting QA retest
- VERIFIED: QA has retested and confirmed fix
- DEFERRED: Not fixing in current milestone; reason in Notes
- CLOSED: Resolved and verified; or intentionally closed

## Notes

DEF-IDs follow format DEF-NNN. All defects must be retested by QA after resolution.
