"""Read-only, non-distributed FLC-005 authority evidence verifier.

verify_authority(instance, evidence_root, packet) reuses the preflight packet.
Additional evidence references: original_approval and maintainer_provenance.
Each is a bounded external JSON path/SHA256, just like preflight evidence.
original_approval contains binding, inputs, maintainer, director, approved=True,
not_before and expires_at (timezone-qualified). maintainer_provenance contains
human, role, target and original_source (another external path/SHA256).
designation also requires original_source. These are inspectable source claims,
NOT authenticated human records or a new approval/adoption wire protocol.
Optional revocation evidence contains target, task, original_approval (reference),
checked_at, expires_at and revoked (bool). Its authenticity remains unverified.

Human authentication belongs to deployment access controls. This module only
checks local evidence consistency; use the separate human-controlled maintenance
entry in recovery_supervised.py for declared authorization scope. No writer or
production authorization exists.
"""
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import re
import stat
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location(
    "authority_preflight", Path(__file__).with_name("recovery_preflight.py"))
pre = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pre)
op, require = pre.op, pre.require
BINDING_KEYS = ("target", "purpose", "task", "executor", "writes", "ids", "completion")


def _root(value):
    root = Path(value).absolute()
    require(root == root.resolve() and root.is_dir(), "ROOT", "Exact existing root required")
    for entry in (root, *root.parents):
        info = entry.lstat()
        require(not entry.is_symlink() and not getattr(info, "st_file_attributes", 0) &
                stat.FILE_ATTRIBUTE_REPARSE_POINT, "ROOT", "Redirected root unsupported")
    return root


def _bound_bytes(root, reference):
    require(isinstance(reference, dict) and set(reference) == {"path", "sha256"} and
            isinstance(reference["sha256"], str) and
            re.fullmatch(r"[0-9a-f]{64}", reference["sha256"]),
            "SOURCE_SHA256", "Exact path/lowercase SHA256 reference required")
    data = pre.raw(root, reference["path"])
    require(pre.digest(data) == reference["sha256"], "SOURCE_SHA256",
            "Changed source bytes: " + reference["path"])
    return data


def _time(value):
    require(isinstance(value, str), "VALIDITY", "Timestamp must be text")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.tzinfo is not None, "VALIDITY", "Timezone-qualified timestamp required")
    return parsed


