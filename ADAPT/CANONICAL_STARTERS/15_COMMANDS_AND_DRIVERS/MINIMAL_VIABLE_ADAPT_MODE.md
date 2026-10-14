# MINIMAL_VIABLE_ADAPT_MODE.md
STATUS: DRAFT

## Purpose
Defines ADAPT Lite — a minimal viable ADAPT configuration for small teams, solo developers, or early-stage projects. ADAPT Lite reduces the module footprint without removing the governance properties that make ADAPT meaningful. It is not a simplified version of ADAPT; it is ADAPT with optional modules deferred until they are needed.

---

## What ADAPT Lite Includes (Mandatory Modules)

The following modules are required even in ADAPT Lite. They cannot be deferred or skipped.

| Module | Path | Why It Is Mandatory |
|--------|------|---------------------|
| `00_FRAMEWORK` | `ADAPT/00_FRAMEWORK/` | Governance rules, role model, glossary, and source authority definitions. Without this, the framework has no rules to enforce. |
| `01_SOURCE_TRUTH` | `ADAPT/01_SOURCE_TRUTH/` | Requirements, business items, acceptance criteria, and open questions. Without source truth, there is no governed basis for any work. |
| `02_DIRECTOR_LANE` | `ADAPT/02_DIRECTOR_LANE/` | Control plane, intake register, gap register, blocker register, and decision log. Without the Director Lane, there is no routing, no certification, and no cycle management. |
| `06_HANDOFFS` | `ADAPT/06_HANDOFFS/` | Lite does not relax handoff emission. Every Atomic Handoff Dispatch cycle ends by emitting a handoff, and it needs somewhere to land. |
| `15_COMMANDS_AND_DRIVERS` | `ADAPT/15_COMMANDS_AND_DRIVERS/` | Holds COMMAND_REGISTRY, STOP_RULES and HUMAN_APPROVAL_GATES. Lite relaxes none of the 18 commands, 15 stop rules or 11 approval gates, so none of them can be validated without it. |
| `08_TEMPLATES` | `ADAPT/08_TEMPLATES/` | All standard ADAPT templates. Required to ensure artifact consistency regardless of team size. |
| `10_CONTEXT_ECONOMY` | `ADAPT/10_CONTEXT_ECONOMY/` | Context rules, context budgets, and context index. Required even in Lite mode — context overload risks are present for any team size. |
| `11_ONBOARDING` | `ADAPT/11_ONBOARDING/` | Onboarding rules and role map. Required to properly register any workcell, even in a single-workcell instance. |

---

## Optional Modules — Added As the Project Grows

The following modules are not required at ADAPT Lite initialization. Each is added independently when the need arises. Adding a module does not require re-initializing the ADAPT instance — each module is self-contained.

| Module | Path | When to Add |
|--------|------|-------------|
| `13_PLANNING` | `ADAPT/13_PLANNING/` | Add when milestone planning is needed — when the project has more than one milestone, or when work sequencing across roles requires formal planning output. |
| `07_GUARDRAILS` (full set) | `ADAPT/07_GUARDRAILS/` | Add when multiple workcells are active and cross-lane governance violations become a realistic risk. A single-workcell Lite instance may use only the mandatory guardrails defined in `00_FRAMEWORK`. |
| `04_INTEGRATION` | `ADAPT/04_INTEGRATION/` | Add when backend and frontend lanes diverge and need formal reconciliation. Not needed if the same workcell handles both or if the project is API-only or UI-only. |
| `05_VALIDATION` | `ADAPT/05_VALIDATION/` | Add when a dedicated QA role is onboarded. Not needed if QA is handled by the Director under a CONSTRAINED exception recorded in DECISION_LOG.md. |
| `12_JANITOR` | `ADAPT/12_JANITOR/` | Add when artifact sprawl is detected — typically after two or more completed cycles when handoff and register accumulation becomes noticeable. |
| `09_CHALLENGE_LANE` | `ADAPT/09_CHALLENGE_LANE/` | Add when risk review is needed before a major milestone delivery, before a release, or when assumptions across lanes need independent challenge. |

---

## When to Use ADAPT Lite vs. Full ADAPT

