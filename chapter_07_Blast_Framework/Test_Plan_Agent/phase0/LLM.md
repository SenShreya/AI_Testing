# LLM.md — Project Constitution

> B.L.A.S.T. Protocol 0 artifact. This is the **binding constitution** for the
> Test Plan Creator: the data schemas, behavioral rules, and architectural
> invariants. In the original BLAST protocol this file is `gemini.md`; per the
> project brief it is named `LLM.md`.
>
> **Rule:** if logic changes, this file changes first. Code follows the
> constitution, never the reverse.

**Project:** Test Plan Creator from a Jira ID
**Version:** 0.2 (Phases 1–4 implemented)
**Status:** ✅ Implemented; verified offline. Live-network calls await real
credentials (see `progress.md` Session 2).

---

## 1. My thinking on the schema (why it looks like this)

Three forces shape the schema:

1. **The Jira payload is messy and site-specific; the LLM needs clean, stable
   input.** So there is a hard **normalisation boundary**: everything Jira →
   a single `JiraIssue` shape. The LLM never sees raw Jira JSON.
2. **A test plan is a document with fixed sections, not free prose.** So the
   output is a **fixed section set**, each section independently checkable.
3. **LLMs hallucinate.** So every field that could be invented carries an
   explicit **provenance/confidence marker**; missing data is `Not specified`,
   never fabricated.

The pipeline is therefore strictly staged and each stage has exactly one
schema:

```
Jira REST JSON ──(normalise)──► JiraIssue ──(build prompt)──► PlanRequest
                                                                    │
                                                            (LLM)   ▼
                                             TestPlanDraft ◄──(validate)──
                                                    │
                                             (render)▼
                                              TestPlan.md
```

---

## 2. Data schemas (JSON)

### 2.1 `JiraIssue` — the single normalised input shape

This is the **only** thing downstream code is allowed to consume from Jira.
It is the contract between Layer 3 (`jira_client`) and the LLM layer.

```json
{
  "key": "VWO-49",
  "url": "https://your-domain.atlassian.net/browse/VWO-49",
  "summary": "Apply discount code at checkout",
  "description": "Plain-text description (ADF already flattened).",
  "acceptance_criteria": "Plain text, or '' if none found.",
  "acceptance_criteria_source": "customfield name | inferred | none",
  "issue_type": "Story",
  "status": "In Progress",
  "priority": "High",
  "labels": ["checkout", "payments"],
  "components": ["Checkout"],
  "fix_versions": ["1.4.0"],
  "assignee": "Jane Doe",
  "reporter": "John Smith",
  "created": "2026-08-01T10:12:00.000+0530",
  "updated": "2026-09-10T09:00:00.000+0530",
  "due_date": null,
  "parent": { "key": "VWO-40", "summary": "Cart & Checkout epic" },
  "subtasks": [
    { "key": "VWO-50", "summary": "Validate expired code", "status": "To Do" }
  ],
  "links": [
    { "type": "blocks", "direction": "outward", "key": "VWO-51", "summary": "..." }
  ],
  "comments": [
    { "author": "Jane Doe", "created": "2026-09-01T...", "body": "Plain text" }
  ],
  "attachments": [
    { "filename": "mockup.png", "url": "https://..." }
  ],
  "fetched_at": "2026-09-13T19:08:07+05:30"
}
```

**Invariants**
- Strings are never `null` — use `""` or `Not specified` at render time.
- Lists are never `null` — use `[]`.
- `description` and `acceptance_criteria` are **always plain text**, never ADF.
- Every value is either **verbatim from Jira** or **explicitly empty**. No
  derived/guessed content in `JiraIssue`.

### 2.2 `PlanRequest` — what we send to the LLM

Not raw JSON to the model; a **deterministic, delimited text block** built from
`JiraIssue`, plus generation parameters. Its schema is conceptual:

```json
{
  "issue": "JiraIssue (normalised, above)",
  "options": {
    "plan_depth": "standard | detailed",
    "include_performance": true,
    "include_security": true,
    "include_accessibility": true,
    "max_test_cases": 40,
    "audience": "enterprise"
  }
}
```

### 2.3 `TestPlan` — the output contract (template-driven)

The document structure is **no longer hardcoded**. It is driven at runtime by
the user-provided files in `templates/`:

| File | Authority |
|---|---|
| `testplan_template.md` | **Required structure** — the outline the output must reproduce |
| `VWO_Test_Plan.md` | **Test-case table format + ID scheme** |

`plan_generator.outline_sections()` reads the template's numbered top-level
sections; `validate_plan()` checks the output against them. A built-in outline
is used only if no template file exists.

