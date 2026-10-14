# Deployment Modes

STATUS: DRAFT
VERSION: 1.0

## Purpose

Defines exactly two scaffold deployment modes. The mode determines how the scaffold resolves source truth, what pre-scaffold steps run, and what goes into `OPEN_QUESTIONS.md` and `GAP_REGISTER.md`. Both modes produce the same ADAPT instance folder structure using the same canonical starters.

---

## Mode Detection Logic

```
If {{PROJECT_FOLDER_PATH}} exists AND contains application source files
(code files, solution files, build configs, or existing documentation):
→ MODE_A: EXISTING_SOLUTION

If {{PROJECT_FOLDER_PATH}} does not exist, OR contains no source files,
OR contains only a project document (no application source):
→ MODE_B: REQUIREMENTS_ONLY
```

The detected mode must be recorded in `PROJECT_CONTROL_PLANE.md` under `DeploymentMode`.

---

## MODE_A: EXISTING_SOLUTION

### Trigger

Triggered when `{{PROJECT_FOLDER_PATH}}` exists and contains application source files — code files, solution files (e.g., `.sln`, `package.json`, `pom.xml`), build configs, or existing project documentation.

### Pre-Scaffold Behavior

Run a read-only discovery pass before creating any ADAPT artifacts:

1. **Discover the codebase:**
   - Primary language(s)
   - Platform and framework(s)
   - Build system and tooling
   - Test setup (presence of test folders, test configs)
   - Folder structure and naming conventions
   - Existing documentation locations
   - Existing requirements references or ticket links

2. **Record discovered facts:**
   - Write all discovered facts to `OPEN_QUESTIONS.md` and `BUSINESS_ITEMS.md` as candidate truth — not accepted truth.
   - Candidate truth is promoted to accepted truth only when the Director runs intake.
   - Behavior read from code, configuration, or runtime is recorded as OBSERVED_EVIDENCE;
     statements ADAPT derives from it are CANDIDATE_TRUTH. Neither governs work until
     promoted. See SOURCE_AUTHORITY_POLICY.md, Truth Classes.
   - Validation mechanisms observed in step 1 — test runners, test configuration, build
     or lint checks, runtime environments — are recorded in `OPEN_QUESTIONS.md` as
     OBSERVED_EVIDENCE candidates for the Director's oracle declaration. Discovery does
     not populate the Validation Oracle in `05_VALIDATION/QA_STRATEGY.md` and does not
     change its Oracle Declaration Status, which stays UNDECLARED until the Director
     declares.

3. **Set the routing mode:**
    - `RoutingMode` is an operator input. There is no default. If it was not supplied,
       STOP and ask before scaffolding.
    - Record it in `PROJECT_CONTROL_PLANE.md` under `RoutingMode`.
    - Populate `{{ROUTING_MODE}}` in `07_GUARDRAILS/SCOPE_GUARDRAIL.md` with the same
       value. The guardrail already contains both routing sections; only the value is
       written. Do not compose, rewrite, or summarise that section.

4. **Check for an existing ADAPT instance:**
   - If an ADAPT instance already exists at `{{ADAPT_INSTANCE_PATH}}`, **recover state** — do not overwrite.
   - Recovery preserves all existing ADAPT state; only missing files are created from canonical starters.

5. **Complete discovery before scaffold:**
   - Only after the read-only discovery pass is complete, proceed with scaffold using canonical starters.

### Source Truth Population

- Populate `REQUIREMENTS_INDEX.md` and `BUSINESS_ITEMS.md` from discovered documentation, existing tickets, or any provided project document.
- Populate `OPEN_QUESTIONS.md` with every item that cannot be determined from discovery.
- Record everything unresolved as `GAP-T11 Context Gap` or `GAP-T10 Decision Gap` in `GAP_REGISTER.md`.

### Forbidden During MODE_A

