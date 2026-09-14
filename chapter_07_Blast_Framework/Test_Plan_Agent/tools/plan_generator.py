"""Deterministic Test Plan generator.

Turns one normalised ``JiraIssue`` into a Markdown Test Plan using Groq.

The document structure comes from ``templates/testplan_template.md`` and the
depth/style (including the test-case table format) from
``templates/VWO_Test_Plan.md`` — both loaded via ``tools/template_loader``.
Generation rules live here as code constants (no external prompt templates).
See ``architecture/03_generate_test_plan.md``.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from tools import template_loader
from tools.groq_client import GroqClient

# Fallback outline, used only when no template file is present.
DEFAULT_SECTION_TITLES = [
    "1. Introduction",
    "2. Test Level",
    "3. Test Reporting and Defect Tracking",
    "4. Change Management",
    "5. Test Planning",
    "6. Customer Validation Plan",
    "Appendix",
]

# Depth levels: each raises the per-section minimums and the overall ambition.
_DEPTH = {
    "standard": {
        "label": "STANDARD",
        "suites": "4",
        "cases": "12",
        "risks": "5",
        "metrics": "5",
        "size": "a complete, dense document (~4–6 pages)",
        "extra": (
            "- Cover positive, negative, boundary and exception paths.\n"
            "- Fill every template table with real rows (no empty tables)."
        ),
    },
    "detailed": {
        "label": "DETAILED",
        "suites": "8",
        "cases": "25",
        "risks": "8",
        "metrics": "8",
        "size": "an exhaustive document (~8–12 pages) — an explicit request for maximum depth",
        "extra": (
            "- Include edge cases, boundary values and data permutations.\n"
            "- Add non-functional coverage where relevant: performance, security, "
            "accessibility, compatibility, usability.\n"
            "- Expand every table to the maximum number of meaningful rows."
        ),
    },
}

_INSTRUCTIONS = """You are a Senior QA Lead writing a formal, enterprise-grade Test Plan for ONE Jira ticket.

You receive FACTS about the ticket, a REQUIRED DOCUMENT TEMPLATE, and a MASTER EXAMPLE. Produce the Test Plan document ONLY.

## Output rules
- Output the finished Test Plan in GitHub-flavoured Markdown. No preamble, no closing commentary, no meta remarks.
- Start with a level-1 title `# Test Plan` and the project name, then use `##` for the numbered top-level sections (1.–6.), `###` for x.y and `####` for x.y.z.
- The REQUIRED TEMPLATE STRUCTURE below defines the document. Reproduce it EXACTLY: every heading and sub-heading, in the same order, with the same numbering.
- Place each table exactly under the heading whose `table:` line matches it — never reuse a table format under a different heading.
- Never delete a section and never add unrelated ones. Never leave a heading without content.
- Tone: precise, professional, enterprise QA documentation.

