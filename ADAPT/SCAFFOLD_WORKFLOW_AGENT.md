# SCAFFOLD WORKFLOW AGENT

## Purpose

This file defines how an AI tool scaffolds a full external ADAPT instance from a project document.

## Operating Model

* `ADAPT_FRAMEWORK` is read-only framework source.
* `PROJECT_FOLDER` is the actual project folder.
* `ADAPT_INSTANCE` is the project-specific ADAPT governance output.
* `START_HERE.md` is the launcher.
* This file is the scaffold workflow agent.
* `SCAFFOLD_OUTPUT_CONTRACT.md` defines required generated files.
* `WORKCELL_ONBOARDING_CONTRACT.md` defines onboarding behavior.
* `DEPLOYMENT_MODES.md` defines MODE_A and MODE_B scaffold behavior.
* `CANONICAL_STARTERS/` is the authoritative source for all starter file content.

Do not depend on tool-specific skills or product-specific agent features. Execute this contract using the file and document capabilities available in the current environment.

## Direct Scaffold Execution Rule

`Read and Execute START_HERE.md` is an execution command.

If the scaffold can safely resolve:

* `{{ADAPT_FRAMEWORK_PATH}}`
* `{{PROJECT_FOLDER_PATH}}`
* `{{ADAPT_INSTANCE_PATH}}`
* `{{PROJECT_DOCUMENT_PATH}}`

then it must proceed directly with:

`FULL_EXTERNAL_ADAPT_INSTANCE_SCAFFOLD`

Do not ask for another approval.
Do not ask the user to reply "Approved."
Do not convert scaffolding into a wizard.

Creating folders and files inside `{{ADAPT_INSTANCE_PATH}}` is part of scaffolding and does not require separate file-creation approval.

## No Wizard Rule

ADAPT scaffolding is not an installation wizard.

The command `Read and Execute START_HERE.md` is sufficient authorization to scaffold the external ADAPT instance.

The AI must not ask for a second approval before creating scaffold files inside `{{ADAPT_INSTANCE_PATH}}`.

The AI should infer safe defaults, proceed with scaffolding, record unresolved details as open questions/gaps, and stop with an initialization report.

Approval-style prompts are allowed only for unsafe conditions such as destructive overwrite, ambiguous paths, project source mutation, or unreadable/missing project documents.

## Required Inputs

Resolve these values before scaffolding:

* `{{ADAPT_FRAMEWORK_PATH}}`
* `{{PROJECT_FOLDER_PATH}}`
* `{{ADAPT_INSTANCE_PATH}}`
* `{{PROJECT_DOCUMENT_PATH}}`

Project source mutation defaults to:

`NO`

The launcher command supplies scaffold file-creation authorization for `{{ADAPT_INSTANCE_PATH}}`. File creation approval is not a separate required input.

## Path Resolution

Infer safe defaults before asking questions.

### ADAPT Framework Path

If `{{ADAPT_FRAMEWORK_PATH}}` is not provided, use the current directory containing `START_HERE.md`.

### Project Document Path

If `{{PROJECT_DOCUMENT_PATH}}` is not provided, search the ADAPT framework root for likely project documents with these extensions:

* `.docx`
* `.md`
* `.txt`
* `.pdf`

Prefer names that indicate project or business requirements, including:

* `Project`
* `Business`
* `Requirements`
* `Proposal`
* `Case`
* a product-specific or project-specific name

Exclude ADAPT framework contracts, launcher files, templates, guardrails, command drivers, framework reports, and other framework documentation.

If exactly one likely project document is found, use it.

If multiple likely documents are found, choose the most project-specific document only when the choice is obvious. If it is not obvious, stop and ask only for `{{PROJECT_DOCUMENT_PATH}}`.

The project name should be inferred from the resolved project document when its title or contents provide a reliable name. Do not invent a project name.

### Project Folder Path

If `{{PROJECT_FOLDER_PATH}}` is not provided, create or use a sibling folder beside the ADAPT framework folder:

`{{ADAPT_FRAMEWORK_PARENT}}/{{PROJECT_NAME}}_PROJECT`

If the project name cannot yet be inferred, use:

`{{ADAPT_FRAMEWORK_PARENT}}/PROJECT_FOLDER`

Do not create the project folder inside `ADAPT_FRAMEWORK` unless it already exists there and the user explicitly provided that path.

### ADAPT Instance Path

If `{{ADAPT_INSTANCE_PATH}}` is not provided, create or use a sibling folder beside the ADAPT framework folder:

`{{ADAPT_FRAMEWORK_PARENT}}/{{PROJECT_NAME}}_ADAPT_INSTANCE`

If the project name cannot yet be inferred, use:

