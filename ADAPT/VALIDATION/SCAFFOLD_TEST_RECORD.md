# Scaffold Test Record

STATUS: PENDING
VERSION: 1.0

## Purpose

Defines the expected test procedure for validating that executing `Read and Execute START_HERE.md` against the existing `example-project` solution produces a correct and complete ADAPT instance.

---

## Test Definition

### Test Command

```
Read and Execute START_HERE.md
```

### Test Inputs

| Input | Value |
|-------|-------|
| Project subject | example-project |
| Deployment mode | MODE_A_EXISTING_SOLUTION |
| ADAPT instance path | ../example-project_ADAPT_INSTANCE/ (sibling of framework folder) |
| Project source mutation | NO |
| Canonical starters path | CANONICAL_STARTERS/ |

### Expected Outputs

- Full ADAPT instance folder structure (16 folders: 00_FRAMEWORK through 15_COMMANDS_AND_DRIVERS)
- TOOLS distribution included automatically, matching its manifest SHA256 hashes
- All required starter files populated from canonical starters (CANONICAL_STARTERS/)
- Existing-solution facts discovered from example-project into:
  - OPEN_QUESTIONS.md
  - BUSINESS_ITEMS.md
- Discovery gaps recorded in GAP_REGISTER.md and OPEN_QUESTIONS.md when repository facts cannot be established
- No existing application source code or configuration in example-project mutated during scaffold
- No real person-owned workcells created (03_WORKCELLS/ contains only README.md and ROLE_WORKCELL_BLUEPRINTS.md)
- ADAPT Startup / Initialization Report produced
- PROJECT_CONTROL_PLANE.md records ExecutionReadiness = NEEDS_PLANNING and CurrentPhase = INITIALIZED

### Pass Criteria

| Criterion | How to Verify |
|-----------|--------------|
| Every file listed in SCAFFOLD_OUTPUT_CONTRACT.md exists in the output | List all files in example-project_ADAPT_INSTANCE/ and compare against contract |
| Tool distribution is runnable and complete | Run the mandatory distribute_tools.py copy/verify step; run generated TOOLS/adapt.py state and doctor; tools have no development-repository dependency |
| Explicitly populated live fields contain no placeholders | Check all 21 control-plane values and RoutingMode; instructional examples are excluded |
| Instance-level header tokens are populated; template tokens are preserved | Apply header-key substitution in SCAFFOLD_WORKFLOW_AGENT.md; report the two categories separately, never fail solely on preserved template tokens |
| Generated `VERSION:` headers carry the source framework's declared version | Read `Current Framework Version` in the framework-root FRAMEWORK_LEARNING_REGISTER.md; confirm every generated `VERSION:` header substituted from the ADAPT_VERSION token carries exactly that value |
| Discovered facts and gaps are recorded | Review BUSINESS_ITEMS.md, OPEN_QUESTIONS.md, and GAP_REGISTER.md for discovery results |
| No existing application source code or configuration was mutated during scaffold | Compare example-project source files and configuration before and after scaffold |
| No person-owned workcells exist | 03_WORKCELLS/ contains only README.md and ROLE_WORKCELL_BLUEPRINTS.md |
| PROJECT_CONTROL_PLANE.md has DeploymentMode = MODE_A_EXISTING_SOLUTION | Read PROJECT_CONTROL_PLANE.md DeploymentMode field |
| Deployment mode is recorded in PROJECT_CONTROL_PLANE.md | Verify DeploymentMode field is present and set |
| PROJECT_CONTROL_PLANE.md has initial scaffold readiness | Verify ExecutionReadiness = NEEDS_PLANNING and CurrentPhase = INITIALIZED |
| ADAPT Startup / Initialization Report was produced | Report must be present in the scaffold output or conversation transcript |

---

## Test Execution Record

The original full agent-led example-project test below remains pending. Tooling
v1 mechanical fresh-scaffold/distribution and standalone execution results are
recorded separately in TOOLING_V1_RELEASE.md with raw focused runner output.
Those results do not certify arbitrary agent-led source discovery/extraction.

| Field | Value |
|-------|-------|
| Last test run | NOT_RUN |
| Last test result | PENDING |
| Tester | — |
| Notes | No successful validation of the sanitized public framework has been established. Supporting historical evidence is unavailable; prior project-specific scaffold runs are not evidence of validation for this public framework. |

---

## Known Pre-Conditions

Before running this test:

1. Verify `CANONICAL_STARTERS/` is populated with all required starter files
2. Verify `DEPLOYMENT_MODES.md` exists and defines MODE_A
3. Verify the `example-project` repository exists with source files present
4. Verify no ADAPT instance is in place and the target path `../example-project_ADAPT_INSTANCE/` does not already exist (or is empty)

---

## Failure Classification

| Failure Type | Classification |
|-------------|---------------|
| Missing required file | CONTRACT_VIOLATION |
| Unreplaced required live field or instance-level header token | POPULATION_FAILURE |
| Application source code created | MUTATION_VIOLATION |
| Real workcell created without onboarding command | WORKCELL_VIOLATION |
| DeploymentMode not recorded | CONTROL_PLANE_FAILURE |
| No gap recorded for missing technical decision | GAP_REGISTER_FAILURE |
| Canonical starter not used (file generated from AI knowledge) | CANONICAL_STARTER_BYPASS |

---

## Bounded first-promotion acceptance

The separate MODE_B synthetic case for local version candidate ADAPT-FW-0003
is documented in BOOTSTRAP_V2_REPORT.md with raw BOOTSTRAP_V2_ACCEPTANCE.json.
It exercises current canonical copying, prescribed population, official tooling
distribution, Director first promotion, Context Steward assembly and ordinary
context/reuse rejection as separate agent-guided stages. Synthetic approval is
test data only. Structural tests and Tooling v1 regressions are recorded separately
in BOOTSTRAP_V2_TESTS.json. These results do not close the original MODE_A
example-project test above, certify arbitrary extraction, certify a framework
release, or count as a successful self-hosted development lane.

## Related Files

- `START_HERE.md` — entry point
- `SCAFFOLD_WORKFLOW_AGENT.md` — scaffold workflow
- `SCAFFOLD_OUTPUT_CONTRACT.md` — required output files
- `DEPLOYMENT_MODES.md` — mode definitions
- `CANONICAL_STARTERS/` — authoritative starter content