## Test cases (critical — this is the core deliverable)
- Include a "Test Case Suites" section (under the template's test-level/planning area, or as its own numbered section if the template has no obvious home for it).
- Present test cases as Markdown tables with EXACTLY these columns:
  | Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |
- Leave the "Actual Result" column EMPTY in every row — it is filled at execution time.
- Test case IDs: `<PROJECT>-<AREA>-<NNN>_<T>` where T is P (positive), N (negative), B (boundary) or E (exception). Group cases into suites by area (S1, S2, ...).
- Cover positive, negative, boundary and exception paths.
- Provide at least __SUITES__ suites and at least __CASES__ test cases in total.

## Depth level: __DEPTH_LABEL__
- Target __SIZE__.
- __DEPTH_EXTRA__
- Risks & Contingencies table: __RISKS__+ rows.
- Metrics: add a metrics table with columns | Metric | Definition | Target | Report Cadence | and __METRICS__+ rows. Place it under the template's reporting section (e.g. "Test Reporting and Defect Tracking"), not under Risk.

## Evidence & traceability
- Every test case must cite a Requirement ID. If the ticket states requirements/acceptance criteria, use them; otherwise define clear requirement IDs derived from the description and label them "(derived)".
- Add a requirement coverage matrix with columns | Requirement | Suites covering it | Status |.

## Anti-hallucination (important)
- Never present a ticket fact you were not given: do not invent people, owners, calendar dates, URLs, or numeric SLAs as if they were real.
- You MAY add standard QA detail — suites, cases, risks, metrics, environments — to make the plan complete, but label anything not stated in the ticket "(inferred)", "(proposed)", "(assumption)", or "Inference (low confidence)".
- Where a value is genuinely unknown (e.g. exact error strings, thresholds), write "<to be confirmed from actual build>" rather than guessing.

## CRITICAL — reference formats only
- The reference table formats come from a different product. Reuse ONLY their column structure — never its product names, screen names, URLs, requirement IDs, test-case IDs, risks or any other content.
- Everything you write must come from the current ticket's facts.
"""


def _depth_config(plan_depth: str) -> dict:
    return _DEPTH.get((plan_depth or "").strip().lower(), _DEPTH["standard"])


def _structure_block(template_text: str, master_text: str) -> str:
    if not template_text:
        numbered = "\n".join(
            f"{i}. {title}" for i, title in enumerate(DEFAULT_SECTION_TITLES, start=1)
        )
        return (
            "=== REQUIRED DOCUMENT STRUCTURE (no template file found — use this) ===\n"
            + numbered
            + "\n=== END STRUCTURE ==="
        )

    block = (
        "=== REQUIRED DOCUMENT STRUCTURE (from the project template) ===\n"
        "Reproduce this outline EXACTLY: same headings, same numbering, same order.\n"
        "Each 'table:' line gives the EXACT columns required for the section it sits\n"
        "under — use that table there and ONLY there. Add real content under every heading.\n\n"
        + template_loader.structure_digest(template_text)
    )
    digest = template_loader.master_digest(master_text) if master_text else ""
    if digest:
        block += (
            "\n\n=== TEST CASE FORMAT (from the master example) ===\n" + digest
        )
    return block + "\n=== END STRUCTURE ==="


def _build_system_prompt(plan_depth: str, template_text: str, master_text: str) -> str:
    """Assemble the system prompt: instructions + compact structure + formats."""
    cfg = _depth_config(plan_depth)
    instructions = (
        _INSTRUCTIONS
        .replace("__SUITES__", cfg["suites"])
        .replace("__CASES__", cfg["cases"])
        .replace("__RISKS__", cfg["risks"])
        .replace("__METRICS__", cfg["metrics"])
        .replace("__DEPTH_LABEL__", cfg["label"])
        .replace("__SIZE__", cfg["size"])
        .replace("__DEPTH_EXTRA__", cfg["extra"])
    )
    return instructions + "\n\n" + _structure_block(template_text, master_text)


def _iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def build_user_prompt(issue: dict, plan_depth: str = "standard") -> str:
    """Build a deterministic, delimited fact block from a JiraIssue."""
    lines = [
        "=== JIRA ISSUE FACTS (use only these) ===",
        f"Key: {issue.get('key', '')}",
        f"URL: {issue.get('url', '')}",
        f"Summary: {issue.get('summary', '')}",
        f"Issue Type: {issue.get('issue_type', '') or 'Not specified'}",
        f"Status: {issue.get('status', '') or 'Not specified'}",
        f"Priority: {issue.get('priority', '') or 'Not specified'}",
        f"Labels: {', '.join(issue.get('labels') or []) or 'Not specified'}",
        f"Components: {', '.join(issue.get('components') or []) or 'Not specified'}",
        f"Fix Versions: {', '.join(issue.get('fix_versions') or []) or 'Not specified'}",
        f"Assignee: {issue.get('assignee', '') or 'Not specified'}",
        f"Reporter: {issue.get('reporter', '') or 'Not specified'}",
        f"Created: {issue.get('created', '') or 'Not specified'}",
        f"Updated: {issue.get('updated', '') or 'Not specified'}",
        f"Due Date: {issue.get('due_date') or 'Not specified'}",
        "",
        "Description:",
        issue.get("description") or "Not specified",
        "",
        "Acceptance Criteria:",
        issue.get("acceptance_criteria") or "Not specified",
    ]

    parent = issue.get("parent")
    if parent:
        lines += ["", f"Parent: {parent.get('key')} - {parent.get('summary')}"]

    if issue.get("subtasks"):
        lines.append("")
        lines.append("Subtasks:")
        for sub in issue["subtasks"]:
            lines.append(f"- {sub.get('key')}: {sub.get('summary')} [{sub.get('status')}]")

    if issue.get("links"):
        lines.append("")
        lines.append("Issue Links:")
        for link in issue["links"]:
            lines.append(f"- {link.get('type')} {link.get('key')}: {link.get('summary')}")

    if issue.get("comments"):
        lines.append("")
        lines.append("Comments (may contain clarifications):")
        for comment in issue["comments"]:
            lines.append(f"- {comment.get('author')} ({comment.get('created')}): {comment.get('body')}")

    lines += [
        "",
        f"Plan depth: {plan_depth}.",
        "Now write the complete Test Plan.",
    ]
    return "\n".join(lines)


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
    if text.endswith("```"):
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _provenance(issue: dict, model: str, plan_depth: str) -> str:
    """Deterministic provenance comment (template supplies its own title page)."""
    return (
        f"<!-- Generated by Test Plan Creator | Jira {issue.get('key', '')} | "
        f"{_iso_now()} | Groq {model} | depth {plan_depth} -->"
    )


def _metadata_header(issue: dict, model: str, plan_depth: str) -> str:
    """Deterministic header block (used only when no template is present)."""
    return "\n".join([
        f"# Test Plan — {issue.get('key', '')}: {issue.get('summary', '') or 'Untitled'}",
        "",
        f"- **Jira Key:** {issue.get('key', '')}",
        f"- **Jira URL:** {issue.get('url', '')}",
        f"- **Issue Type:** {issue.get('issue_type', '') or 'Not specified'}",
        f"- **Priority:** {issue.get('priority', '') or 'Not specified'}",
        f"- **Depth:** {plan_depth}",
        f"- **Generated:** {_iso_now()}",
        f"- **Generated by:** Groq · {model}",
        "",
        "---",
        "",
    ])


def outline_sections() -> list[str]:
    """Sections the output must contain (from the template, else built-in)."""
    return template_loader.required_sections() or DEFAULT_SECTION_TITLES


def validate_plan(markdown: str, sections: list[str] | None = None) -> list:
    """Return the section titles missing from the generated plan."""
    lowered = (markdown or "").lower()
    missing = []
    for title in (sections if sections is not None else outline_sections()):
        needle = re.escape(str(title).lower())
        if not re.search(needle, lowered):
            missing.append(title)
    return missing


def generate_test_plan(settings: dict, issue: dict,
                       client: GroqClient | None = None) -> tuple[str, str]:
    """Generate a test plan. Returns (model, markdown_document).

    Raises ``groq_client.GroqError`` if the LLM call fails.
    """
    model = (settings.get("groq_model") or "").strip()
    depth = (settings.get("plan_depth") or "standard").strip().lower()
    if depth not in _DEPTH:
        depth = "standard"
    if client is None:
        client = GroqClient(settings.get("groq_api_key", ""), model)

    template_text = template_loader.load_template()
    master_text = template_loader.load_master()

    system_prompt = _build_system_prompt(depth, template_text, master_text)
    user_prompt = build_user_prompt(issue, depth)
    body = client.chat(system_prompt, user_prompt, max_tokens=16000)
    body = _strip_code_fences(body)

    if template_text:
        document = _provenance(issue, model, depth) + "\n\n" + body
    else:
        document = _metadata_header(issue, model, depth) + body
    return model, document


def suggested_filename(issue: dict) -> str:
    return f"TestPlan_{issue.get('key', 'issue')}.md"