`{{ADAPT_FRAMEWORK_PARENT}}/ADAPT_INSTANCE`

Do not create the ADAPT instance inside `PROJECT_FOLDER`.
Do not create the ADAPT instance inside `ADAPT_FRAMEWORK` unless the user explicitly provided that path.

## ADAPT Instance Target Handling

Creating the target directory and scaffold files is normal execution.

* If `{{ADAPT_INSTANCE_PATH}}` does not exist, create it and scaffold the full ADAPT instance.
* If it exists and is empty, scaffold into it.
* If it already contains an ADAPT instance, recover existing state and do not overwrite blindly.
* If it contains unrelated files, stop and ask for a different ADAPT instance path or whether to create a subfolder.

Recovery must preserve existing ADAPT state. Any destructive overwrite, deletion, replacement, or archival requires an explicit decision before proceeding.

## Deployment Mode Detection

Before scaffolding, detect which deployment mode applies. See `DEPLOYMENT_MODES.md` for full mode definitions.

```
If {{PROJECT_FOLDER_PATH}} exists AND contains application source files
(code files, solution files, build configs, or existing documentation):
→ MODE_A: EXISTING_SOLUTION

If {{PROJECT_FOLDER_PATH}} does not exist, OR contains no source files,
OR only a project document is the input with no existing codebase:
→ MODE_B: REQUIREMENTS_ONLY
```

Record the detected mode in `PROJECT_CONTROL_PLANE.md` under `DeploymentMode` before completing scaffolding.

## Workflow

1. Locate `START_HERE.md` and resolve `{{ADAPT_FRAMEWORK_PATH}}`.
2. Infer `{{PROJECT_DOCUMENT_PATH}}`, `{{PROJECT_NAME}}`, `{{PROJECT_FOLDER_PATH}}`, and `{{ADAPT_INSTANCE_PATH}}` using the path resolution rules.
3. Validate that the resolved paths satisfy the placement and target-folder safety rules.
4. Read `START_HERE.md`.
5. Read `SCAFFOLD_WORKFLOW_AGENT.md`.
6. Read `SCAFFOLD_OUTPUT_CONTRACT.md`.
7. Read `WORKCELL_ONBOARDING_CONTRACT.md`.
8. Read `DEPLOYMENT_MODES.md`.
9. Detect deployment mode (MODE_A or MODE_B) using the detection logic above.
10. If MODE_A: run the read-only discovery pass defined in `DEPLOYMENT_MODES.md` before proceeding.
11. Read the resolved project document.
12. Extract source truth.
13. Infer project shape.
14. Create or recover the full external ADAPT instance using canonical starters (see Canonical Starters section below).
15. Populate starter artifacts required by the scaffold output contract. For a
    NEW instance, automatically perform the Tooling Distribution step below.
16. Record missing details as open questions and gaps.
17. Do not create real workcells unless onboarding commands were provided.
18. Keep project source mutation at `NO` unless the user explicitly requested a clear project shell or source mutation scope.
19. Populate PROJECT_CONTROL_PLANE.md completely. Every field takes a value. No
	{{...}} placeholder may survive scaffold completion.

	| Field | Value at scaffold completion |
	|---|---|
	| ProjectName | resolved project name |
	| ProjectType | one of: Web App, Mobile App, API Service, Data Pipeline, Mixed. If none fit, use a free-form value and record the justification in Notes. |
	| DeploymentMode | the detected mode |
	| RoutingMode | the routing mode supplied as an operator input. No default. If not supplied, STOP and ask. |
	| InitializationMode | FULL_EXTERNAL_ADAPT_INSTANCE_SCAFFOLD |
	| SourceTruthVersion | NONE |
	| ActiveMilestone | NONE |
	| ActiveCycle | NONE |
	| ActiveHandoff | NONE |
	| CurrentAuthority | Director Lane |
	| ExecutionReadiness | NEEDS_PLANNING |
	| CurrentPhase | INITIALIZED |
	| ActiveWorkcell | NONE |
	| Blocked | NO |
	| ActiveBlockers | NONE |
	| ActiveGaps | comma-separated GAP-IDs raised during discovery, else NONE |
	| LastAction | description of this scaffold run, with date |
	| LastContextDelta | NONE |
	| NextExpectedAction | Run Director intake |
	| LastConsolidatedAt | NEVER |
	| Notes | terminal state, and any deviations |

	Where this table specifies a literal, write that literal exactly. Do not invent a
	value for any field.

	ExecutionReadiness is never READY at scaffold completion. No source truth is
	promoted and no milestone exists, which fails consistency rule CP-C03.
20. Produce the ADAPT Startup / Initialization Report.
21. Stop.

Do not pause between path resolution and scaffold creation merely to request approval.

## Canonical Starters

