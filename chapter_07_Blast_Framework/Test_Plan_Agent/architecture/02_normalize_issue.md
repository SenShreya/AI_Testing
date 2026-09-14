# SOP 02 — Normalise the Jira Payload

**Layer:** 1 (Architecture)
**Tool:** `tools/jira_client.py`
**Status:** Active

---

## Goal

Convert the raw, site-specific Jira JSON (including Atlassian Document Format
rich text) into **one stable shape** — `JiraIssue` — that every downstream
component can rely on. The LLM never sees raw Jira JSON.

## Output shape — `JiraIssue`

```json
{
  "key": "VWO-49",
  "url": "https://your-domain.atlassian.net/browse/VWO-49",
  "summary": "…",
  "description": "plain text",
  "acceptance_criteria": "plain text or ''",
  "acceptance_criteria_source": "customfield | none",
  "issue_type": "Story",
  "status": "In Progress",
  "priority": "High",
  "labels": ["…"],
  "components": ["…"],
  "fix_versions": ["…"],
  "assignee": "Jane Doe",
  "reporter": "John Smith",
  "created": "ISO-8601",
  "updated": "ISO-8601",
  "due_date": null,
  "parent": { "key": "…", "summary": "…" },
  "subtasks": [ { "key": "…", "summary": "…", "status": "…" } ],
  "links": [ { "type": "…", "direction": "…", "key": "…", "summary": "…" } ],
  "comments": [ { "author": "…", "created": "ISO-8601", "body": "…" } ],
  "fetched_at": "ISO-8601"
}
```

## Invariants (must hold for every issue)

1. Strings are **never** `null` — use `""`.
2. Lists are **never** `null` — use `[]`.
3. `description` and `acceptance_criteria` are **always plain text**, never ADF.
4. Content is **verbatim from Jira** or explicitly empty — no guessing here.

## ADF → plain text

Modern Jira Cloud returns `description` as an ADF document
(`{"type":"doc","content":[…]}`). Walk the tree and emit lines:

| ADF node | Rendering |
|---|---|
| `paragraph`, `heading` | the node's text |
| `bulletList`, `orderedList` | recurse into items |
| `listItem` | `- <text>` then nested content, indented |
| `codeBlock`, `blockquote` | fenced block |
| `table` | rows joined with ` \| ` |
| `mediaSingle` | `[image]` |
| `rule`, `hardBreak` | blank line |
| text marks `code` / `strong` | back-ticks / `**bold**` |
| `inlineCard` | the card URL |
| `mention` | `@name` |
| unknown | ignored silently |

A plain-string description is returned as-is.

## Verification

Given a fetched issue, every key in `JiraIssue` is present, lists are lists,
and no value is `null`.

## Golden rule

If this logic changes, **update this SOP before changing the code.**
