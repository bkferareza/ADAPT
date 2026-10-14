# ADAPT

ADAPT is a file-based framework for governing AI-assisted software work. It separates
requirements, authority, task scope, handoffs, validation and delivery evidence so
an agent can recover current state without reconstructing decisions from chat.

It addresses ambiguous ownership, accidental scope expansion, stale context,
untraceable completion claims and repeated reasoning for routine inspection.
The framework source is [ADAPT/](ADAPT/START_HERE.md); a scaffolded instance is a
separate project-specific governance directory. Application code stays in its
project repository.

## Architecture and authority

Sixteen governance directories cover framework rules, source truth, Director
control, workcells, integration, validation, handoffs, guardrails, templates,
challenge, context, onboarding, cleanup, planning, references and commands.
The [control-plane schema](ADAPT/CANONICAL_STARTERS/15_COMMANDS_AND_DRIVERS/CONTROL_PLANE_SCHEMA.md)
defines 21 live state fields. Director assignment, explicit identity and scope,
human approval gates and one bounded action per handoff govern execution.
Evidence is classified as GROUNDED, REVIEWED or ASSERTED. Developer self-validation
is not independent QA signoff. [Governance rules](ADAPT/CANONICAL_STARTERS/00_FRAMEWORK/GOVERNANCE_RULES.md)
and canonical artifacts remain authoritative; tooling never grants authority.

## Scaffold a new instance

Provide an AI agent the framework path, project folder, project document, target
instance path and explicit RoutingMode (`PROTECTED_DEFAULT` or `DUAL_WRITE`). Then:

```text
Read and Execute ADAPT/START_HERE.md
```

Follow [the actual scaffold workflow](ADAPT/SCAFFOLD_WORKFLOW_AGENT.md), not a CLI
installation wizard. [Deployment modes](ADAPT/DEPLOYMENT_MODES.md) are
`MODE_A_EXISTING_SOLUTION` (read-only discovery of existing code) and
`MODE_B_REQUIREMENTS_ONLY` (document-driven initialization). Unresolved facts
become questions/gaps; source truth is not automatically promoted. RoutingMode
has no default. Project source mutation defaults to NO.

The output contains the canonical governance directories, initialized control
plane and **TOOLS/**. New scaffolds automatically run the narrow tooling copy
and hash verification step; no manual operator copy is required. See the
[output contract](ADAPT/SCAFFOLD_OUTPUT_CONTRACT.md). Recovery preserves existing
state and does not migrate tooling automatically.

## Operator tooling

Python 3.9+ is required for tooling and its scaffold distribution step. Git is
needed only by `evidence`. There are no external Python packages, service
credentials, network services or AI integrations. Tool use is optional; the
distribution is included in every new scaffold. From a generated instance:

```powershell
python ADAPT/TOOLS/adapt.py state --instance ADAPT --json
python ADAPT/TOOLS/adapt.py doctor --instance ADAPT --json
python ADAPT/TOOLS/adapt.py prompt next --instance ADAPT --json
python ADAPT/TOOLS/adapt.py evidence --instance ADAPT --repo ../PROJECT --file src/example.py --json
```

Supply the root directly containing `02_DIRECTOR_LANE`. The repository path must
be its Git root; evidence file paths are explicit and repo-relative. Human output
is available by omitting `--json`. The same commands run against an external
instance using explicit paths from this repository's `ADAPT/TOOLS/adapt.py`.

- **state:** deterministic schema-ordered JSON with recorded string values.
- **doctor:** structural/value/reference/register diagnostics, with unsupported
  history or semantic checks explicitly unverified.
- **prompt next:** an operator invocation preview only when recorded identity,
  Director handoff, scope, decisions, context integrity and evidence agree.
  Fresh scaffolds have no executing workcell and correctly return BLOCKED.
- **evidence:** local Git metadata, changed paths and bounded SHA256 file hashes.

See [tool documentation](ADAPT/TOOLS/README.md) and the
[decision contract](ADAPT/CANONICAL_STARTERS/15_COMMANDS_AND_DRIVERS/TOOLING_DECISION_CONTRACT.md).
All four commands are read-only. Prompt generation never executes anything.
No result substitutes for human approval, semantic guardrails or certification.

## Validation and release status

Tooling v1 is a repository-owner-directed framework release. Automated evidence,
test commands and limitations are recorded in the
[release record](ADAPT/VALIDATION/TOOLING_V1_RELEASE.md). Tests use fresh temporary
canonical-derived instances and the actual mandatory tool distribution step.
They verify standalone generated-instance execution, deterministic outputs,
failure behavior, input integrity and focused contract consistency.

```powershell
python -B -m unittest discover -s ADAPT/EXPERIMENTS/STATE_READER/tests -v
python -B -m unittest discover -s ADAPT/EXPERIMENTS/OPERATOR_TOOLKIT/tests -v
python -B -m unittest discover -s ADAPT/TOOLS/tests -v
```

These are automated self-validation results, not independent QA, release
certification or a claim that every agent-led discovery/extraction workflow has
been validated. The original broader [scaffold test record](ADAPT/VALIDATION/SCAFFOLD_TEST_RECORD.md)
separately describes its scope and pending live agent-run validation.

## Evolution and limitations

Framework Maintainer decisions and versions are recorded in the
[framework learning register](ADAPT/FRAMEWORK_LEARNING_REGISTER.md). The current
version is **ADAPT-FW-0002** with Tooling v1. Changes are
prospective; existing instances require explicit upgrade/backport authorization.
No second authority database is introduced.

Tooling supports a bounded subset of Markdown layouts and exact workcell roles.
Unsupported lane/role selection, unresolved approval references or ambiguous
context return BLOCKED. Hashes detect changes in declared files, not undisclosed
dependencies or forged approvals. Concurrent modifications are not an atomic
snapshot. Windows/Python 3.11 is the exercised environment; other platforms use
portable standard-library paths but have not been certified. There is no ADAPT
Studio, automated execution, result ingest or existing-instance migration.

## Repository overview

```text
README.md                         public introduction
ADAPT/                            canonical framework source
  CANONICAL_STARTERS/              governance artifacts copied to instances
  TOOLS/                          self-contained operator distribution
  EXPERIMENTS/                    compatibility entry points and regression tests
  VALIDATION/                    distribution verifier and release evidence
```
