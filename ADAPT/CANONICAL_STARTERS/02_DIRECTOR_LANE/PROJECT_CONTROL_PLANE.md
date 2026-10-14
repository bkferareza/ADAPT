# Project Control Plane

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
LAST_UPDATED: {{DATE}}
UPDATED_BY: Director Lane

---

## Control Plane State

| Field | Value |
|-------|-------|
| ProjectName | {{PROJECT_NAME}} |
| ProjectType | {{PROJECT_TYPE}} |
| DeploymentMode | {{DEPLOYMENT_MODE}} |
| RoutingMode | {{ROUTING_MODE}} |
| InitializationMode | {{INITIALIZATION_MODE}} |
| SourceTruthVersion | {{SOURCE_TRUTH_VERSION}} |
| ActiveMilestone | {{ACTIVE_MILESTONE}} |
| ActiveCycle | {{ACTIVE_CYCLE}} |
| ActiveHandoff | {{ACTIVE_HANDOFF_ID}} |
| CurrentAuthority | {{CURRENT_AUTHORITY}} |
| ExecutionReadiness | {{EXECUTION_READINESS}} |
| CurrentPhase | {{CURRENT_PHASE}} |
| ActiveWorkcell | {{ACTIVE_WORKCELL}} |
| Blocked | {{BLOCKED}} |
| ActiveBlockers | {{ACTIVE_BLOCKERS}} |
| ActiveGaps | {{ACTIVE_GAPS}} |
| LastAction | {{LAST_ACTION}} |
| LastContextDelta | {{LAST_CONTEXT_DELTA}} |
| NextExpectedAction | {{NEXT_EXPECTED_ACTION}} |
| LastConsolidatedAt | {{LAST_CONSOLIDATED_AT}} |
| Notes | {{NOTES}} |

---

## Allowed Values

### DeploymentMode
- MODE_A_EXISTING_SOLUTION
- MODE_B_REQUIREMENTS_ONLY

### RoutingMode
- PROTECTED_DEFAULT
- DUAL_WRITE

### ExecutionReadiness
- READY
- NOT_READY
- BLOCKED
- NEEDS_CONTEXT
- NEEDS_APPROVAL
- NEEDS_PLANNING
- NEEDS_ONBOARDING

### CurrentPhase
- INITIALIZED
- SOURCE_TRUTH_LOADING
- SOURCE_TRUTH_READY
- ONBOARDING
- PLANNING
- READY_FOR_ASSIGNMENT
- EXECUTION
- INTEGRATION
- QA_VALIDATION
- CHALLENGE_REVIEW
- CONSOLIDATION
- JANITOR_PASS
- READY_FOR_NEXT_CYCLE
- BLOCKED

---

## Notes

The control plane is the single source of current project state. It must be updated by the Director Lane at the end of every Director action and after every consolidation cycle. All other lanes read the control plane; only the Director writes to it except that a workcell may discharge its own active handoff, clear `ActiveHandoff`, and set `CurrentPhase = READY_FOR_ASSIGNMENT` after completing its bounded action.