- Mutating any existing source file without explicit human approval
- Assuming requirements from code structure alone (code is not source truth)
- Creating workcells before onboarding commands are given
- Overwriting an existing ADAPT instance without explicit recovery confirmation

### Control Plane Entry

```
DeploymentMode: MODE_A_EXISTING_SOLUTION
```

---

## MODE_B: REQUIREMENTS_ONLY

### Trigger

Triggered when `{{PROJECT_FOLDER_PATH}}` does not exist, or contains no application source code, or only a project document (`.docx`, `.md`, `.pdf`, `.txt`) is provided as input with no existing codebase.

### Pre-Scaffold Behavior

1. **Read the project document:**
   - The resolved `{{PROJECT_DOCUMENT_PATH}}` is the sole source of truth input.
   - If no document can be resolved, stop and request `{{PROJECT_DOCUMENT_PATH}}`.

2. **Extract all available source truth from the document:**
   - Project name and domain
   - Target users and user roles
   - Workflows and user flows
   - Business rules and constraints
   - Requirements and features
   - Acceptance criteria
   - Risks and non-goals
   - Open questions and known unknowns
   - Suggested modules or components
   - Integration concerns
   - Validation concerns

3. **Do not invent content:**
   - If a fact is not in the document, do not infer it from the project name or general knowledge.
   - Every missing fact becomes an open question or gap.

4. **Record missing technical decisions:**
   - Language, framework, database, authentication, deployment model — any technical decision not in the document must be recorded as `GAP-T10 Decision Gap` in `GAP_REGISTER.md` and `OPEN_QUESTIONS.md`.

### Source Truth Population

- Populate `REQUIREMENTS_INDEX.md`, `BUSINESS_ITEMS.md`, and `ACCEPTANCE_CRITERIA.md` directly from the project document.
- Do not populate implementation-layer artifacts (`API_CONTRACTS.md`, `PIPELINE_STATUS.md`, `UI_BE_CONTRACTS.md`, etc.) with invented content — leave them at their canonical starter state with `STATUS: DRAFT`.
- The `SOURCE_TRUTH_VERSION_LOG.md` should note the document used and mark it as pending Director promotion.

### Forbidden During MODE_B

- Creating application source code or shell projects unless explicitly authorized by the user
- Treating document section headings as accepted requirements without extraction and review
- Populating implementation contracts from inferred assumptions
- Creating workcells before onboarding commands are given

### Control Plane Entry

```
DeploymentMode: MODE_B_REQUIREMENTS_ONLY
```

---

## Common Rules for Both Modes

Both modes must:

1. **Use canonical starters** — all files not populated from source truth must be copied from `CANONICAL_STARTERS/` rather than generated from AI training knowledge.

2. **Produce the same ADAPT instance folder structure** — 16 governance folders plus TOOLS, all required files per `SCAFFOLD_OUTPUT_CONTRACT.md`. New-instance creation automatically copies and verifies the tooling distribution; recovery never adds or overwrites tooling without an explicit upgrade decision.

3. **End with the same ADAPT Startup / Initialization Report** — including deployment mode, paths, files created, open questions, gaps, and next recommended command.

4. **Record the deployment mode in `PROJECT_CONTROL_PLANE.md`** — the `DeploymentMode` field must be set before the scaffold is considered complete.

5. **Not create workcells** — only `README.md` and `ROLE_WORKCELL_BLUEPRINTS.md` go in `03_WORKCELLS/` at scaffold time.

6. **Report `CANONICAL_STARTER_MISSING` for any required output file whose canonical starter does not exist** — generate a best-effort version and flag it clearly in the initialization report.

---

## References

- `START_HERE.md` — path inference and mode detection trigger
- `SCAFFOLD_WORKFLOW_AGENT.md` — full scaffold workflow including mode handling
- `SCAFFOLD_OUTPUT_CONTRACT.md` — required output files for both modes
- `CANONICAL_STARTERS/` — authoritative starter file content
