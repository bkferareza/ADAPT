# Experimental State Reader

Read-only Python standard-library prototype for ADAPT-FW-0001. It is optional,
outside canonical starters, and is not part of mandatory ADAPT execution.

From this directory:

```powershell
python state_reader.py --instance "D:\path\ADAPT_INSTANCE\ADAPT" --json
python -B -m unittest discover -s tests -p test_state_reader.py -v
```

Supply the directory directly containing `02_DIRECTOR_LANE`, not its parent.
The only input read is `02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md` beneath it.
Success writes a JSON object containing exactly the 21 schema fields to stdout
and exits 0. Failure writes a diagnostic to stderr, no JSON, and exits nonzero.

Keys follow the canonical starter/schema order regardless of input row order.
Values remain strings, including empty cells, placeholders, `YES`, `NONE`, and
dates. No defaults, type conversion, Markdown rendering, readiness inference,
action execution, or work authorization occurs. Markdown cell padding is
trimmed; internal whitespace and escaped pipes are preserved literally.

## Supported input and limitations

Requires exactly one `## Control Plane State` section containing a single
two-column `Field | Value` table with outer pipes and a Markdown separator
(at least three hyphens per cell; alignment colons allowed). Each field must
appear exactly once. Unknown fields, extra columns, broken rows, duplicate
sections, interrupted tables, or additional prose/tables in that section fail.
Blank lines and a `---` divider may follow the table; the next level-one or
level-two heading ends the section. Other document sections are ignored.
Input is UTF-8, optionally with a BOM. Literal pipes in values must be escaped
with an odd number of preceding backslashes; those escapes remain in JSON.
Multiline cells and alternate Markdown layouts are unsupported.

This extracts recorded text only. It does not validate allowed values, perform
CP-C01 through CP-C11 checks, read registers/handoffs, or certify governance
state. It has no locking or coordinated snapshot guarantee against concurrent
instance writes. The field list is pinned to the reviewed 21-field schema;
future schema revisions need explicit review. The utility opens input only for
reading and does not modify instance or framework files.

## Evidence needed before promotion

Focused fixture tests establish parser behavior only. Promotion would need
referenced, classified evidence from real governed instance use showing the
problem addressed, reproducible extraction accuracy and failure behavior,
determinism and input integrity across relevant environments/layouts, and a
qualifying framework-learning escalation or lesson with novelty dimensions.
Separate solution-specific findings from the proposed generic change. The
Framework Maintainer would need to assess the candidate, record a `PROMOTED`
disposition with a decision and introduced version, and authorize a framework
patch with upgrade/backport assessment. No candidate, approval, promotion,
or version change is asserted by this experiment.
