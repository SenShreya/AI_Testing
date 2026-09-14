"""Load the Test Plan template and master exemplar.

Generation is driven by two user-provided Markdown files in ``templates/``:

* ``testplan_template.md`` — the **required document structure** (the outline the
  output must follow, including its tables).
* ``VWO_Test_Plan.md`` — a **master example** showing the desired depth, style and
  the test-case table format. Reference only; its content must never be copied.

If a file is missing the caller falls back to a built-in outline.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"

TEMPLATE_FILENAME = "testplan_template.md"
MASTER_FILENAME = "VWO_Test_Plan.md"

# A Markdown heading: "## 2. Test Level", "#### 2.4.1 Item Pass / Fail Criteria".
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
# A numbered heading title: "2. Test Level", "2.4.1 Item Pass / Fail Criteria".
_NUMBERED_RE = re.compile(r"^\d+(?:\.\d+)*\.?\s")


def template_path() -> Path:
    return TEMPLATES_DIR / TEMPLATE_FILENAME


def master_path() -> Path:
    return TEMPLATES_DIR / MASTER_FILENAME


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def load_template() -> str:
    """Full text of the required-structure template (or '' if absent)."""
    return _read(template_path())


def load_master() -> str:
    """Full text of the master example (or '' if absent)."""
    return _read(master_path())


def template_available() -> bool:
    return template_path().is_file()


def master_available() -> bool:
    return master_path().is_file()


def _headings(text: str) -> list[tuple[int, str]]:
    out = []
    for line in (text or "").splitlines():
        match = _HEADING_RE.match(line)
        if match and not line.lstrip().startswith("- "):
            out.append((len(match.group(1)), match.group(2).strip()))
    return out


def required_sections(template_text: str | None = None) -> list[str]:
    """Top-level numbered sections of the template.

    These are the sections the generated plan must reproduce, used by
    ``plan_generator.validate_plan``. Un-numbered headings (Copyright Notice,
    Appendix, ...) are excluded — they are boilerplate/optional.
    """
    text = template_text if template_text is not None else load_template()
    if not text:
        return []
    return [
        title for level, title in _headings(text)
        if level == 2 and _NUMBERED_RE.match(title)
    ]


def all_sections(template_text: str | None = None) -> list[str]:
    """Every numbered heading (levels 2-4) — the full sub-section outline."""
    text = template_text if template_text is not None else load_template()
    if not text:
        return []
    return [title for _, title in _headings(text) if _NUMBERED_RE.match(title)]


def outline_text(template_text: str | None = None) -> str:
    """Compact, indented outline of the template's numbered headings.

    This is what goes into the LLM prompt: it carries the full structure
    without the template's bulk (needed for Groq's token-per-minute limit).
    """
    text = template_text if template_text is not None else load_template()
    if not text:
        return ""
    lines = []
    for _, title in _headings(text):
        if not _NUMBERED_RE.match(title):
            continue
        depth = max(0, title.count(".") - 1)
        lines.append("  " * depth + title)
    return "\n".join(lines)


# A table separator row: |---|---| (optionally with colons/space).
_SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")


def _table_header_indices(lines: list[str]) -> set:
    """Indices of lines that are Markdown table header rows."""
    idx = set()
    for i in range(len(lines) - 1):
        a, b = lines[i].strip(), lines[i + 1].strip()
        if a.startswith("|") and a.endswith("|") and _SEPARATOR_RE.match(b):
            idx.add(i)
    return idx


def _clean_header(line: str) -> str:
    cells = [c.strip().strip("*").strip() for c in line.strip().strip("|").split("|")]
    return "| " + " | ".join(cells) + " |"


def structure_digest(template_text: str | None = None) -> str:
    """Per-section structure from the template: headings + the table each
    section expects + any `<placeholder>` guidance.

    This is the authoritative placement of tables, so the model puts the right
    table under the right heading. Compact enough for the prompt budget.
    """
    text = template_text if template_text is not None else load_template()
    if not text:
        return ""
    lines = text.splitlines()
    headers = _table_header_indices(lines)

    entries: list[tuple[str, list[str]]] = []
    current: list[str] | None = None
    for i, line in enumerate(lines):
        match = _HEADING_RE.match(line)
        if match and not line.lstrip().startswith("- "):
            title = match.group(2).strip()
            if _NUMBERED_RE.match(title):
                current = []
                entries.append((title, current))
            else:
                current = None
            continue
        if current is None:
            continue
        stripped = line.strip()
        if i in headers:
            current.append("table: " + _clean_header(stripped))
        else:
            # <placeholder> guidance, possibly wrapped in back-ticks.
            candidate = stripped.strip("`").strip()
            if candidate.startswith("<") and candidate.endswith(">"):
                current.append(candidate)

    out = []
    for title, items in entries:
        depth = max(0, title.count(".") - 1)
        out.append("  " * depth + title)
        for item in items:
            out.append("  " * (depth + 1) + item)
    return "\n".join(out)


def master_digest(master_text: str | None = None) -> str:
    """The test-case table format + ID scheme, extracted from the master.

    The master is the only source for the test-case format, so we lift just
    that — never its prose, and no unrelated tables (which would otherwise be
    copied into the wrong sections).
    """
    text = master_text if master_text is not None else load_master()
    if not text:
        return ""
    lines = text.splitlines()
    headers = _table_header_indices(lines)

    parts: list[str] = []
    seen = set()
    for i in sorted(headers):
        header = _clean_header(lines[i])
        if "test case" in header.lower() and header not in seen:
            seen.add(header)
            parts.append("test case table: " + header)
    for line in lines:
        if "ID scheme" in line:
            parts.append(line.strip())
    return "\n".join(parts)