**Current required sections** (from the template):
```
1. Introduction        4. Change Management
2. Test Level          5. Test Planning
3. Test Reporting and Defect Tracking
6. Customer Validation Plan
```
The template's 31 numbered headings and 12 tables are all reproduced; each
`table:` line in the prompt states the exact columns for its section.

**Fixed test-case contract** (from the master):
- columns `| Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |`
- **"Actual Result" left blank** (filled at execution time)
- IDs `<PROJECT>-<AREA>-<NNN>_<T>`, T ∈ {P, N, B, E}; grouped into suites S1..Sn
- a requirement coverage matrix `| Requirement | Suites covering it | Status |`

**Meta** is emitted deterministically as an HTML provenance comment
(`<!-- Generated by … -->`); the template supplies its own title page.

**Prompt-budget invariant (hard).** Groq meters `openai/gpt-oss-120b` at
**8,000 tokens/minute** on the free tier, and only the **prompt** is metered
(`max_tokens` does not count). The template/master are therefore **condensed**
into a per-section structure digest + test-case format, never embedded
verbatim. Current prompt ≈ 3,300 tokens. See `findings.md` §12.2.

**Per-section content rules** (the template's tables are authoritative):
| Area | Must contain | Never contains |
|---|---|---|
| Introduction | overview, purpose, acronyms | invented business goals |
| Test Level | entry/exit table, test items, exclusions, pass/fail + suspension + regression criteria | criteria not tied to acceptance criteria |
| Reporting | metrics table `| Metric | Definition | Target | Report Cadence |`, defect tracking | vanity metrics with no target |
| Change Management | change workflow + impact analysis | — |
| Test Planning | roles, schedule, hardware, software, training, risks | invented dates/owners |
| Customer Validation | roles, schedule, environments, validation items, closure | — |
| Test Case Suites | tagged cases, one row per case, Actual Result blank | fabricated results |
| Coverage Matrix | `| Requirement | Suites covering it | Status |` | rows with no source |

### 2.4 `Config` — settings schema (mirrors sibling project)

```json
{
  "jira_email": "",
  "jira_api_token": "",
  "jira_base_url": "https://your-domain.atlassian.net",
  "jira_api_version": "3",
  "groq_api_key": "",
  "groq_model": "openai/gpt-oss-120b",
  "plan_depth": "standard"
}
```

Precedence (fixed): `defaults ← config/settings.json ← .env`. Secrets never
hardcoded, never logged.

---

## 3. Behavioral rules (how the system must act)

### 3.1 Generation rules (embedded as code constants, not templates)
- Output the **fixed section set** above, in order, as Markdown.
- Use **only** facts present in `JiraIssue`. If absent → write
  `Not specified` / `To be confirmed`.
- **Anti-hallucination:** never invent features, endpoints, environments,
  dates, owners, or numeric targets. Any inference is labelled
  `Inference (low confidence)`.
- **Coverage:** the traceability matrix covers **positive, negative, boundary,
  and exception** scenario types (per project taste).
- **Tone:** precise, enterprise QA documentation.
- **No preamble / no closing chatter** — the plan document only.

### 3.2 Determinism rules
- `temperature = 0.2` (as proven in the sibling project).
- Inputs are sorted before prompting (labels, components, subtasks by key) so
  the same ticket yields a stable prompt.
- The generator validates structural conformance post-hoc (all sections
  present, matrix non-empty); failure is an explicit error, not silent.

### 3.3 Error behavior
- User-facing errors are **typed and human-readable**, never raw tracebacks.
- `JiraError` and `LLMError` mirror the sibling project's taxonomy.
- If Jira is unreachable → do not call the LLM at all.
- If both LLMs fail → surface which one failed and why.

---

## 4. Architectural invariants (A.N.T. 3-layer)

Adopted from `BLAST.md`:

```
Layer 1  architecture/   Technical SOPs (Markdown) — the "how", human-readable
Layer 2  navigation      Reasoning/decision layer — routes data, calls tools
Layer 3  tools/          Deterministic Python — atomic, testable, .env + .tmp/
```

**Invariants (must never be violated):**
1. **I-1** Layers depend downward only: navigation → tools. Tools never call
   the navigation layer.
2. **I-2** Business logic is deterministic; the LLM only *generates prose for
   sections already defined by the schema*.
3. **I-3** All external I/O (Jira, Groq) is isolated in Layer 3.
4. **I-4** All intermediate files go in `.tmp/`; only finished deliverables are
   promoted out.
5. **I-5** Credentials live only in `.env` (gitignored) — never in code,
   commands, or logs.
6. **I-6** SOP-first: if behaviour changes, the SOP in `architecture/` updates
   before the code in `tools/`.
7. **I-7** Every tool is independently runnable and testable from the CLI.
8. **I-8** One schema per boundary; no layer reaches past its neighbour's
   contract.

---

## 5. As-built directory layout

```
chapter_07_Blast_Framework/Test_Plan_Agent/
├── app.py                   # Layer 2 — Streamlit UI (chat + settings)
├── tools/                   # Layer 3 — deterministic Python
│   ├── __init__.py
│   ├── config_manager.py    # defaults <- settings.json <- .env
│   ├── jira_client.py       # REST v3 fetch + ADF flatten -> JiraIssue
│   ├── groq_client.py       # Groq chat/completions + connection test
│   ├── template_loader.py   # templates/ -> outline, per-section structure, formats
│   └── plan_generator.py    # JiraIssue + template -> prompt -> Test Plan + validation
├── architecture/            # Layer 1 — SOPs (markdown)
│   ├── 01_jira_fetch.md
│   ├── 02_normalize_issue.md
│   └── 03_generate_test_plan.md
├── templates/               # user-provided reference files (read-only inputs)
│   ├── testplan_template.md # required document structure (authoritative outline)
│   └── VWO_Test_Plan.md     # master example: depth + test-case table format
├── phase0/                  # BLAST Protocol 0 memory (this folder)
│   ├── task_plan.md         # goals & checklists
│   ├── findings.md          # research
│   ├── progress.md          # running log
│   └── LLM.md               # THIS FILE (constitution)
├── .env.example             # documented vars, no secrets
├── .gitignore               # ignores .env, config/settings.json, .tmp/
├── requirements.txt
├── README.md
├── BLAST.md                 # master protocol (given)
└── config/settings.json     # runtime-persisted settings (gitignored)
```

> Layer 2 (Navigation) is realised by `app.py` plus the agent's own reasoning
> loop during a run; it selects which Layer-3 tool to invoke and in what order.

---

## 6. Technology decisions (rationale)

| Decision | Choice | Why |
|---|---|---|
| Language | Python 3.9+ | Sibling project proven; Streamlit-native |
| HTTP | `requests` | Already used & proven; simple sync semantics |
| Config | `python-dotenv` + JSON | Proven precedence model in sibling project |
| LLM | **Groq** `openai/gpt-oss-120b` | User-mandated engine (GPT-OSS 120B on Groq); fast + cheap |
| Prompt budget | Condensed template **digest** (~3.3k tokens), never full files | Groq free tier caps gpt-oss-120b at **8k TPM**; only the prompt is metered |
| Document structure | Driven by `templates/testplan_template.md` | User-supplied template is the authority; no code change to alter output shape |
| Output format | Markdown | Human-readable + machine-checkable structure |
| Doc delivery | On-screen + `.md` download | Portable; Confluence/Jira delivery deferred |

---

## 7. Discovery decisions — RESOLVED

The Phase-1 prompt answered the earlier open decisions. Recorded here so the
constitution reflects reality:

- **D-1 North Star → resolved:** a simple **Streamlit UI** (single screen,
  two panels). Implemented in `app.py`.
- **D-2 Delivery → resolved:** render the plan on-screen **and** offer a
  `.md` **download**. Writing back to Jira/Confluence/Slack is out of scope v1.
- **D-3 Source of truth → resolved:** a **single Jira ticket** (its subtasks,
  links, and comments are pulled in as context; epic-wide roll-up is not v1).
- **D-4 Credentials → confirmed:** the user configured Jira + Groq via the UI;
  both live connection tests pass and a live end-to-end run succeeded (see D-8).
- **D-5 Sections & tone → superseded by D-7:** the original 14-section list is
  retired in favour of the user's template. `SECTION_TITLES` was renamed to
  `DEFAULT_SECTION_TITLES` and now serves only as a no-template fallback.
- **D-6 LLM engine → resolved:** **Groq only** (`openai/gpt-oss-120b`). The
  Ollama-first strategy from v0.1 was dropped per the Phase-1 prompt.
- **D-7 Document structure → resolved:** driven by
  `templates/testplan_template.md` (structure) and `templates/VWO_Test_Plan.md`
  (test-case format). The original hardcoded 14-section contract is retired; it
  survives only as a fallback when no template file is present.
- **D-8 Live verification → done:** real Jira + Groq credentials confirmed
  working; live generation against `KAN-3` produced a 6-section template-shaped
  plan with 40–64 test cases. See `findings.md` §12.6.
