# FW-0007 actual Codex conversation acceptance

Status: PASS for the actual MODE_B operator conversation on 2026-11-03. The
operator requested details and a CP terminology explanation, approved naturally,
received the validated result and confirmed "next step clear". Evidence is in
`.adapt-local/maintenance/fw0007-chat-first-20261103/actual-mode-b-acceptance/`.
MODE_A human usability remains NOT_TESTED. This is bounded operator acceptance,
not independent QA or release approval. The MODE_B decision is consumed; never
replay it. The earlier console trial remains supporting technical evidence only.

In ordinary Codex chat in D:\Project\ADAPT, send only:

> Start the FW-0007 disposable chat acceptance test.

ADAPT must drive the remaining interaction. The operator should need no shell
commands, JSON, hashes, evidence-file reading or prompt edits. The test changes
only a disposable sample, using explicitly simulated Director/Maintainer
capacities; it grants no authority over a real instance.

## Instructions for the hosting ADAPT assistant

Read the prepared fixture index at
`.adapt-local/maintenance/fw0007-chat-first-20261103/conversation-fixtures.json`.
Default to MODE_B; MODE_A is also prepared and may be tested in another session.
Read the selected session JSON and its instance's installed
`15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_MASTER.md`, the human approval gates and
existing maintenance contracts. If the fixtures no longer match current source,
prepare a fresh one with the test-only `prepare_conversation_fixture(mode)` in
`TOOLS/tests/test_recovery_human_interaction.py`. Never refresh a consumed action
or change its evidence to bypass a STOP. No protected instance is a fallback.

Load that instance's `VALIDATION/recovery_operational.py`. Construct the existing
MaintenanceEntry with the saved installation, ledger and `synthetic=True`. Call
`interact(saved_request)` to start the normal bounded maintenance action. Explain
the actual review in the conversation, including the displaced sample register
rows, preserved history, unchanged blocker, write risk, simulated capacities and
exact decision question. STOP this turn and await the actual operator response.
Do not feed a simulated response or run the console harness.

On a later turn reconstruct the same entry with the same session and installation.
Pass the actual response to `interact(response=..., human='Synthetic Director',
source_reference=...)`. This human field is the explicitly simulated fixture
capacity, not authenticated real identity. Obtain original response provenance
from the actual interaction and retain its original text/reference; do not
fabricate provenance. Interpret natural language only under the installed master
contract. Show details and clarification must preserve the pending decision.
Rejection must leave the instance unchanged. Approval permits only the exact
sample structural repair; it never permits recovery context assembly.

After approval inspect the result and audit its claim with the existing entry.
Explain the actual mutation, validation, remaining blocker, next separate action
and its approval requirement in chat. STOP. Do not execute the recommendation.
Keep the technical records available without making the human read them.

Ask for brief operator feedback after the action boundary: could they understand
the proposal, decide naturally, understand the outcome and identify the next step
without opening files or consulting another AI? Retain the actual transcript,
feedback, date, selected mode, details/clarification turns, assistance, prompt
edits, technical fields typed and any difficulty outside the instance in its
fixture directory. Do not claim successful delivery merely from adapter text.
Do not mark HUMAN_USABILITY PASS until an actual operator completes the trial
and their recorded feedback supports acceptance. Record failure candidly.
Independent identity authentication and independent QA remain outside this trial.

The optional legacy console harness is still available as `manual_session()` in
the existing test module. It is not a substitute for this ordinary Codex trial.