| Condition | Use |
|-----------|-----|
| Solo developer or 2-person team | ADAPT Lite |
| Single-role execution (one workcell doing all implementation) | ADAPT Lite |
| Early project stage — before key technology decisions are made | ADAPT Lite |
| Proof of concept or initial scaffolding | ADAPT Lite |
| Multi-role team with two or more active workcells | Full ADAPT |
| Parallel workcells (backend and frontend running concurrently) | Full ADAPT |
| Integration between backend and frontend required | Full ADAPT (add `04_INTEGRATION`) |
| Independent QA role is required or expected | Full ADAPT (add `05_VALIDATION`) |
| Milestone planning is needed across multiple cycles | Full ADAPT (add `13_PLANNING`) |
| Challenge review is requested before a major release | Full ADAPT (add `09_CHALLENGE_LANE`) |
| Artifact sprawl is causing governance noise | Add `12_JANITOR` (Lite or Full) |

---

## Transition from ADAPT Lite to Full ADAPT

### Transition Principle
ADAPT Lite and Full ADAPT are the same framework. The transition is additive — you add optional modules one at a time as the need arises. No re-initialization is required.

### How to Add an Optional Module
1. The Director Lane (or human initiator) identifies the need for a specific optional module.
2. The Director records the module addition in DECISION_LOG.md: module name, reason for adding, date.
3. The module folder is created and populated from canonical starters (same as initial scaffold).
4. If the module requires a new role (e.g., `05_VALIDATION` requires a QA Workcell), the `Onboard {{IDENTITY}} as {{ROLE}}` command is issued to create the workcell.
5. The control plane is updated: any new phases introduced by the module are added to the `CurrentPhase` allowed values (or noted in the Notes field of the control plane for this instance).

### Transition Is Per-Module
Each optional module is added independently. Adding `13_PLANNING` does not automatically add `09_CHALLENGE_LANE`. The Director decides when each module is needed based on the project's current state.

---

## What ADAPT Lite Does NOT Skip

These governance properties are mandatory in ADAPT Lite. They are not simplified, waived, or approximated.

| Mandatory Governance Property | Why It Cannot Be Skipped |
|-------------------------------|--------------------------|
| **Source truth promotion** | All work must trace to an accepted source truth version. Even a solo developer must promote source truth before implementing. |
| **Evidence production** | Every completed action requires reviewable evidence. Team size does not reduce the evidence standard. |
| **Handoff emission** | Every completed Atomic Handoff Dispatch cycle must emit a handoff. Even in a solo project, the handoff is the record of what was done and what comes next. |
| **Human approval gates** | The 11 human approval gates in HUMAN_APPROVAL_GATES.md apply in ADAPT Lite. A small team does not bypass approval gates — the human approver may be the same person as the sole developer, but the approval must be explicit and recorded. |
| **Stop rules** | All 15 stop rules in STOP_RULES.md apply in ADAPT Lite. Stopping when a stop condition is triggered is not optional for small teams. |
| **Director Lane** | ADAPT Lite requires the Director Lane even in solo projects. In a single-person project, the same person holds both the Director role and the workcell role — but the Director Lane artifacts (control plane, intake register, decision log) must still exist and be maintained. |

---

## Notes for Single-Person ADAPT Lite Projects

When the same person serves as both Director and the sole workcell, ADAPT Lite applies these specific conventions:

1. **No QA independence is possible without a second person.** The Director Lane must record a CONSTRAINED exception in DECISION_LOG.md with the reason (single-person team). Developer self-validation substitutes for independent QA under this exception — but this must be explicitly recorded, not assumed.
2. **Human approval gates are still meaningful.** The same person wearing the "human approver" hat must explicitly record their approval (e.g., "Approval granted: promote ProjectSpec.docx as SOURCE_TRUTH_V0.1 — [date]") before the AI proceeds. Wearing both hats does not eliminate the gate.
3. **Consolidation cycles are still required.** Even solo projects must consolidate at the end of each cycle. Consolidation in a solo ADAPT Lite project is lightweight — a brief control plane update and a DECISION_LOG.md entry — but it must happen.