`CANONICAL_STARTERS/` is the authoritative source for all starter file content.

### Copy, Do Not Generate

The scaffold must copy each required file from `CANONICAL_STARTERS/` into `{{ADAPT_INSTANCE_PATH}}/ADAPT` (or directly into the supplied path if it already names the inner ADAPT directory), rather than generating starter content from AI training knowledge.

The canonical starters mirror the ADAPT instance folder structure. For each required file listed in `SCAFFOLD_OUTPUT_CONTRACT.md`, locate the corresponding file in `CANONICAL_STARTERS/` and copy it to the target path.

### Populate After Copying

After copying, populate project-specific values (project name, team names, requirements, decisions) into the copied files using only:

* The resolved project document (promoted or pending promotion)
* Other explicitly accepted source truth
* Discovered facts (for MODE_A only)

Do not invent project-specific content to fill placeholders. Record unfilled facts as open questions or gaps.

#### Instance-level token substitution

Four tokens carry one value for the whole instance. Substitute them across every
copied file, but **only where they appear in a header line** — a line in the first
eight lines of the file matching `^[A-Z_]+:` — under the header key named below.

| Token | Header key | Value |
|---|---|---|
| `{{PROJECT_NAME}}` | `PROJECT:` | the resolved project name |
| `{{ADAPT_VERSION}}` | `VERSION:` | the `Current Framework Version` declared in `FRAMEWORK_LEARNING_REGISTER.md` at the root of the framework source being scaffolded, copied exactly. Never invent, infer, increment, or derive it from a git commit or a date. If it cannot be read, STOP. |
| `{{INITIALIZATION_DATE}}` | `INITIALIZED:` | the scaffold date, ISO 8601 |
| `{{DATE}}` | `LAST_UPDATED:` only | the scaffold date, ISO 8601 |

Outside the explicit population steps (including the complete control-plane table
and RoutingMode in the scope guardrail), every other token is template-level and
must survive untouched. This includes instructional occurrences of
occurrences of `{{PROJECT_NAME}}` and `{{DATE}}` in body text, tables, and examples.

Template-level tokens also appear in header lines. These four are the most common and
are **not** substituted at scaffold time:

| Token | Populated when |
|---|---|
| `{{ACTIVE_MILESTONE}}` | a milestone is opened |
| `{{SOURCE_TRUTH_VERSION}}` | source truth is promoted |
| `{{WORKCELL_ID}}` | a workcell is onboarded |
| `{{IDENTITY}}` | a workcell is onboarded |

A surviving placeholder is a POPULATION_FAILURE only in an explicitly populated
live field or an instance-level header.
Template-level placeholders surviving scaffold completion are the expected state. The
completion scan must report the two categories separately.

`{{DATE}}` appears under eight different header keys. Substitute it under
`LAST_UPDATED:` only. Under `RAISED_DATE:`, `RESOLVED_DATE:`, `ASSIGNED_DATE:`,
`ASSESSED_DATE:`, `DATE_REQUESTED:`, `DATE_ASSEMBLED:` and `DATE:` it refers to a
record that does not exist yet. Leave those.

**Exclude these two files from substitution entirely:**

- `00_FRAMEWORK/ARTIFACT_STANDARDS.md` — documents the placeholder convention and
	lists tokens as correctness examples. Substituting corrupts the file that defines
	the rule.
- `15_COMMANDS_AND_DRIVERS/COMMAND_SYNTAX.md` — same reason.

Never substitute `{{DOUBLE_BRACE}}`. It names the convention, it is not a value.

After substitution, the placeholder scan below reports only template-level tokens,
which is the expected state. Report the count.

Before completing scaffolding, scan every created file for surviving {{...}}
placeholders. Report the count in two categories, separately:

  instance-level survivors — a POPULATION_FAILURE. Report each by path and token.
  template-level survivors — the expected state. Report the count only.

Do not report a single combined number. A combined count cannot be interpreted, and a
run that reports one has not performed this scan.

### Missing Canonical Starters

If a canonical starter file does not exist for a required output file, the AI must:

1. Report `CANONICAL_STARTER_MISSING: {{FILE_NAME}}` for that file in the initialization report.
2. Generate a best-effort version of the file using ADAPT governance principles.
3. Mark the generated file with `GENERATED_FROM_TRAINING_KNOWLEDGE: YES` at the top.
4. Flag it clearly in the initialization report.

## Tooling Distribution (mandatory for NEW instances)

The scaffold is agent-guided; there is no hidden general-purpose generator.
After copying canonical starters, the scaffold agent MUST run:

