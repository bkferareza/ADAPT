# Role Model

STATUS: DRAFT
VERSION: {{ADAPT_VERSION}}
PROJECT: {{PROJECT_NAME}}

## Purpose

Defines all roles available in this ADAPT instance, their lane, authority scope, and mutation boundaries.

## Roles

### Director
- **Lane:** Director Lane (02_DIRECTOR_LANE/)
- **Authority:** Intake, routing, source-truth promotion, assignment, gap classification, blocker routing, certification
- **Mutation Scope:** ADAPT control artifacts only (control plane, registers, logs) — no application source code
- **Cannot:** Mutate application source, produce QA signoff, bypass evidence gates

### Backend Developer
- **Lane:** Backend Workcell (03_WORKCELLS/BACKEND_{{IDENTITY}}/)
- **Authority:** Backend implementation within assigned scope
- **Mutation Scope:** Backend source files, backend tests, backend API definitions — as assigned
- **Cannot:** Mutate frontend files, produce QA signoff, exceed assigned scope

### Frontend Developer
- **Lane:** Frontend Workcell (03_WORKCELLS/FRONTEND_{{IDENTITY}}/)
- **Authority:** Frontend implementation within assigned scope
- **Mutation Scope:** Frontend source files, frontend tests, frontend UI definitions — as assigned
- **Cannot:** Mutate backend files, produce QA signoff, exceed assigned scope

### Integrator
- **Lane:** Integration Lane (04_INTEGRATION/)
- **Authority:** Contract reconciliation, API/UI binding verification, merge readiness assessment
- **Mutation Scope:** Integration contracts, pipeline config — as assigned; must not silently rewrite feature logic
- **Cannot:** Produce QA signoff, act as Director approval, absorb unowned work without gap classification

### QA Engineer
- **Lane:** QA Lane (05_VALIDATION/)
- **Authority:** Independent validation against accepted source truth and acceptance criteria
- **Mutation Scope:** Test artifacts only — no application source code mutation
- **Cannot:** Mutate application source, treat developer self-validation as QA signoff, validate without acceptance criteria

### Planner
- **Lane:** Planning Lane (13_PLANNING/)
- **Authority:** Milestone analysis, work slicing, roadmap recommendation
- **Mutation Scope:** Planning artifacts only — no implementation or QA artifacts
- **Cannot:** Approve its own plan (Director approves), mutate code, over-assign work

### Context Steward
- **Lane:** Context Economy (10_CONTEXT_ECONOMY/)
- **Authority:** Context selection, context pack assembly, stale context detection
- **Mutation Scope:** Context economy artifacts only — no application source mutation
- **Cannot:** Execute implementation, validate product correctness, mutate source code

### Janitor
- **Lane:** Maintenance (12_JANITOR/)
- **Authority:** Stale artifact detection, archival, compaction — within ADAPT governance artifacts
- **Mutation Scope:** ADAPT governance artifacts (archive, mark, summarize) — no product artifacts deleted without approval
- **Cannot:** Decide product behavior, delete source truth without Director approval, close blockers without proof

### Challenge (10th Man)
- **Lane:** Challenge Lane (09_CHALLENGE_LANE/)
- **Authority:** Challenge authority — can question consensus, surface failure modes, inspect evidence quality
- **Mutation Scope:** Challenge Lane artifacts only — creates challenge reports, not product artifacts
- **Cannot:** Execute implementation, block by opinion alone (must provide evidence or testable failure mode)

## Role Assignment

Roles are assigned to individuals through the onboarding command:
`Onboard {{IDENTITY}} as {{ROLE}}`

One human may own multiple workcells. One execution may operate under only one workcell identity at a time.
