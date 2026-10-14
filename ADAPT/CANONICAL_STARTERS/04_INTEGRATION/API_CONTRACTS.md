# API Contracts

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
MILESTONE: {{ACTIVE_MILESTONE}}
SOURCE_TRUTH_VERSION: {{SOURCE_TRUTH_VERSION}}

## Purpose

Defines the agreed API contracts between backend producers and frontend (or other) consumers. Each entry represents an endpoint or API surface that has been accepted by both the producing and consuming lane.

## API Contracts

| API-ID | Endpoint | Method | Request Body | Response Body | Auth Required | Error Codes | Version | Status | Notes |
|--------|----------|--------|-------------|--------------|---------------|-------------|---------|--------|-------|
<!-- EXAMPLE: | API-001 | /auth/login | POST | { email: string, password: string } | { token: string, expiresAt: string } | No | 400 Invalid, 401 Unauthorized | V0.1 | ACCEPTED | Session token format: JWT | -->

## Status Values

- DRAFT: Defined but not yet reviewed
- ACCEPTED: Both producer and consumer lanes have agreed
- DEPRECATED: No longer in use; retained for traceability
- CONFLICT: Incompatibility between producer and consumer

## Notes

API contracts are the authoritative binding between backend and frontend lanes. Frontend must not invent API behavior outside these contracts. Backend must not change accepted contracts without going through Integrator reconciliation.
