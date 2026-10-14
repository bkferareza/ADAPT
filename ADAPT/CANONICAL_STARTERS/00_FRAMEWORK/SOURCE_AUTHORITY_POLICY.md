# Source Authority Policy

STATUS: DRAFT
VERSION: {{ADAPT_VERSION}}
PROJECT: {{PROJECT_NAME}}

## Purpose

Defines what constitutes source truth in this ADAPT instance, how it is promoted, and how it governs work.

## Source Truth Definition

Source truth is any document explicitly promoted and versioned by the Director Lane that governs ADAPT decisions, requirements, acceptance criteria, or architecture. Source truth is the authoritative input for all workcell work.

## Promotion Process

To promote a document as source truth:

1. Issue the command: `Promote {{DOCUMENT_NAME}} as {{SOURCE_TRUTH_VERSION}}`
2. Director Lane validates the document is readable and complete
3. Human approval is required (see HUMAN_APPROVAL_GATES.md)
4. Director records the promotion in SOURCE_TRUTH_VERSION_LOG.md
5. The document is assigned a version identifier: e.g., SOURCE_TRUTH_V0.1
6. All downstream work must trace to the promoted version

## Version Identifier Format

Source truth versions use: SOURCE_TRUTH_V{{MAJOR}}.{{MINOR}}

Examples: SOURCE_TRUTH_V0.1, SOURCE_TRUTH_V1.0, SOURCE_TRUTH_V1.1

## Authority Hierarchy

1. Promoted source truth documents (highest authority)
2. Accepted contracts and decisions recorded in DECISION_LOG.md
3. Workcell scope contracts (scoped to their lane)
4. Context packs (must reference one of the above)
5. Memory Bank (reference only — lowest authority)

## What Is NOT Source Truth

- Unpromoted documents (reference material only)
- Memory Bank content
- Application source code and runtime behavior — these are OBSERVED_EVIDENCE of what the system currently does, never source truth for what it should do (see Truth Classes)
- AI inference or training knowledge
- Prior-cycle ADAPT state not carried forward via CARRY_OVER_REGISTER.md

## Truth Classes

Every statement ADAPT records about a solution belongs to one class. The class decides
what the statement may govern.

| Class | What it is | What it may govern |
|---|---|---|
| PROMOTED_TRUTH | A statement in a promoted, versioned source truth document, or derived from one with its source quoted verbatim | Requirements, acceptance criteria, decisions, all workcell work |
| CANDIDATE_TRUTH | A statement ADAPT derived — from discovery, intake, or interpretation — that has not been promoted | Nothing. It may be proposed for promotion, questioned, or rejected |
| OBSERVED_EVIDENCE | Measured or read behavior of an existing system: code, runtime output, logs, configuration | What the system currently does. Never what it should do |

There is no separate class for a client document's external authority. A ticket or
specification gains authority in ADAPT only by promotion; who issued it is recorded as
its origin in SOURCE_TRUTH_VERSION_LOG.md, not as a class.

**The forbidden sequence.** Observed behavior must not become a requirement by being
described. The sequence observed implementation → AI interpretation → recorded
requirement → later work treating it as fact converts what a system does into what it
must do, with no decision in between. An observation enters source truth only as a
promoted statement that quotes it, names it as OBSERVED_EVIDENCE, and records who
decided it should become a requirement.

The existing implementation is authoritative evidence of current behavior. It is not
evidence of intended behavior. Where the two may differ, that difference is an open
question, not an inference to resolve.

## Conflict Resolution

If two promoted source truth versions conflict:
1. The conflict must be recorded as an OPEN_QUESTIONS.md entry
2. The Director must resolve the conflict and record the decision in DECISION_LOG.md
3. A new source truth version may be promoted to incorporate the resolution

## Consumption Rules

- Every workcell task must reference a source truth version
- Context packs must declare which source truth version they were built against
- Evidence must be traceable to source truth
- If the relevant source truth version has been superseded, the work must be re-validated against the current version