```text
python {{ADAPT_FRAMEWORK_PATH}}/VALIDATION/distribute_tools.py --framework {{ADAPT_FRAMEWORK_PATH}} --instance {{ADAPT_INSTANCE_PATH}}/ADAPT
python {{ADAPT_FRAMEWORK_PATH}}/VALIDATION/distribute_tools.py --framework {{ADAPT_FRAMEWORK_PATH}} --instance {{ADAPT_INSTANCE_PATH}}/ADAPT --verify
```

Quote all paths in the calling shell. If the resolved instance path already names
the inner ADAPT directory, pass that directory directly. This narrow copy step
creates only its TOOLS directory and verifies manifest hashes; it does not populate
source truth, approve anything or scaffold the governance tree. Python 3.9+ is
required; inability to copy/verify tooling is a scaffold failure, not a silent skip.
TOOLS is copied verbatim: never substitute framework/template tokens in tool code
or documentation. Source manifest and distributed file hashes must agree.

During recovery of an EXISTING instance, do not add or overwrite TOOLS. A tooling
upgrade is an explicitly authorized framework upgrade/backport, not recovery.
The startup report records tool file count and distribution verification result.

## Source Truth Extraction

Scaffold extraction is CANDIDATE_TRUTH pending promotion, not Gate 1 approval.
Preserve NONE / INITIALIZED at completion. The startup evidence records the source
framework version/reference and frozen governing contract SHA256 hashes for the
Director's later eligibility verification under SOURCE_AUTHORITY_POLICY.md,
First-Promotion Initial Context Basis. Scaffold creation does not begin an attempt,
promote a source, grant implementation authority or create a context pack.

Extract:

* project name
* domain summary
* users
* workflows
* business rules
* requirements
* acceptance criteria
* risks
* non-goals
* open questions
* suggested modules
* validation concerns
* integration concerns

Do not invent missing content.

## Missing Details Handling

Missing language, framework, database, auth, deployment, team names, and first milestone must not block scaffolding.

Record unresolved details in:

* `OPEN_QUESTIONS.md`
* `GAP_REGISTER.md`

Use:

* `GAP-T10 Decision Gap`
* `GAP-T11 Context Gap`

## Project Source Mutation Policy

Project source mutation defaults to `NO`.

If the user did not explicitly request project shell creation or project source mutation:

* do not modify `{{PROJECT_FOLDER_PATH}}`
* write normal scaffold output only to `{{ADAPT_INSTANCE_PATH}}`
* report project files touched as none

Project shell creation is allowed only when project source mutation is explicitly authorized as `YES` and its scope is clear.

If authorized, shell creation must be limited to:

* solution shell
* frontend shell
* backend shell
* README files
* placeholder contracts
* placeholder docs
* placeholder test folders

Forbidden:

* real business logic
* secrets
* cloud resources
* production auth
* database persistence
* payment/chat/GPS/live-map implementation

Do not edit existing project source unless the explicit authorization covers those files.

## Valid Stop Conditions

Stop only when safe execution is not possible:

* `START_HERE.md` cannot be found.
* `SCAFFOLD_WORKFLOW_AGENT.md`, `SCAFFOLD_OUTPUT_CONTRACT.md`, or `WORKCELL_ONBOARDING_CONTRACT.md` cannot be found.
* No project document can be resolved.
* Multiple project document candidates exist and no obvious choice exists.
* The ADAPT instance path points inside the project folder without an explicit user-provided path.
* The ADAPT instance path points inside the framework folder without an explicit user-provided path.
* The ADAPT instance target contains unrelated files.
* Project source mutation is requested but its scope is unclear.
* Destructive overwrite, deletion, or archival is required.
* The project document cannot be read.
* Required scaffold output cannot be written.

Do not stop merely to ask for approval to create scaffold files inside `{{ADAPT_INSTANCE_PATH}}`.

## Required Final Report

After scaffolding, output:

# ADAPT Startup / Initialization Report

Include:

* framework source path
* project folder path
* ADAPT instance path
* project document path
* inferred project name
* deployment mode detected (MODE_A_EXISTING_SOLUTION or MODE_B_REQUIREMENTS_ONLY)
* source truth status
* canonical starters used (count)
* canonical starters missing (list, if any)
* folders created
* files created
* project files touched
* open questions recorded
* gaps created
* blockers created
* next recommended command
* status

Next recommended command:

`Run Director intake`

When DIRECTOR_IDENTITY.md still has its initial human-owner placeholder, that
command performs only ACTION_PROMPT_DIRECTOR.md's Initial Director designation
stage, using explicit Human Owner designation supplied with the invocation.
Scaffolding must not infer or prepopulate that human identity. The stage records
identity and designation evidence, preserves INITIALIZED / source truth NONE,
and stops before a separately approved first promotion. No development workcell
or ordinary context pack is required to establish this initial accountability.

## Stop Rule

After scaffold initialization and the final report, stop.
