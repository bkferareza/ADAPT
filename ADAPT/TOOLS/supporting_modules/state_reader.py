"""Read-only extraction of the ADAPT control-plane table."""

import argparse
import json
from pathlib import Path
import re
import sys


FIELDS = (
    "ProjectName", "ProjectType", "DeploymentMode", "RoutingMode",
    "InitializationMode", "SourceTruthVersion", "ActiveMilestone", "ActiveCycle",
    "ActiveHandoff", "CurrentAuthority", "ExecutionReadiness", "CurrentPhase",
    "ActiveWorkcell", "Blocked", "ActiveBlockers", "ActiveGaps", "LastAction",
    "LastContextDelta", "NextExpectedAction", "LastConsolidatedAt", "Notes",
)
CONTROL_PLANE = Path("02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md")


def cells(line):
    """Split unescaped pipes, retaining literal Markdown value text."""
    line = line.strip()
    parts = []
    start = 0
    backslashes = 0
    for index, char in enumerate(line):
        if char == "|" and backslashes % 2 == 0:
            parts.append(line[start:index])
            start = index + 1
        backslashes = backslashes + 1 if char == "\\" else 0
    parts.append(line[start:])
    if len(parts) != 4 or parts[0] or parts[-1]:
        raise ValueError("Malformed table: expected two cells with outer pipes")
    return [part.strip() for part in parts[1:-1]]


def read_state(instance):
    """Return all 21 recorded strings in schema order; never write files."""
    lines = (Path(instance) / CONTROL_PLANE).read_text(encoding="utf-8-sig").splitlines()
    headings = [i for i, line in enumerate(lines)
                if line.strip() == "## Control Plane State"]
    if len(headings) != 1:
        raise ValueError("Expected exactly one '## Control Plane State' section")
    start = headings[0] + 1
    end = next((i for i in range(start, len(lines))
                if re.match(r"^#{1,2}\s", lines[i])), len(lines))
    section = lines[start:end]
    while section and not section[0].strip():
        section.pop(0)
    if len(section) < 2 or cells(section[0]) != ["Field", "Value"]:
        raise ValueError("Malformed table: expected Field / Value header")
    if any(not re.fullmatch(r":?-{3,}:?", cell) for cell in cells(section[1])):
        raise ValueError("Malformed table separator")
    values = {}
    ended = False
    for line in section[2:]:
        if not line.strip() or line.strip() == "---":
            ended = True
            continue
        if ended:
            raise ValueError("Malformed table: unexpected content after table")
        field, value = cells(line)
        if field not in FIELDS:
            raise ValueError(f"Unexpected field: {field}")
        if field in values:
            raise ValueError(f"Duplicate field: {field}")
        values[field] = value
    missing = [field for field in FIELDS if field not in values]
    if missing:
        raise ValueError("Missing fields: " + ", ".join(missing))
    return {field: values[field] for field in FIELDS}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, type=Path)
    parser.add_argument("--json", required=True, action="store_true")
    args = parser.parse_args(argv)
    try:
        state = read_state(args.instance)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"state_reader: {error}", file=sys.stderr)
        return 1
    print(json.dumps(state, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