def verify_authority(instance, evidence_root, packet):
    """Inspect byte/claim consistency only; never authenticate or grant writes.

    Time evaluation uses the verifier's UTC clock. Lawful release, installation
    and applicable adoption remain governance gates, independent of providers.
    """
    findings = []
    result = {"status": "INVALID_AUTHORITY_EVIDENCE", "structural_status": "FAIL",
              "operational_authority": False, "human_authenticity": "UNVERIFIED",
              "release_or_adoption": "UNVERIFIED", "findings": findings,
              "distribution": "NON_DISTRIBUTED_PROTOTYPE",
              "evaluated_at": datetime.now(timezone.utc).isoformat()}
    now = _time(result["evaluated_at"])

    def check(code, action):
        try:
            message = action()
            findings.append(op.diagnostic(code, "PASS", message))
            return True
        except (pre.Refusal, op.Problem, OSError, ValueError, KeyError,
                TypeError, AttributeError, OverflowError) as error:
            findings.append(op.diagnostic(code, "FAIL", str(error)))
            return False

    def inspect():
        root, external = _root(instance), _root(evidence_root)
        require(not external.is_relative_to(root) and not root.is_relative_to(external),
                "ROOT", "Canonical and evidence roots must be disjoint")
        require(isinstance(packet, dict), "PACKET", "Packet must be a mapping")
        pre.raw(root, op.CP)
        pre.raw(root, op.SCHEMA)
        values = op.state(root)
        target = {"root": str(root), "identity": values["ProjectName"]}

        def target_check():
            require(packet["target"] == target, "TARGET", "Wrong instance/root binding")
            require(packet["purpose"] == pre.PURPOSE and
                    all(isinstance(packet[k], str) and op.resolved(packet[k])
                        for k in ("task", "executor")), "TASK", "Bound recovery task/executor required")
            return "Resolved root and canonical ProjectName match the recovery target"
        check("INSTANCE_AND_ROOT", target_check)
        records = {}
        evidence = packet["evidence"]
        require(isinstance(evidence, dict), "EVIDENCE", "Evidence map required")
        aliases = set()
        for name, ref in evidence.items():
            def read_record():
                data = _bound_bytes(external, ref)
                alias = ref["path"].casefold()
                require(alias not in aliases, "ALIAS", "Duplicate evidence path")
                aliases.add(alias)
                record = pre.load_json(data)
                require(isinstance(record, dict), "EVIDENCE", "JSON object required")
                records[name] = record
                return "Exact SHA256 and unique-key JSON checked: " + ref["path"]
            check("EVIDENCE_SOURCE:" + str(name), read_record)

        binding = {key: packet[key] for key in BINDING_KEYS}

        def original_source(record):
            data = _bound_bytes(external, record["original_source"])
            require(bool(data.strip()), "ORIGINAL", "Empty original source")

        def director_check():
            pre.raw(root, pre.DIRECTOR)
            headers = op.headers(op.text(root, pre.DIRECTOR), ["HUMAN_OWNER", "ROLE", "PROJECT"])
            director, designation = records["director"], records["designation"]
            require(headers["ROLE"] == "Director" and headers["PROJECT"] == target["identity"] and
                    headers["HUMAN_OWNER"] == director["human"] == designation["human"] and
                    designation["target"] == target and designation["role"] == "Human Director" and
                    director["role"] == "Human Director" and
                    designation["original_input"] is True,
                    "DIRECTOR", "Director identity/designation claims conflict")
            original_source(designation)
            return "Director designation and original source bytes match local identity claims only"
        check("DIRECTOR_DESIGNATION", director_check)

        def maintainer_check():
            maintainer, provenance = records["maintainer"], records["maintainer_provenance"]
            require(maintainer["role"] == provenance["role"] == "Human Framework Maintainer" and
                    isinstance(maintainer["human"], str) and op.resolved(maintainer["human"]) and
                    maintainer["human"] == provenance["human"] and provenance["target"] == target,
                    "MAINTAINER", "Maintainer identity/role/provenance claims conflict")
            original_source(provenance)
            return "Human Framework Maintainer role/provenance claims have a hashed source; authenticity unverified"
        check("MAINTAINER_PROVENANCE", maintainer_check)

        def approval_check():
            approval = records["original_approval"]
            require(approval["approved"] is True and approval["binding"] == binding and
                    approval["inputs"] == packet["inputs"] and
                    approval["maintainer"] == records["maintainer"]["human"] and
                    approval["director"] == records["director"]["human"],
                    "APPROVAL", "Original approval reference does not bind exact action/principals")
            require(evidence["original_approval"]["path"].casefold() not in
                    {evidence[n]["path"].casefold() for n in ("authorization", "maintainer", "director")},
                    "APPROVAL", "Original approval must be a separate source")
            return "Original approval source read and hashed; its claims match exact action and humans"
        check("ORIGINAL_HUMAN_APPROVAL", approval_check)

        def scope_check():
            for name, role in (("maintainer", "Human Framework Maintainer"),
                               ("director", "Human Director"), ("authorization", "Bound Authorization")):
                record = records[name]
                require(record["binding"] == binding and record["inputs"] == packet["inputs"] and
                        record["role"] == role and record["original_input"] is True,
                        "SCOPE", "Exact action/input binding missing: " + name)
            auth = records["authorization"]
            require(auth["maintainer"] == records["maintainer"]["human"] and
                    auth["director"] == records["director"]["human"] and
                    auth["executor"] == packet["executor"] and auth["capacity"] == "recovery Context Steward" and
                    auth["canonical_assembly_approved"] is True and bool(auth["gates"]) and
                    auth["gates"] == records["maintainer"]["gates"] == records["director"]["gates"] and
                    all(v in {"APPROVED", "SYNTHETIC_APPROVED"} for v in auth["gates"].values()),
                    "SCOPE", "Explicit delegated assembly/gate claims required")
            require(records["original_approval"]["binding"] == binding,
                    "SCOPE", "Write paths, fields, operations or task differ from original approval")
            aliases = set()
            for write in packet["writes"]:
                path = pre.safe(root, write["path"])
                alias = str(path).casefold()
                require(alias not in aliases, "SCOPE", "Duplicate mutation target")
                aliases.add(alias)
                require(write["operation"] in {"create", "append_row", "append_open_row", "set_fields"} and
                        isinstance(write["fields"], list) and bool(write["fields"]),
                        "SCOPE", "Unsupported operation/field scope")
                require((not path.exists() and write["before_sha256"] == "ABSENT") or
                        (path.is_file() and pre.digest(pre.raw(root, write["path"])) == write["before_sha256"]),
                        "SCOPE", "Mutation before-image changed")
            return "Exact task, delegated executor and mutation plan match source claims; no execution granted"
        check("APPROVED_OPERATION_AND_SCOPE", scope_check)

        def source_check():
            require(bool(packet["inputs"]), "INPUT", "Source inventory required")
            aliases = set()
            for item in packet["inputs"]:
                ref = {k: item[k] for k in ("path", "sha256")}
                _bound_bytes(root, ref)
                require(item["path"].casefold() not in aliases, "INPUT", "Duplicate canonical source")
                aliases.add(item["path"].casefold())
                require(_time(item["verified_at"]) <= now, "VALIDITY", "Future source verification time")
            required = {op.CP, op.SCHEMA, pre.DIRECTOR, pre.GOVERNANCE}
            require(required <= {i["path"] for i in packet["inputs"]}, "INPUT", "Missing identity/contract hashes")
            return "Actual canonical source bytes match exact SHA256 inventory"
        check("EXACT_SOURCE_SHA256", source_check)

        def validity_check():
            approval = records["original_approval"]
            require(_time(approval["not_before"]) <= now < _time(approval["expires_at"]),
                    "VALIDITY", "Authority not yet valid or expired")
            require(all(_time(approval["not_before"]) <= _time(i["verified_at"]) <= now
                        for i in packet["inputs"]), "VALIDITY", "Sources predate authority validity window")
            return "Approval time window and input verification times currently applicable as local claims"
        check("EVIDENCE_VALIDITY", validity_check)

        if "revocation" in evidence:
            def revocation_check():
                record = records["revocation"]
                require(record["target"] == target and record["task"] == packet["task"] and
                        record["original_approval"] == evidence["original_approval"] and
                        _time(record["checked_at"]) <= now < _time(record["expires_at"]) and
                        record["revoked"] is False,
                        "REVOKED", "Revoked, stale or inapplicable revocation information")
                return "Local revocation claim is current and clear; independent revocation source unavailable"
            check("REVOCATION_INFORMATION", revocation_check)
        else:
            findings.append(op.diagnostic("REVOCATION_INFORMATION", "NOT_CHECKED",
                                          "No revocation source supplied; current revocation cannot be established"))

        version = {}
        def version_check():
            pre.raw(root, pre.GOVERNANCE)
            version["value"] = op.headers(op.text(root, pre.GOVERNANCE), ["VERSION"])["VERSION"]
            result["claimed_effective_release"] = version["value"]
            require(version["value"] == "ADAPT-FW-0006", "CAPABILITY",
                    "Installed version does not claim the proposed recovery capability")
            return "Local governing header claims " + version["value"] + "; publication not authenticated"
        check("EFFECTIVE_RELEASE_IDENTITY", version_check)

        for name in ("release", "adoption"):
            def chain_check():
                record, installation = records[name], records["installation"]
                require(record["target"] == target and record["version"] == version["value"] and
                        record["effective"] is True and
                        record["maintainer"] == records["maintainer"]["human"] and
                        installation[name] == evidence[name], "CAPABILITY", "Conflicting " + name + " chain")
                return "Hashed " + name + " claim is internally consistent; authenticity unverified"
            check(name.upper() + "_EVIDENCE", chain_check)

        def installation_check():
            install = records["installation"]
            require(install["target"] == target and install["version"] == version["value"] and
                    install["effective"] is True and
                    install["maintainer"] == records["maintainer"]["human"] and
                    install["capabilities"] == ["rule14-entry", "purpose-b-assembly"] and
                    set(install["contracts"]) == {pre.GOVERNANCE, op.SCHEMA,
                        "15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md"},
                    "CAPABILITY", "Incomplete installation/capability claims")
            for path, sha in install["contracts"].items():
                _bound_bytes(root, {"path": path, "sha256": sha})
            return "Installed contract bytes match local installation claims; no installation attestation"
        check("INSTALLATION_EVIDENCE", installation_check)
        return "Read-only evidence inspection completed"

    check("EVIDENCE_INSPECTION", inspect)
    structural_valid = not any(f["status"] == "FAIL" for f in findings)
    if structural_valid:
        result.update(status="UNVERIFIED", structural_status="PASS")
    findings.append(op.diagnostic("STRUCTURAL_EVIDENCE_VALID",
                                 "PASS" if structural_valid else "FAIL",
                                 "Local structural consistency only; no operational grant"))
    findings.extend([
        op.diagnostic("RELEASE_OR_ADOPTION_UNVERIFIED", "UNVERIFIED",
                      "Local headers and evidence claims alone do not establish lawful release/adoption."),
        op.diagnostic("OPERATIONAL_AUTHORITY_UNVERIFIED", "UNVERIFIED",
                      "Read-only evidence inspection cannot authorize production recovery."),
        op.diagnostic("HUMAN_AUTHENTICITY_UNVERIFIED", "UNVERIFIED",
                      "Human authentication is the deployment operator's responsibility; "
                      "authorization must be supplied separately through maintenance entry.")])
    return result
