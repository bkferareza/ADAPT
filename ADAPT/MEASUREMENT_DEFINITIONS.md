# MEASUREMENT DEFINITIONS

Definitions of the measures used to evaluate ADAPT. This file defines measures only: it collects no values, sets no targets, and adds no runtime field. It is framework documentation, never copied into an instance and never a project document.

Each measure is taken manually from an instance's existing artifacts. No measure is scored by the operator whose work it evaluates (GOVERNANCE_RULES.md, Rule 13).

## 1. Independent Context Recovery

- Question: Can someone other than the original operator recover a solution's working context from its ADAPT artifacts?
- Definition: for a new ticket, the share of a fixed checklist of context facts (requirements in scope, open questions, prior decisions, constraints) that a person who is not the operator establishes correctly from the artifacts before consulting source code.
- Sources: the instance's source truth, OPEN_QUESTIONS.md, DECISION_LOG.md and GAP_REGISTER.md.
- Status: NOT_MEASURABLE_WITH_CURRENT_ARTIFACTS. Missing data point: a recorded recovery exercise, naming the checklist, who performed it, and what they established.
- Limits: depends on the reviewer's experience and the checklist chosen. One exercise is an anecdote, not a rate.

## 2. Requirement / Constraint Gap Yield

- Question: Does structured intake surface material context the ticket did not contain?
- Definition: per ticket, the number of open questions and gaps raised at intake that the ticket did not state, divided by the number of requirements extracted from it.
- Sources: OPEN_QUESTIONS.md, GAP_REGISTER.md, REQUIREMENTS_INDEX.md and the promoted ticket.
- Status: PARTIALLY_MEASURABLE. Missing data point: whether each item came from the ticket, from intake, from a human or from the repository. This is not recorded today.
- Limits: a high yield may reflect a weak ticket rather than a strong intake. Counts say nothing about materiality.

## 3. Repository Dependency Observation

- Question: How often does preparing work still require reading source code rather than the artifacts?
- Definition: per ticket, the number of preparation steps that required direct repository access, and what each sought.
- Sources: none today.
- Status: NOT_MEASURABLE_WITH_CURRENT_ARTIFACTS. Missing data point: a record, kept during preparation, of each repository access and its purpose.
- Limits: some code reading is legitimate. The measure describes dependency, not failure.

## 4. Time to First Authorized Work Package

- Question: How long does ADAPT preparation take before governed work may begin?
- Definition: elapsed time from intake of a ticket to the first Lane Assignment that binds a handoff for it.
- Sources: INTAKE_REGISTER.md and DECISION_LOG.md dates, and the first assignment handoff.
- Status: MEASURABLE_NOW, at the granularity of recorded dates.
- Limits: measures preparation, not delivery speed. Time spent waiting on humans counts as elapsed time.

## 5. Recurrence After Promotion

- Question: Did a promoted framework change stop the failure it addressed?
- Definition: for each PROMOTED candidate, the number of later GAP-T14 gaps or candidates describing the same failure in instances scaffolded at or after its Introduced In version.
- Sources: FRAMEWORK_LEARNING_REGISTER.md, and instance GAP_REGISTER.md entries and VERSION: headers.
- Status: PARTIALLY_MEASURABLE. Missing data point: a link from a later gap or candidate to the earlier candidate it repeats. Matching is manual today.
- Limits: no recurrence may only mean the path was not exercised again.

## 6. Framework Learning Disposition Distribution

- Question: Is the learning loop producing learning or noise?
- Definition: the number of candidates under each disposition, and the share still pending.
- Sources: FRAMEWORK_LEARNING_REGISTER.md.
- Status: MEASURABLE_NOW. The register has no candidates yet.
- Limits: a high rejection share may mean the Rule 14 threshold is too loose, or only that early candidates were weak. It prompts review; it is not a verdict.
