# Context Budgets

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

This document defines context size classifications for ADAPT actions. The Context Steward must select the appropriate tier before assembling a context pack. When an action spans multiple tiers, the larger tier applies.

---

## Size Tiers

### XS — Minimal

**Included artifacts:**
- One command or directive
- One small artifact (single register row, single status field, routing instruction)
- No cross-lane context

**Excluded artifacts:**
- Requirements documents
- Scope contracts
- Handoff chains
- Decisions from other lanes

**Director approval required:** No

**Use for:**
- Simple status queries
- Single-register updates
- Command routing
- Quick confirmation responses

**Note:** If any cross-lane context is required, escalate to S or higher.

---

### S — Small

**Included artifacts:**
- One requirement or business item
- One scope contract
- One template or form

**Excluded artifacts:**
- Integration contracts
- Multi-lane context
- Full decision logs
- QA artifacts

**Director approval required:** No

**Use for:**
- Single business item analysis
- Template generation
- Onboarding start
- Focused single-requirement clarification

**Note:** If decisions from other lanes must be consulted, escalate to M.

---

### M — Medium

**Included artifacts:**
- One or more requirements scoped to the business item
- Scope contract for the action
- Relevant decisions from DECISION_LOG.md (scoped to this item)
- One active integration or lane contract (if applicable)
- Active handoff for the action

**Excluded artifacts:**
- Full decision log history
- Unrelated lane artifacts
- QA or integration artifacts not directly involved

**Director approval required:** No

**Use for:**
- Standard bounded implementation action
- Single-lane work of moderate complexity
- Focused design or analysis tasks within one workcell

**Note:** If QA or Integration must actively participate, escalate to L.

---

### L — Large

**Included artifacts:**
- Multi-lane context (implementation + integration + QA as needed)
- Integration contracts relevant to the milestone
- QA artifacts (test cases, defect register, signoff register)
- Director awareness artifacts (control plane summary, active blockers)
- Active handoff chain for the milestone

**Excluded artifacts:**
- Archived handoffs from prior milestones
- Context deltas older than current cycle
- Unrelated workcell scopes

**Director approval required:** Yes — Director must be informed before L-tier action begins

**Use for:**
- Integration review sessions
- QA validation runs
- Cross-lane consolidation
- Milestone close preparation

**Note:** If the full lane audit or a major replan is required, escalate to XL.

---

### XL — Extra Large

**Included artifacts:**
- Full lane audit scope (all active workcells, all open items)
- Release readiness artifacts (RELEASE_READINESS.md, SIGNOFF_REGISTER.md)
- Full gap register and blocker register
- Full decision log for the milestone
- Director approval artifacts

**Excluded artifacts:**
- Per-workcell implementation details not relevant to release or replan
- Prior milestone artifacts (unless carry-over)

**Director approval required:** Yes — human approval or splitting is required before XL action proceeds

**Use for:**
- Release readiness review
- Milestone close
- Major gap resolution
- Full replan after blocker or scope change

**Note:** If an XL action cannot be completed within a single bounded session, it must be split into multiple L or M actions and sequenced by the Planning Lane.
