# Operator Dispatch Binding (section to include in the ACTIVE handoff)

## Operator Dispatch Binding

| Field | Value |
|-------|-------|
| Command | Run atomic handoff dispatch |
| WorkItem | {{BI-ID}} |
| ScopeContract | {{SCOPE_CONTRACT_PATH}} |
| ScopeDecision | {{SCOPE_DEC_ID}} |
| MilestoneDecision | {{MILESTONE_DEC_ID}} |
| ApprovalReference | {{APPROVAL_RECORD_PATH}} |
| ActionPrompt | {{MEMBER_ACTION_PROMPT_PATH}} |
| MutationPaths | {{EXPLICIT_PATHS_OR_NONE}} |
| SourceTruthDocument | {{SOURCE_DOCUMENT_PATH}} |
| ContextPack | {{CONTEXT_PACK_PATH}} |
| EmittingBlueprint | {{EMITTING_BLUEPRINT_PATH}} |

These fields reference existing records; they do not grant authority. Populate
only from the Director's approved handoff and existing decisions. See
`15_COMMANDS_AND_DRIVERS/TOOLING_DECISION_CONTRACT.md` for fail-closed checks.
