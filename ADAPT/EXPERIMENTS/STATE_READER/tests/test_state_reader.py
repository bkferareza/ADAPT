"""Focused temporary-fixture tests; no live instance is used."""

import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "state_reader.py"
spec = importlib.util.spec_from_file_location("state_reader", SCRIPT)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)

# Independent expected schema inventory, so accidental implementation drift fails.
EXPECTED = (
    "ProjectName ProjectType DeploymentMode RoutingMode InitializationMode "
    "SourceTruthVersion ActiveMilestone ActiveCycle ActiveHandoff CurrentAuthority "
    "ExecutionReadiness CurrentPhase ActiveWorkcell Blocked ActiveBlockers "
    "ActiveGaps LastAction LastContextDelta NextExpectedAction LastConsolidatedAt Notes"
).split()


class StateReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md"
        self.path.parent.mkdir()
        self.values = {field: f"{{{{{field}}}}}" for field in EXPECTED}
        self.values.update(ProjectName="Project café", Blocked="YES",
                           ActiveBlockers="NONE", Notes=r"a  b \| c",
                           LastConsolidatedAt="NEVER", ActiveGaps="")

    def fixture(self, rows=None):
        if rows is None:
            rows = [f"| {key} | {value} |" for key, value in self.values.items()]
        text = ("# Project Control Plane\n\n## Control Plane State\n\n"
                "| Field | Value |\n|-------|-------|\n" + "\n".join(rows)
                + "\n\n---\n\n## Allowed Values\nIgnored prose\n")
        self.path.write_text(text, encoding="utf-8")
        return text

    def cli(self):
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--instance", str(self.root), "--json"],
            capture_output=True, text=True, check=False,
        )

    def test_valid_values_and_schema_order(self):
        self.fixture()
        state = reader.read_state(self.root)
        self.assertEqual(list(state), EXPECTED)
        self.assertEqual(state, self.values)

    def test_missing_and_duplicate_fields(self):
        rows = [f"| {k} | {v} |" for k, v in self.values.items()]
        for bad, message in [(rows[:-1], "Missing fields"),
                             (rows + [rows[0]], "Duplicate field")]:
            with self.subTest(message=message):
                self.fixture(bad)
                with self.assertRaisesRegex(ValueError, message):
                    reader.read_state(self.root)
                result = self.cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn(message, result.stderr)

    def test_missing_file(self):
        result = self.cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr)

    def test_malformed_tables(self):
        valid = self.fixture()
        cases = [
            valid.replace("| Field | Value |", "| Field | Other |"),
            valid.replace("|-------|-------|", "|--|-------|"),
            valid.replace("| Blocked | YES |", "| Blocked | YES | extra |"),
            valid.replace("| Blocked | YES |", "Blocked | YES"),
            valid.replace("| Blocked | YES |", "| Unknown | YES |"),
            valid.replace("| Blocked | YES |", "\n| Blocked | YES |"),
            valid.replace("| Blocked | YES |", "| Blocked | x | y |"),
            valid.replace("## Allowed Values", "## Control Plane State"),
            valid.replace("## Control Plane State", "## Other"),
            valid.replace("\n\n---", "\nprose\n\n---"),
        ]
        for index, text in enumerate(cases):
            with self.subTest(case=index):
                self.path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    reader.read_state(self.root)
                result = self.cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")

    def test_deterministic_output_and_no_mutation(self):
        self.fixture()
        before = {p.relative_to(self.root): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        first, second = self.cli(), self.cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(json.loads(first.stdout), self.values)
        self.assertEqual(list(json.loads(first.stdout)), EXPECTED)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes()
                                 for p in self.root.rglob("*") if p.is_file()})
        self.fixture([f"| {k} | {self.values[k]} |" for k in reversed(EXPECTED)])
        self.assertEqual(self.cli().stdout, first.stdout)

    def test_bom_crlf_and_alignment(self):
        text = self.fixture().replace("|-------|-------|", "|:-------|-------:|")
        self.path.write_bytes(b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode())
        self.assertEqual(reader.read_state(self.root), self.values)

    def canonical_fixture(self):
        framework = SCRIPT.parents[2]
        template = framework / "CANONICAL_STARTERS/02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md"
        schema = framework / "CANONICAL_STARTERS/15_COMMANDS_AND_DRIVERS/CONTROL_PLANE_SCHEMA.md"
        text = template.read_text(encoding="utf-8")
        schema_text = schema.read_text(encoding="utf-8")
        schema_section = schema_text.split("## Schema\n", 1)[1].split(
            "## Control Plane Consistency Rules", 1)[0]
        fields = re.findall(r"^### (\w+)\s*$", schema_section, re.MULTILINE)
        self.assertEqual(len(fields), 21)
        self.assertEqual(list(reader.FIELDS), fields)
        section = text.split("## Control Plane State\n", 1)[1].split(
            "## Allowed Values", 1)[0]
        rows = re.findall(r"^\| (\w+) \| (.*?) \|$", section, re.MULTILINE)
        self.assertEqual(rows[0], ("Field", "Value"))
        expected = dict(rows[1:])
        self.assertEqual(list(expected), fields)
        self.path.write_bytes(template.read_bytes())
        return text, expected

    def test_actual_canonical_template_acceptance(self):
        _, expected = self.canonical_fixture()
        before = self.path.read_bytes()
        first, second = self.cli(), self.cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(json.loads(first.stdout), expected)
        self.assertEqual(list(json.loads(first.stdout)), list(expected))
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.root.rglob("*.md")), [self.path])

    def test_actual_template_rejects_each_missing_duplicate_and_unknown_field(self):
        text, expected = self.canonical_fixture()
        cases = []
        for field, value in expected.items():
            row = f"| {field} | {value} |\n"
            cases.append((f"missing {field}", text.replace(row, "", 1)))
            cases.append((f"duplicate {field}", text.replace(row, row + row, 1)))
        cases.append(("unknown extra field", text.replace(
            "| Field | Value |\n|-------|-------|\n",
            "| Field | Value |\n|-------|-------|\n| UnknownField | value |\n", 1)))
        for name, invalid in cases:
            with self.subTest(case=name):
                self.path.write_text(invalid, encoding="utf-8")
                before = self.path.read_bytes()
                result = self.cli()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr)
                self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
