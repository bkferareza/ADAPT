"""Fixed synthetic agent acceptance actions and read-only conformance checks.

Validation asset only: not shipped tooling, an approval authenticator, or a
general onboarding engine. Codex invokes and inspects each stage separately.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import shutil

spec = importlib.util.spec_from_file_location("bootstrap", Path(__file__).with_name("bootstrap_case.py"))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
need, read, write, sha, state, snapshot = b.need, b.read, b.write, b.sha, b.state, b.snapshot
REGISTRY = "02_DIRECTOR_LANE/WORKCELL_REGISTRY.md"
IDENTITY = "02_DIRECTOR_LANE/DIRECTOR_IDENTITY.md"
POLICY = "15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_ONBOARDING.md"
DIRECTOR = "SYNTHETIC TEST OWNER"
ROLES = {"Planner": ("PLANNER", "PLANNING"), "QA Engineer": ("QA", "QA")}
CORE = ["WORKCELL_IDENTITY.md", "SCOPE_CONTRACT.md", "DEFAULT_AGENT_BLUEPRINT.md", "WORKFLOW_CUSTOMIZATION.md", "EFFECTIVE_WORKFLOW.md", "GUARDRAIL_BINDINGS.md", "WORKFLOW_CHANGE_REQUESTS.md", "WORKFLOW_CHANGE_LOG.md", "ROADMAP.md", "TASK_REGISTER.md", "EVIDENCE_LOG.md", "HANDOFFS.md", "BLOCKERS.md", "CONTEXT_DELTAS.md"]
PINS = [POLICY, "11_ONBOARDING/ONBOARDING_RULES.md", "00_FRAMEWORK/GOVERNANCE_RULES.md", "00_FRAMEWORK/ROLE_MODEL.md", "15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_MASTER.md", "15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_DIRECTOR.md", "15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_CONTEXT_STEWARD.md", "15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md", "15_COMMANDS_AND_DRIVERS/COMMAND_REGISTRY.md", "15_COMMANDS_AND_DRIVERS/COMMAND_ROUTING_MATRIX.md", "15_COMMANDS_AND_DRIVERS/HUMAN_APPROVAL_GATES.md", "15_COMMANDS_AND_DRIVERS/CONTROL_PLANE_SCHEMA.md", "15_COMMANDS_AND_DRIVERS/STOP_RULES.md"]


def data(root, ref):
    return json.loads(read(root, ref))


def metadata(text, field):
    found = re.findall(r"^" + re.escape(field) + r":\s*([^\r\n]+)$", text, re.M)
    need(len(found) == 1, "IDENTITY_FIELD")
    return found[0]


def target(n):
    role = "Planner" if n == 1 else "QA Engineer"
    abbreviation, prompt = ROLES[role]
    name = "TESTALPHA" if n == 1 else "TESTBETA"
    wid = abbreviation + "_" + name
    return {"n": n, "identity": name, "role": role, "id": wid, "folder": "03_WORKCELLS/" + wid, "prompt": prompt,
            "input": f"11_ONBOARDING/SYNTHETIC_INPUT_{n}.json", "request": f"06_HANDOFFS/ACTIVE/HO-{3*n:04}.md",
            "pack": f"10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-{n+1:04}.md", "er": f"11_ONBOARDING/ER-{2*n+2:04}.md",
            "delta": f"10_CONTEXT_ECONOMY/CONTEXT_DELTAS/CD-{2*n+2:04}.md", "out": f"06_HANDOFFS/ACTIVE/HO-{3*n+2:04}.md"}


def files(t):
    return [*CORE, f"ACTION_PROMPT_{t['id']}.md"]


def scope_paths(t):
    return [t["folder"] + "/" + f for f in files(t)] + [REGISTRY, "11_ONBOARDING/ROLE_TO_WORKCELL_MAP.md", "11_ONBOARDING/ONBOARDING_REPORTS.md", t["er"], t["delta"], t["request"], t["request"].replace("/ACTIVE/", "/CONSUMED/"), f"06_HANDOFFS/ACTIVE/HO-{3*t['n']+1:04}.md", f"06_HANDOFFS/CONSUMED/HO-{3*t['n']+1:04}.md", t["out"], b.CP]


def handoff(root, identifier, sender, receiver, pack, er, delta, scope):
    text = b.handoff(root, identifier, "Director Lane", er, delta, pack, "Governance onboarding only", scope)
    text = text.replace("FROM_LANE: Context Steward", "FROM_LANE: " + sender).replace("TO_WORKCELL / TO_LANE: Director Lane", "TO_WORKCELL / TO_LANE: " + receiver)
    return text


def fixture_inputs(base, root, n):
    """Synthetic human/Director-issued input records, not an executed Director dispatch.

    Approval provenance authenticity is a test assumption, explicitly synthetic.
    The acceptance claim covers Steward assembly and Onboarding execution from
    these supplied records, not a new Director intake implementation.
    """
    t = target(n)
    decision_id = b.next_decision_id(root)
    need((root / b.PACK).is_file(), "FIRST_ORDINARY_PACK")
    need(metadata(read(root, IDENTITY), "HUMAN_OWNER") == DIRECTOR, "DIRECTOR_FIXTURE")
    doc = {"synthetic_fixture_only": True, "decision_id": decision_id, "designation": {"human_owner": DIRECTOR, "project": state(root)["ProjectName"], "reference": "SYNTHETIC-HUMAN-DESIGNATION-001"},
           "approval": {"gate": 3, "approved": True, "identity": t["identity"], "role": t["role"], "reference": f"SYNTHETIC-GATE3-{n}", "director": DIRECTOR},
           "command": f"Onboard {t['identity']} as {t['role']}", "scope": scope_paths(t), "source_version": b.VERSION,
           "control_fields": ["CurrentPhase", "LastAction", "LastContextDelta", "NextExpectedAction"],
           "notice": "Synthetic external input fixture only; no genuine Human Owner approved these identities. Director records are supplied inputs, not a claimed Director dispatch."}
    write(root, t["input"], json.dumps(doc, indent=2) + "\n")
    b.put_row(root, b.DEC, f"{decision_id}", [f"{decision_id}", "Synthetic Director designation and Gate 3 onboarding scope", "Governance preparation only", DIRECTOR, b.DATE, t["id"], "No implementation", "ACTIVE", t["input"] + "; " + doc["approval"]["reference"] + "; SYNTHETIC-HUMAN-DESIGNATION-001"])
    b.put_row(root, b.INTAKE, f"INT-{n+1:03}", [f"INT-{n+1:03}", b.DATE, "Synthetic human fixture", doc["command"], "Onboarding Command", "Onboarding Orchestrator", "ROUTED", t["input"] + f"; exact scope in {decision_id}"])
    b.put_row(root, "11_ONBOARDING/ONBOARDING_REPORTS.md", f"ONB-{n:03}", [f"ONB-{n:03}", t["id"], t["role"], "0", "15", "NOT_CHECKED", "REQUESTED", doc["approval"]["reference"] + "; " + t["input"]])
    write(root, t["request"], handoff(root, f"HO-{3*n:04}", "Director Lane", "Onboarding Orchestrator", "PENDING ordinary pack", t["input"], "NONE", doc["command"] + "; " + t["input"] + f"; {decision_id}"))
    # Fixture includes the Director's routed lane authority; it never binds a workcell.
    b.set_state(root, CurrentAuthority="Context Steward")
    write(base, f"inputs-{n}.json", json.dumps({"classification": "SYNTHETIC_HUMAN_AND_DIRECTOR_INPUT_FIXTURES", "target": t, "input": doc, "hashes": snapshot(root)}, indent=2))
    print("SYNTHETIC_INPUTS_READY; not a Director dispatch claim; STOP")


def director_check(root, t):
    need((root / IDENTITY).is_file(), "DIRECTOR_MISSING")
    text = read(root, IDENTITY)
    need("{{" not in text, "DIRECTOR_PLACEHOLDER")
    need(metadata(text, "PROJECT") == state(root)["ProjectName"] and metadata(text, "ROLE") == "Director" and metadata(text, "WORKCELL_TYPE") == "Director Lane", "DIRECTOR_AUTHORITY")
    d = data(root, t["input"])
    need(d.get("synthetic_fixture_only") is True, "FIXTURE_LABEL")
    designation = d["designation"]
    need(metadata(text, "HUMAN_OWNER") == designation["human_owner"] == DIRECTOR and designation["project"] == state(root)["ProjectName"], "DESIGNATION_CONFLICT")
    need(designation["reference"] in read(root, b.DEC) and t["input"] in read(root, b.DEC), "DESIGNATION_UNTRACED")
    return d


def preflight(root, t, executor="Onboarding Orchestrator", planned=None):
    d = director_check(root, t)
    s = state(root)
    need(executor == s["CurrentAuthority"] == "Onboarding Orchestrator", "EXECUTOR_AUTHORITY")
    need(s["SourceTruthVersion"] == b.VERSION == d["source_version"] and "| " + b.VERSION + " |" in b.real_rows(root / b.LOG), "SOURCE_VERSION")
    need(all(s[k] == "NONE" for k in ("ActiveWorkcell", "ActiveHandoff")), "WORKCELL_BINDING")
    a = d.get("approval", {})
    need(a.get("approved") is True and a.get("gate") == 3 and a.get("identity") == t["identity"] and a.get("role") == t["role"] and a.get("director") == DIRECTOR, "GATE_3")
    need(a["reference"] in read(root, b.DEC) and a["reference"] in read(root, "11_ONBOARDING/ONBOARDING_REPORTS.md"), "APPROVAL_UNTRACED")
    need(d["command"] == f"Onboard {t['identity']} as {t['role']}" and "`Onboard {{IDENTITY}} as {{ROLE}}`" in read(root, "15_COMMANDS_AND_DRIVERS/COMMAND_REGISTRY.md"), "COMMAND")
    need(set(d["scope"]) == set(scope_paths(t)) and set(planned or d["scope"]) <= set(d["scope"]), "SCOPE_AUTHORIZATION")
    need(d.get("control_fields") == ["CurrentPhase", "LastAction", "LastContextDelta", "NextExpectedAction"], "CONTROL_SCOPE_AUTHORIZATION")
    need(t["role"] in ROLES and "### " + t["role"] in read(root, "00_FRAMEWORK/ROLE_MODEL.md"), "ROLE")
    need(not (root / t["folder"]).exists() and not re.search(r"^\| " + re.escape(t["id"]) + r" \|", read(root, REGISTRY), re.M), "DUPLICATE_IDENTITY")
    need((root / t["request"]).is_file(), "HANDOFF_MISSING")
    ho = read(root, t["request"])
    need("STATUS: ACTIVE" in ho and "FROM_LANE: Director Lane" in ho and "TO_WORKCELL / TO_LANE: Onboarding Orchestrator" in ho and d["command"] in ho, "HANDOFF_BINDING")
    need((root / t["pack"]).is_file(), "ORDINARY_CONTEXT_MISSING")
    pack = read(root, t["pack"])
    need("ASSEMBLED_BY: Context Steward" in pack and "SOURCE_TRUTH_VERSION: " + b.VERSION in pack and f"HANDOFF_ID: HO-{3*t['n']:04}" in pack, "CONTEXT_BINDING")
    hashes = dict(re.findall(r"^\| ([^|]+) \| ([a-f0-9]{64}) \|$", pack, re.M))
    need({IDENTITY, b.PRESERVED, b.LOG, b.DEC, t["input"], t["request"], *PINS} <= hashes.keys(), "CONTEXT_INPUTS")
    need(all((root / p).is_file() and sha(root / p) == h for p, h in hashes.items()), "ORDINARY_CONTEXT_STALE")
    need("RoutingMode: " + s["RoutingMode"] in read(root, "07_GUARDRAILS/SCOPE_GUARDRAIL.md"), "ROUTING")
    return "PASS_ONBOARDING_BASIS"


def context(base, root, n):
    t = target(n); d = director_check(root, t)
    decision_id = d["decision_id"]
    need(state(root)["CurrentAuthority"] == "Context Steward", "STEWARD_AUTHORITY")
    need(state(root)["SourceTruthVersion"] == b.VERSION and (root / t["request"]).is_file(), "STEWARD_INPUT")
    need(d["approval"]["approved"] and set(d["scope"]) == set(scope_paths(t)), "STEWARD_SCOPE")
    before = snapshot(root); shutil.copytree(root, base / f"before-onb-context-{n}")
    index = "10_CONTEXT_ECONOMY/CONTEXT_INDEX.md"
    content = read(root, index)
    for pack_file in (root / '10_CONTEXT_ECONOMY/CONTEXT_PACKS').glob('*.md'):
        recorded = dict(re.findall(r'^\| ([^|]+) \| ([a-f0-9]{64}) \|$', pack_file.read_text(encoding='utf-8'), re.M))
        if any(not (root/p).is_file() or sha(root/p) != h for p,h in recorded.items()):
            identifier = re.search(r'^CONTEXT_PACK_ID: (\S+)', pack_file.read_text(encoding='utf-8'), re.M)
            if identifier:
                content = re.sub(r'(^\| '+re.escape(identifier[1])+r' \|.*)\| ACTIVE \|',r'\1| STALE |',content,flags=re.M)
    write(root,index,content)
    refs = [IDENTITY, b.PRESERVED, b.LOG, b.DEC, b.INTAKE, REGISTRY, t["input"], t["request"], *PINS]
    pack = f"# Ordinary onboarding context\nSTATUS: ACTIVE\nCONTEXT_PACK_ID: CP-{n+1:04}\nASSEMBLED_BY: Context Steward\nWORKCELL_ID: NONE\nLANE: Onboarding Orchestrator\nHANDOFF_ID: HO-{3*n:04}\nSOURCE_TRUTH_VERSION: {b.VERSION}\nCONTEXT_SIZE: M\n## Authoritative State\n{json.dumps(state(root), indent=2)}\n## Active Task\n{read(root,t['request'])}\n## Scope Contract Summary\nPre-workcell governance scope from {decision_id}; exact paths in {t['input']}. Assigned BI-IDs NONE. No product mutation, framework editing, QA or implementation assignment.\n## Required Artifacts / Inclusion Reasons\nIdentity and designation establish accountability; source/log bind truth; decision/input bind Gate 3 and exact scope; registry detects duplicates; contracts govern lane protocol. All SHA256 checked.\n## Decisions, Gaps and Blockers\n{decision_id}; synthetic approval. Existing technical choices concern future product implementation, not onboarding. No blocking item names this onboarding.\n## Exclusions\nUnrelated source history, product source and implementation authority excluded. No superseded inputs.\n## Staleness\nReview prior CD and current hashes before delivery; ordinary checks required again before execution.\n## File Integrity\n| Path | SHA256 |\n|---|---|\n" + "".join(f"| {p} | {sha(root/p)} |\n" for p in refs)
    write(root, t["pack"], pack)
    b.put_row(root, "10_CONTEXT_ECONOMY/CONTEXT_INDEX.md", f"CP-{n+1:04}", [f"CP-{n+1:04}", "NONE (Onboarding lane)", f"HO-{3*n:04}", b.VERSION, "M", b.DATE, "ACTIVE", "Exact synthetic Gate 3 scope; no implementation"])
    # Context delivery addresses Onboarding; the Director's task request remains its task.
    er = f"10_CONTEXT_ECONOMY/CONTEXT_SUMMARIES/ER-{2*n+1:04}.md";cd=f"10_CONTEXT_ECONOMY/CONTEXT_DELTAS/CD-{2*n+1:04}.md"
    write(root, er, f"# Context assembly evidence\nSYNTHETIC ONLY\nSteps 1-13: recovered state; Director task HO-{3*n:04}; Steward self-assembly; M; registered source; exact approved scope; ordinary pack/index; evidence; delta; delivery; named Trace writes; STOP.\nNo workcell invented; all seven Steward stages engaged, one attempt each. Source/identity/approval/contract hashes checked. No product or QA action.\n")
    write(root, cd, f"# CD-{2*n+1:04}\nCreated CP-{n+1:04} and index row. Reviewed prior delta and input hashes; no required input change from this delivery. PROCEED_AS_IS.\n")
    write(root, f"06_HANDOFFS/ACTIVE/HO-{3*n+1:04}.md", handoff(root, f"HO-{3*n+1:04}", "Context Steward", "Onboarding Orchestrator", t["pack"], er, cd, "Deliver ordinary context only; consume this delivery before onboarding completion."))
    b.set_state(root, LastAction=f"CP-{n+1:04} delivered", LastContextDelta=f"CD-{2*n+1:04}", NextExpectedAction="Director to route lawful Onboarding authority")
    b.checkpoint(base, root, f"onb-context-{n}", before)
    print("PASS_ORDINARY_ONBOARDING_CONTEXT; STOP")


def route_fixture(root, n):
    """Supplied Director authority transition, explicitly not a Steward write."""
    director_check(root,target(n))
    need((root/target(n)['pack']).is_file(),'ROUTE_CONTEXT_MISSING')
    b.set_state(root, CurrentAuthority="Onboarding Orchestrator")


def blueprint(root, t):
    text = read(root, f"15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_{t['prompt']}.md")
    sections = re.split(r"(?m)^### \d+\. ", text)[1:]
    value = "# DEFAULT AGENT BLUEPRINT\nSYNTHETIC fixture workcell; defaults copied from canonical role action prompt.\n"
    for section in sections:
        for heading in ["Purpose", "Inputs", "Actions", "Outputs", "Boundaries", "Stop Conditions", "Evidence Produced", "Next Handoff"]:
            section = section.replace("**" + heading + "**", "### " + heading)
        name, rest = section.split("\n", 1)
        value += "\n## " + name + "\n" + rest
    return value


def generate(root, t):
    values = {"PROJECT_NAME": state(root)["ProjectName"], "ROLE": t["role"], "IDENTITY": t["identity"], "WORKCELL_ID": t["id"], "WORKCELL_TYPE": t["role"], "LANE": t["role"], "ONBOARDED_DATE": b.DATE, "DATE": b.DATE, "VERSION": "1", "AUTHORITY_SUMMARY": "Role governance only; no assigned work", "AUTHORITY_SCOPE": "Registered role; execution requires Director assignment", "MUTATION_SCOPE": "NONE until explicit Director assignment", "QA_INDEPENDENCE_STATUS": "FULL", "ACTIVE_MILESTONE": "NONE", "CURRENT_STATUS": "ACTIVE", "INITIAL_SCOPE_SUMMARY": "NONE assigned", "IN_SCOPE_ITEM_1": "Await Director assignment", "IN_SCOPE_ITEM_2": "Read current source and scope before any assigned action", "IN_SCOPE_ITEM_N": "Produce evidence and handoff only for assigned work", "OUT_OF_SCOPE_ITEM_1": "No implementation without assignment", "OUT_OF_SCOPE_ITEM_2": "No scope expansion or QA self-signoff", "OUT_OF_SCOPE_ITEM_N": "No framework edits or release approval", "PATH_PATTERN": "NONE", "FILE_TYPES": "NONE", "RESTRICTIONS": "No execution mutation granted at onboarding", "BI-ID": "NONE", "BI_TITLE": "No assigned business items", "MEMBER_DEFINED_EXECUTION_SEQUENCE": "Follow role defaults and master dispatch; STOP after handoff", "MEMBER_PREFERRED_ANALYSIS_ORDER": "Source, task, scope, context, guardrails", "MEMBER_LOCAL_CHECKLISTS": "Verify authority, ordinary pack, scope and evidence", "MEMBER_WORKING_NOTES": "Synthetic fixture only; no product work"}
    templates = {"WORKCELL_IDENTITY.md": "WORKCELL_IDENTITY", "SCOPE_CONTRACT.md": "SCOPE_CONTRACT", f"ACTION_PROMPT_{t['id']}.md": "ACTION_PROMPT_ROLE_IDENTITY", "GUARDRAIL_BINDINGS.md": "GUARDRAIL_BINDINGS", "WORKFLOW_CUSTOMIZATION.md": "WORKFLOW_CUSTOMIZATION", "WORKFLOW_CHANGE_REQUESTS.md": "WORKFLOW_CHANGE_REQUEST", "WORKFLOW_CHANGE_LOG.md": "WORKFLOW_CHANGE_LOG", "EFFECTIVE_WORKFLOW.md": "EFFECTIVE_WORKFLOW"}
    for f in files(t):
        text = read(root, f"08_TEMPLATES/{templates[f]}_TEMPLATE.md") if f in templates else f"# {f[:-3].replace('_',' ')}\nWORKCELL_ID: {t['id']}\nNo entries; onboarding only; no work assigned or executed.\n"
        for k,v in values.items():text=text.replace("{{"+k+"}}",v)
        text = re.sub(r"\{\{[^}]+\}\}", "NONE", text)
        text = text.replace(t["role"] + "_" + t["identity"], t["id"])
        text=text.replace(f"02_DIRECTOR_LANE/SCOPE_CONTRACT_{t['id']}.md",t['folder']+'/SCOPE_CONTRACT.md')
        write(root, t["folder"]+'/'+f,text)
    write(root,t['folder']+'/DEFAULT_AGENT_BLUEPRINT.md',blueprint(root,t))
    guards = "\n## Enforced framework guardrails\n" + "\n".join(f"- GR-{i:02}: APPLIES; no exception or waiver" for i in range(1,8))
    write(root,t['folder']+'/GUARDRAIL_BINDINGS.md',f"# Guardrail bindings\nWORKCELL_ID: {t['id']}\n"+guards+"\nNo workcell-specific additions. All canonical 07_GUARDRAILS contracts apply.\n")
    names=re.findall(r'^## (.+)$',read(root,t['folder']+'/DEFAULT_AGENT_BLUEPRINT.md'),re.M)
    write(root,t['folder']+'/EFFECTIVE_WORKFLOW.md',f"# Effective workflow\nWORKCELL_ID: {t['id']}\nDEFAULT_AGENT_BLUEPRINT.md + WORKFLOW_CUSTOMIZATION.md + GUARDRAIL_BINDINGS.md\nNo active customizations. All default agents in order:\n"+'\n'.join(f'{i}. {a}' for i,a in enumerate(names,1))+guards+"\nNo execution without assigned handoff, approved scope and ordinary context.\n")
    b.append(root,t['folder']+'/WORKFLOW_CUSTOMIZATION.md',"\nNo active customizations; canonical role defaults only.\n")


def quality(root,t):
    need(all((root/t['folder']/f).is_file() for f in files(t)),"INCOMPLETE_WORKCELL")
    need(all('{{' not in read(root,t['folder']+'/'+f) for f in files(t)),"WORKCELL_PLACEHOLDER")
    text=read(root,t['folder']+'/DEFAULT_AGENT_BLUEPRINT.md')
    agents=re.split(r'(?m)^## ',text)[1:]
    contract=read(b.FRAMEWORK,'WORKCELL_ONBOARDING_CONTRACT.md')
    role_name='Planning' if t['role']=='Planner' else 'QA'
    part=contract.split('### '+role_name+'\n',1)[1].split('### ',1)[0]
    expected=re.findall(r'^\* (.+?) - ',part,re.M)
    need([x.splitlines()[0] for x in agents]==expected,'BLUEPRINT_AGENTS')
    for a in agents:
        need(all('### '+h in a for h in ['Purpose','Inputs','Actions','Outputs','Boundaries','Stop Conditions','Evidence Produced','Next Handoff']),'ROLE_AGENT_BLUEPRINT_DEPTH_FAILURE')
        actions=a.split('### Actions',1)[1].split('### Outputs',1)[0]
        need(len(re.findall(r'^\d+\. ',actions,re.M))>=3,'ROLE_AGENT_BLUEPRINT_DEPTH_FAILURE')
    need('NONE' in read(root,t['folder']+'/SCOPE_CONTRACT.md'),'SCOPE_ASSIGNED')
    return 'PASS_WORKCELL_QUALITY'


def onboard(base,root,n):
    t=target(n);print(preflight(root,t));before=snapshot(root)
    decision_id = data(root, t["input"])["decision_id"]
    shutil.copytree(root,base/f'before-onboard-{n}')
    b.set_state(root,CurrentPhase='ONBOARDING')
    generate(root,t);print(quality(root,t))
    b.put_row(root,REGISTRY,t['id'],[t['id'],t['role'],t['identity'],t['folder'],b.DATE,'ACTIVE',f'SYNTHETIC-GATE3-{n}; {decision_id}; no implementation assigned'])
    b.put_row(root,'11_ONBOARDING/ROLE_TO_WORKCELL_MAP.md',t['role'],[t['role'],t['id'],t['identity'],t['folder'],'ACTIVE'])
    b.put_row(root,'11_ONBOARDING/ONBOARDING_REPORTS.md',f'ONB-{n:03}',[f'ONB-{n:03}',t['id'],t['role'],'15','NONE','PASS','COMPLETE',f'SYNTHETIC-GATE3-{n}; '+t['er']])
    for incoming in [t['request'],f'06_HANDOFFS/ACTIVE/HO-{3*n+1:04}.md']:
        write(root,incoming.replace('/ACTIVE/','/CONSUMED/'),read(root,incoming).replace('STATUS: ACTIVE','STATUS: CONSUMED',1));(root/incoming).unlink()
    write(root,t['er'],f"# Onboarding evidence\nSYNTHETIC ONLY\nDirector designation and Gate 3: {t['input']}; {decision_id}.\n## Stage Record\n| Stage | Attempts | Result |\n|---|---|---|\n"+'\n'.join(f'| {i} | 1 | COMPLETE |' for i in ['1 Recover state','2 Locate addressed handoff','3 Verify lane authority, designation and Gate 3','4 Size M','5 Select minimum context','6 Verify ordinary context and exact scope','7 Execute decision','8 Generate and quality-check 15 files before registration','9 Evidence and before/after differences','10 Context delta','11 Discharge requests and emit Director completion','12 Named Trace fields and ONBOARDING phase','13 STOP'])+"\nAll planned paths checked against approved scope. Source version, human fixture approval, identity, ordinary context hashes and guardrails verified. No product, QA or implementation executed. External checkpoint records exact differences and inverse hashes, including this report.\n")
    write(root,t['delta'],f"# CD-{2*n+2:04}\nCreated {t['id']} with 15 checked artifacts and registry/map/report entries. Assigned BI-IDs NONE. Consumed onboarding and context-delivery requests. Ordinary input packs referencing changed registry/report are now stale; refresh before further use. No implementation authority.\n")
    write(root,t['out'],handoff(root,f'HO-{3*n+2:04}','Onboarding Orchestrator','Director Lane',t['pack'],t['er'],t['delta'],'Review completed onboarding only; assignment is a separate Director action.'))
    b.set_state(root,LastAction=f'{t["id"]} onboarded; '+t['er'],LastContextDelta=f'CD-{2*n+2:04}',NextExpectedAction='Director to review onboarding; no implementation assigned')
    after=snapshot(root);changed={p for p in before.keys()|after.keys() if before.get(p)!=after.get(p)}
    need(changed<=set(scope_paths(t)),'ACTUAL_MUTATION_SCOPE')
    old=data(base,f'onb-context-{n}.json')['state']
    need(all(state(root)[k]==v for k,v in old.items() if k not in {'CurrentAuthority','CurrentPhase','LastAction','LastContextDelta','NextExpectedAction'}),'CONTROL_FIELD_SCOPE')
    b.checkpoint(base,root,f'onboard-{n}',before)
    b.cli(base,root,'doctor');b.cli(base,root,'prompt','next',expected=1)
    print('PASS_ONBOARDING; no assignment; STOP')


def implementation(root,t):
    need(state(root)['ActiveWorkcell']==t['id'] and state(root)['ActiveHandoff']!='NONE','IMPLEMENTATION_UNASSIGNED')


def negatives(base,root):
    """Attack disposable clones of actual supplied onboarding state."""
    t=target(1);records=[];accepted=snapshot(root)
    def attempt(name,setup,check):
        clone=base/('negative-'+name)/'ADAPT';shutil.copytree(root,clone);setup(clone);before=snapshot(clone)
        try:check(clone)
        except b.Stop as error:
            need(snapshot(clone)==before,'NEGATIVE_MUTATED')
            records.append({'case':name,'result':'STOP_REQUIRED','reason':str(error),'no_writes_after_check':True})
        else:raise AssertionError('Expected STOP: '+name)
    def change(c,field,value):
        d=data(c,t['input']);d[field]=value;write(c,t['input'],json.dumps(d))
    noop=lambda c:None
    attempt('missing-director',lambda c:(c/IDENTITY).unlink(),lambda c:preflight(c,t))
    attempt('unresolved-owner',lambda c:write(c,IDENTITY,read(c,IDENTITY).replace(DIRECTOR,'{{DIRECTOR_IDENTITY}}')),lambda c:preflight(c,t))
    attempt('conflicting-designation',lambda c:change(c,'designation',{'human_owner':'OTHER','project':state(c)['ProjectName']}),lambda c:preflight(c,t))
    attempt('missing-gate3',lambda c:change(c,'approval',{}),lambda c:preflight(c,t))
    attempt('mismatched-gate3',lambda c:change(c,'approval',{'approved':True,'gate':3,'identity':'OTHER','role':'Planner','director':DIRECTOR}),lambda c:preflight(c,t))
    attempt('unauthorized-executor',noop,lambda c:preflight(c,t,executor='Backend Workcell'))
    attempt('spoofed-driver',lambda c:b.set_state(c,CurrentAuthority='Director Lane'),lambda c:preflight(c,t))
    attempt('missing-ordinary-context',lambda c:(c/t['pack']).unlink(),lambda c:preflight(c,t))
    attempt('missing-scope',lambda c:change(c,'scope',[]),lambda c:preflight(c,t))
    attempt('duplicate-identity',lambda c:b.put_row(c,REGISTRY,t['id'],[t['id'],'Planner',t['identity'],t['folder'],b.DATE,'ACTIVE','existing']),lambda c:preflight(c,t))
    attempt('incomplete-artifacts',lambda c:generate(c,t) or (c/t['folder']/'SCOPE_CONTRACT.md').unlink(),lambda c:quality(c,t))
    attempt('product-mutation',noop,lambda c:preflight(c,t,planned=['../project/src/greeting.py']))
    attempt('implementation-without-assignment',noop,lambda c:implementation(c,t))
    need(snapshot(root)==accepted,'NEGATIVES_CHANGED_ACCEPTED_INSTANCE')
    write(base,'negative-results.json',json.dumps({'classification':'Conformance attacks on clones of actual scaffold/promoted/context-delivered instance','cases':records,'not_exercised':[]},indent=2))
    print(json.dumps(records,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=['scaffold','promote','first-context','verify-bootstrap','inputs','context','route','negatives','onboard']);p.add_argument('--disposable',type=Path,required=True);p.add_argument('--number',type=int,choices=[1,2],default=1);o=p.parse_args();base=o.disposable.resolve()
    need(base.is_dir() and base.name.startswith('adapt-bootstrap-v2-') and not base.is_relative_to(b.FRAMEWORK.parent),'EXTERNAL_DISPOSABLE_REQUIRED')
    root=base/'acceptance/ADAPT'
    if o.stage=='scaffold':
        b.DOCUMENT=b.DOCUMENT.replace('No product code, workcells, milestone acceptance or QA signoff.','No product code, milestone acceptance or QA signoff. Governance workcell onboarding with Gate 3 is permitted.')
        b.scaffold(base,'MODE_A_EXISTING_SOLUTION')
    elif o.stage in ['promote','first-context','verify-bootstrap']:
        {'promote':b.promote,'first-context':b.context,'verify-bootstrap':b.verify}[o.stage](base,root,data(base,'basis.json'))
    elif o.stage=='inputs':fixture_inputs(base,root,o.number)
    elif o.stage=='context':context(base,root,o.number)
    elif o.stage=='route':
        before=snapshot(root);route_fixture(root,o.number)
        write(base,f'route-{o.number}.json',json.dumps({'classification':'Supplied synthetic Director routing fixture; not a Steward write or executed Director dispatch','before':before,'after':snapshot(root),'state':state(root)},indent=2))
        print('SYNTHETIC_DIRECTOR_ROUTE_READY')
    elif o.stage=='negatives':negatives(base,root)
    elif o.stage=='onboard':onboard(base,root,o.number)
