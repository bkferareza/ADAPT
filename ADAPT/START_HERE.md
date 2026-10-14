# START HERE - ADAPT Framework Launcher

When an AI tool is told:

`Read and Execute START_HERE.md`

it must start here and execute the scaffold workflow.

This repository is `ADAPT_FRAMEWORK_SOURCE`.

Do not treat this repository as the project-specific ADAPT instance.

## Default Folder Model

```text
/workspace/
|-- ADAPT/
|-- PROJECT_FOLDER/
`-- ADAPT_INSTANCE/
```

The project folder and ADAPT instance should normally be siblings of the ADAPT framework folder.

Default behavior:

`FULL_EXTERNAL_ADAPT_INSTANCE_SCAFFOLD`

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

Creating folders and files inside `{{ADAPT_INSTANCE_PATH}}` is part of the authorized scaffold operation.

## No Wizard Rule

ADAPT scaffolding is not an installation wizard.

The command `Read and Execute START_HERE.md` is sufficient authorization to scaffold the external ADAPT instance.

The AI must not ask for a second approval before creating scaffold files inside `{{ADAPT_INSTANCE_PATH}}`.

The AI should infer safe defaults, proceed with scaffolding, record unresolved details as open questions/gaps, and stop with an initialization report.

Approval-style prompts are allowed only for unsafe conditions such as destructive overwrite, ambiguous paths, project source mutation, or unreadable/missing project documents.

## Path Inference Rules

Infer safe defaults before asking the user for paths.

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

Do not treat ADAPT framework contracts, launcher files, templates, guardrails, commands, reports, or other framework documentation as project documents.

If exactly one likely project document is found, use it.

If multiple likely documents are found, use the most project-specific document only when the choice is obvious. Otherwise, stop and ask only for `{{PROJECT_DOCUMENT_PATH}}`.

### Project Folder Path

If `{{PROJECT_FOLDER_PATH}}` is not provided, create or use a sibling folder beside the ADAPT framework folder.

Use:

`{{ADAPT_FRAMEWORK_PARENT}}/{{PROJECT_NAME}}_PROJECT`

If the project name cannot yet be inferred, use:

`{{ADAPT_FRAMEWORK_PARENT}}/PROJECT_FOLDER`

Do not create the project folder inside `ADAPT_FRAMEWORK` unless it already exists there and the user explicitly provided that path.

### ADAPT Instance Path

If `{{ADAPT_INSTANCE_PATH}}` is not provided, create or use a sibling folder beside the ADAPT framework folder.

Use:

`{{ADAPT_FRAMEWORK_PARENT}}/{{PROJECT_NAME}}_ADAPT_INSTANCE`

If the project name cannot yet be inferred, use:

`{{ADAPT_FRAMEWORK_PARENT}}/ADAPT_INSTANCE`

Do not create the ADAPT instance inside `PROJECT_FOLDER`.
Do not create the ADAPT instance inside `ADAPT_FRAMEWORK` unless the user explicitly provided that path.

## Target Folder Handling

If `{{ADAPT_INSTANCE_PATH}}` does not exist, create it and scaffold the full ADAPT instance.

If it exists and is empty, scaffold into it.

If it already contains an ADAPT instance, recover the existing state and do not overwrite blindly.

If it contains unrelated files, stop and ask for a different ADAPT instance path or whether to create a subfolder.

## Project Source Mutation Default

Project source mutation defaults to:

`NO`

Unless the user explicitly requests project shell creation or project source mutation, do not modify `{{PROJECT_FOLDER_PATH}}`.

Normal scaffold execution writes only to `{{ADAPT_INSTANCE_PATH}}`.

Do not write project-specific ADAPT state into `ADAPT_FRAMEWORK`.
Do not write ADAPT state into `PROJECT_FOLDER` by default.
Do not create application source code as part of normal scaffolding.

## Execution Order

1. Resolve available paths and infer safe defaults.
2. Read `START_HERE.md`.
3. Read `SCAFFOLD_WORKFLOW_AGENT.md`.
4. Read `SCAFFOLD_OUTPUT_CONTRACT.md`.
5. Read `WORKCELL_ONBOARDING_CONTRACT.md`.
6. Read the resolved project document.
7. Create or recover the full external ADAPT instance at `{{ADAPT_INSTANCE_PATH}}`.
8. Record unresolved details as open questions and gaps.
9. Output the ADAPT Startup / Initialization Report.
10. Stop.

## Valid Stop Conditions

Stop only when safe execution is not possible, including when:

* `START_HERE.md` cannot be found.
* Required scaffold contract files cannot be found.
* No project document can be resolved.
* Multiple project document candidates exist and no obvious choice exists.
* The ADAPT instance path points inside the project folder without an explicit user-provided path.
* The ADAPT instance path points inside the framework folder without an explicit user-provided path.
* The ADAPT instance path contains unrelated files.
* Project source mutation is requested but its scope is unclear.
* Destructive overwrite, deletion, or archival is required.
* The project document cannot be read.
* Required scaffold output cannot be written.

Do not stop merely to ask for scaffold approval.

## Required Final Report

After scaffolding, output:

# ADAPT Startup / Initialization Report

Include:

* framework source path
* project folder path
* ADAPT instance path
* project document path
* inferred project name
* source truth status
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

After the report, stop.

---

## Integrated Read-only Tooling

New scaffolds automatically include `TOOLS/`, copied and hash-verified under
`SCAFFOLD_WORKFLOW_AGENT.md`. Python 3.9+ is required for distribution and operator
commands; Git is needed only for `evidence`. Tool use is optional and never grants
execution authority. See `TOOLS/README.md`. Existing instances are not migrated.

## Framework Maintainer Orientation

Reference for whoever maintains this framework. This section is not part of scaffold execution and changes nothing above.

- **Framework version:** `Current Framework Version` in `FRAMEWORK_LEARNING_REGISTER.md` at this root. Scaffolding copies it into each instance's `VERSION:` headers.
- **Normative content:** the contracts at this root (`START_HERE.md`, `SCAFFOLD_WORKFLOW_AGENT.md`, `SCAFFOLD_OUTPUT_CONTRACT.md`, `WORKCELL_ONBOARDING_CONTRACT.md`, `DEPLOYMENT_MODES.md`) and the canonical starters in `CANONICAL_STARTERS/`, which every instance copies. `VALIDATION/SCAFFOLD_TEST_RECORD.md` defines the scaffold test.
- **Supporting content:** `FRAMEWORK_LEARNING_REGISTER.md` and `MEASUREMENT_DEFINITIONS.md` are framework documentation. They are never copied into an instance and are never project documents.
- **Framework and instance boundary:** this folder is the framework source and is never written by a scaffold. Each instance is a separate sibling folder holding its own solution truth and state.
- **Authority for a rule:** governance rules are in `CANONICAL_STARTERS/00_FRAMEWORK/GOVERNANCE_RULES.md`; what counts as truth is in `CANONICAL_STARTERS/00_FRAMEWORK/SOURCE_AUTHORITY_POLICY.md`.
- **Changing the framework:** only the Framework Maintainer authorizes a change (`GOVERNANCE_RULES.md`, Rule 14). Record it as a candidate in `FRAMEWORK_LEARNING_REGISTER.md` before promoting it.
- **Existing instances:** promoted changes reach future scaffolds only. Existing instances are never migrated automatically; an upgrade or backport is a separate, deliberate decision.
