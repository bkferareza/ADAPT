# COMMAND_SYNTAX.md
STATUS: DRAFT

## Purpose
Defines the canonical syntax rules for all ADAPT commands. Commands that deviate from these rules must be rejected by the Director Intake Agent. This file is authoritative for command validation.

---

## Syntax Rules

### Rule 1 — Commands Must Use Exact ADAPT Command Names
Every command must match a command name listed in COMMAND_REGISTRY.md. Paraphrasing, abbreviation, or natural-language task description is NOT a valid command.

### Rule 2 — {{DOUBLE_BRACE}} Placeholders Must Be Filled
Any `{{PLACEHOLDER}}` in a command name must be replaced with the actual value for that execution. A command issued with an unfilled placeholder is invalid unless it is being referenced as a template (e.g., in documentation).

### Rule 3 — Commands Must Not Combine Multiple Actions
Each command must represent one atomic action. Chaining multiple actions in a single command (e.g., "Onboard Brian and Plan milestone M01") is NOT valid.

### Rule 4 — Commands Do Not Carry Implementation Instructions
A command invokes a governed ADAPT workflow. It does not carry inline implementation instructions. Implementation is governed by handoffs, scope contracts, and context packs — not by command arguments.

### Rule 5 — Lane/Role Context Is Determined by the Control Plane, Not by the Command Text
You do not prefix a command with a role name. The Director Intake Agent reads the control plane to determine which lane or agent handles the command.

### Rule 6 — Approval Gates Are Not Part of Command Syntax
Commands do not contain approval tokens. Approval is recorded in the appropriate register (e.g., DECISION_LOG.md, SOURCE_TRUTH_VERSION_LOG.md) prior to the command being processed.

---

## Valid Commands

The following are canonical valid commands. Commands with `{{DOUBLE_BRACE}}` values show the template form followed by an example.

| # | Template Form | Example |
|---|--------------|---------|
| 1 | `Initialize ADAPT from requirements` | `Initialize ADAPT from requirements` |
| 2 | `Promote {{DOCUMENT_NAME}} as {{SOURCE_TRUTH_VERSION}}` | `Promote ProjectSpec.docx as SOURCE_TRUTH_V0.1` |
| 3 | `Analyze requirements into source truth` | `Analyze requirements into source truth` |
| 4 | `Run Director intake` | `Run Director intake` |
| 5 | `Onboard {{IDENTITY}} as {{ROLE}}` | `Onboard Ana as Backend Developer` |
| 5b | `Onboard {{IDENTITY}} as {{ROLE}}` | `Onboard Brian as Integrator` |
| 6 | `Plan milestone {{MILESTONE_ID}}` | `Plan milestone M01` |
| 7 | `Approve milestone plan` | `Approve milestone plan` |
| 8 | `Generate roadmap for {{WORKCELL_ID}}` | `Generate roadmap for WC-ANA-BACKEND` |
| 9 | `Generate context pack for active handoff` | `Generate context pack for active handoff` |
| 10 | `Run atomic handoff dispatch` | `Run atomic handoff dispatch` |
| 11 | `Route gap {{GAP_ID}}` | `Route gap GAP-001` |
| 12 | `Resolve blocker {{BLK_ID}}` | `Resolve blocker BLK-003` |
| 13 | `Run integration review` | `Run integration review` |
| 14 | `Run QA validation` | `Run QA validation` |
| 15 | `Trigger challenge review for {{ITEM}}` | `Trigger challenge review for M01 release candidate` |
| 16 | `Run janitor pass` | `Run janitor pass` |
| 17 | `Director consolidate cycle` | `Director consolidate cycle` |
| 18 | `Prepare next cycle` | `Prepare next cycle` |

---

## Invalid Commands — With Explanations

| # | Invalid Command | Why It Is Invalid | Correct Alternative |
|---|----------------|------------------|---------------------|
| 1 | `Implement the login feature` | NOT VALID: this is a task description, not an ADAPT command. There is no authority specified, no handoff referenced, and no workcell scope active. Workcell execution happens through `Run atomic handoff dispatch` under a pre-assigned active handoff. | Issue: `Run atomic handoff dispatch` — after the workcell has been onboarded, a milestone planned, and a handoff has been routed to the workcell for the login feature work. |
| 2 | `Fix the bug` | NOT VALID: this is too ambiguous to be actionable. ADAPT requires all work to reference a specific BI-ID (business item), DEF-ID (defect), or GAP-ID so that authority, scope, and evidence can be traced. | Create or reference a DEF-ID in the DEFECT_REGISTER.md and then: `Run atomic handoff dispatch` (for the assigned workcell) or `Route gap GAP-ID` (if this is an unowned defect). |
| 3 | `Do everything for M01` | NOT VALID: this violates the Atomic Handoff Dispatch rule. ADAPT requires every execution unit to be bounded, one at a time, with evidence and handoffs between each step. "Everything" cannot be a single atomic action. | Break M01 work into individual commands: `Plan milestone M01` → Director approves → per-workcell handoffs → `Run atomic handoff dispatch` (once per bounded task) → `Run integration review` → `Run QA validation` → `Director consolidate cycle`. |
| 4 | `Onboard Brian` | NOT VALID: the role is missing. The `Onboard` command requires both an identity and a role. Without a role, the Onboarding Orchestrator cannot generate role-specific blueprints, assign scope contracts, or register the workcell correctly. | `Onboard Brian as {{ROLE}}` — e.g., `Onboard Brian as Integrator` |
| 5 | `QA sign off on M01` | NOT VALID: QA signoff is the outcome of a governed QA validation workflow, not a command that can be issued directly. Signoff is produced by the QA Orchestrator after running test scenarios against accepted acceptance criteria. Issuing it as a command bypasses evidence production, defect recording, and independence requirements. | `Run QA validation` — the QA Orchestrator then produces test cases, executes them, records defects, and emits a QA recommendation (PASS / CONDITIONAL_PASS / FAIL). The QA validation report becomes the signoff record. |
| 6 | `Plan everything` | NOT VALID: planning must reference a specific milestone ID. "Everything" is not a milestone. Planning in ADAPT is milestone-scoped to ensure bounded, verifiable recommendations. | `Plan milestone {{MILESTONE_ID}}` — e.g., `Plan milestone M01` |
| 7 | `Director approve` | NOT VALID: Director approval is not a standalone command. Approval actions in ADAPT are recorded in specific registers (DECISION_LOG.md, SOURCE_TRUTH_VERSION_LOG.md, ONBOARDING_REPORTS.md) and are tied to a specific approval gate. | Identify the approval gate (e.g., milestone plan, onboarding, source truth promotion) and record approval in the appropriate register, then issue the follow-on command. |

---

## Command Parsing Checklist

When the Director Intake Agent receives a command string, it must:

1. Check that the command string matches a command name in COMMAND_REGISTRY.md (exact match after filling any `{{PLACEHOLDER}}` values).
2. Verify all `{{PLACEHOLDER}}` values have been filled with actual identifiers.
3. Confirm the command is a single atomic action (no chaining).
4. Look up the command's Required Authority in COMMAND_REGISTRY.md and confirm the current control plane state supports that authority.
5. Look up Approval Required. If YES, confirm approval is on record before routing.
6. Route to the Target Orchestrator specified in COMMAND_REGISTRY.md.
7. Record the intake in INTAKE_REGISTER.md with classification and routing decision.
