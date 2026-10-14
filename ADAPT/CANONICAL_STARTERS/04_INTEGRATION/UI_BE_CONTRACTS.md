# UI–Backend Contracts

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
MILESTONE: {{ACTIVE_MILESTONE}}

## Purpose

Records the agreed UI behavior expectations and their corresponding backend API bindings. Covers loading states, success states, empty states, validation feedback, and error handling.

## UI–Backend Bindings

| UIBE-ID | UI Screen/Component | Trigger | Backend Endpoint | Loading State | Success State | Empty State | Error State | Validation | Status | Notes |
|---------|--------------------|---------|-----------------|--------------|--------------|-----------:|-------------|------------|--------|-------|
<!-- EXAMPLE: | UIBE-001 | Login Form | Submit button click | POST /auth/login | Spinner on submit button | Redirect to dashboard | N/A | Show error message from API | Required: email format, password non-empty | ACCEPTED | — | -->

## Status Values

- DRAFT / ACCEPTED / CONFLICT / DEPRECATED

## Notes

These bindings are derived from both accepted API contracts (API_CONTRACTS.md) and accepted UI flow definitions. Any discrepancy between what the UI expects and what the API provides must be escalated to the Integrator.
