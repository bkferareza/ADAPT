"""Capture existing unittest suites without rewriting prior release evidence."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
records = []
for folder in ("ADAPT/TOOLS/tests", "ADAPT/EXPERIMENTS/STATE_READER/tests", "ADAPT/EXPERIMENTS/OPERATOR_TOOLKIT/tests"):
    args = [sys.executable, "-B", "-m", "unittest", "discover", "-s", folder, "-v"]
    run = subprocess.run(args, cwd=root, capture_output=True, text=True)
    records.append({"command": ["python", *args[1:]], "exit_code": run.returncode, "stdout": run.stdout, "stderr": run.stderr})
    print(folder + ": exit " + str(run.returncode), flush=True)
(root / "ADAPT/VALIDATION/ONBOARDING_TESTS.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8", newline="\n")
raise SystemExit(0 if all(record["exit_code"] == 0 for record in records) else 1)
