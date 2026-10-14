# FRAMEWORK LEARNING REGISTER

Current Framework Version: ADAPT-FW-0002

## Purpose

The framework-level record of framework-learning candidates and the Framework Maintainer's disposition of each, and the single declaration of the current framework version. Scaffolding copies that version into every new instance as `VERSION:`.

## Authority and Scope

- Sole writer: the Framework Maintainer (GOVERNANCE_RULES.md, Rule 14). No instance actor writes this file.
- Framework-scoped. It lives at the framework root, outside CANONICAL_STARTERS, and is never copied into an instance.
- Not instance truth. An observation stays evidence in the instance where it arose. Only a candidate's Proposed Generic Change can become framework content, and only through a PROMOTED disposition and an authorized framework patch.
- Prospective. A promoted change reaches future scaffolds through the canonical starters. Existing instances are never rewritten automatically; recovery does not overwrite existing files (DEPLOYMENT_MODES.md). Any upgrade or backport is a separate, deliberate decision.

## Framework Version

- Format ADAPT-FW-NNNN, where NNNN is a zero-padded positive integer. Numeric order is framework order.
- Declared and advanced only by the Framework Maintainer: once per authorized framework patch containing one or more PROMOTED candidates, never once per file or per candidate.
- A label, once issued, is never reused or redefined.

## Pre-Register Hardening Baseline

ADAPT-FW-0001 is the first codified hardened baseline. Its controls, including those introduced by the hardening work that created this register, predate the register and have no candidate rows here. Their rationale and acceptance evidence are held in the Framework Maintainer's hardening records outside this framework. They are not reconstructed here as candidates, and no candidate ID, decision reference or evidence record is invented for them.

ADAPT-FW-0001 becomes an issued framework state when the first instance is scaffolded from it, and is never redefined after that. A control is kept while the failure or risk it addresses still exists. Every later change to a framework control, including the simplification or removal of a baseline control, is recorded here as a candidate before it is promoted.

## Raising a Candidate

A candidate is recorded only when it meets the framework-learning threshold in GOVERNANCE_RULES.md, Rule 14. It arrives by Director escalation of a GAP-T14 Framework Gap or a qualifying Memory Bank lesson.

Novelty Dimensions name what was materially new, one or more of: SOLUTION_OR_REPOSITORY, ROLE, WORK_TYPE, EXECUTION_PATH, VALIDATION_MECHANISM, DEPLOYMENT_OR_RUNTIME, GOVERNANCE_COMBINATION. GOVERNANCE_COMBINATION means a combination of authorities, gates, approvals, exceptions, or governance conditions exercised together in one flow that has not previously been exercised as that combination.

Evidence lists the references and their evidence class (GOVERNANCE_RULES.md, Rule 5). Solution-Specific Portion and Proposed Generic Change are always recorded separately.

## Dispositions

- `—` — pending; not yet disposed
- PROMOTED — the generic change is incorporated; requires Decision and Introduced In
- REJECTED_NON_GENERIC — valid but solution-specific; stays local
- REJECTED_INSUFFICIENT_EVIDENCE — not established; may be re-raised with more evidence
- ALREADY_COVERED — an existing control handles it; Decision names that control
- DEFERRED — valid but postponed; Decision gives the reason
- CONTRADICTED — stronger evidence shows the claim is wrong; Decision cites it

A disposed candidate is never deleted. Introduced In (an ADAPT-FW-NNNN label), Backport (ELIGIBLE or NOT_ELIGIBLE) and Upgrade Assessment (REQUIRED or NOT_REQUIRED) apply only to PROMOTED candidates and are `—` otherwise. Candidate IDs follow FLC-NNN.

## Candidates

| FLC-ID | Observed In | Evidence | Novelty Dimensions | Solution-Specific Portion | Proposed Generic Change | Disposition | Decision | Introduced In | Backport | Upgrade Assessment |
|---|---|---|---|---|---|---|---|---|---|---|

| FLC-001 | Tooling v1 consolidation, 2026-10-15; owner-raised framework gap review | GROUNDED: VALIDATION/TOOLING_V1_TEST_OUTPUT.txt, TOOLS/MANIFEST.json; ASSERTED summary: VALIDATION/TOOLING_V1_RELEASE.md | GOVERNANCE_COMBINATION, VALIDATION_MECHANISM | No client instance or solution-specific changes | Align placeholder validation, lifecycle ownership and schema write precedence; distribute read-only tools with explicit handoff-bound preview and reproducible copy verification | PROMOTED | Current repository-owner/Framework Maintainer directive: ADAPT — TOOLING V1 COMPLETION AND PUBLICATION; explicitly authorizes this scoped correction, promotion and publication after validation. Recorded on behalf of that human authority, not an AI/Director self-approval or historical signature. See VALIDATION/TOOLING_V1_RELEASE.md. | ADAPT-FW-0002 | ELIGIBLE | REQUIRED |
