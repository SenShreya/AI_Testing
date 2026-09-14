# templates/

The reference documents that drive Test Plan generation. These are **read-only
inputs** — the app never writes to them. Editing a file here changes the output
without touching any code.

## Files

| File | What it is | How the app uses it |
|---|---|---|
| `testplan_template.md` | The **test plan template** — the document structure you want (headings, sub-headings and the tables under each) | **Authoritative structure.** `template_loader.structure_digest()` turns it into the required outline + the exact table for every section. The output reproduces it. |
| `VWO_Test_Plan.md` | The **master / gold-standard plan** — a finished example showing the depth and the test-case table format | **Authoritative test-case format.** `template_loader.master_digest()` extracts the test-case table columns and the ID scheme. |

## How it is wired

- `tools/template_loader.py` reads both files and derives compact artefacts:
  - `required_sections()` → numbered top-level sections (used by `validate_plan`)
  - `structure_digest()` → headings + per-section `table:` specs + placeholders
  - `master_digest()` → test-case table header + ID scheme (deduped)
- `tools/plan_generator.py` assembles the prompt from those digests.

## Important: prompt budget

Groq's free tier limits `openai/gpt-oss-120b` to **8,000 tokens/minute**, and
only the *prompt* is metered. The files are therefore **condensed into digests**
— they are **not** embedded verbatim (doing so caused an HTTP 413). See
`phase0/findings.md` §12.2.

## Rules

- Keep the `.md` extension and these exact file names (`template_loader` reads
  them by name: `TEMPLATE_FILENAME`, `MASTER_FILENAME`).
- If a file is missing, generation falls back to a built-in outline.
- If your master is a PDF/DOCX, convert it to `.md` first.
