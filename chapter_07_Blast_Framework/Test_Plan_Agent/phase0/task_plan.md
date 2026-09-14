# task_plan.md — Goals, Phases & Checklists

> B.L.A.S.T. Protocol 0 artifact. This is the **single source of truth for
> scope and progress**. Nothing is marked ✅ until it is demonstrably verified.
>
> **Legend:** `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked

**Project:** Test Plan Creator from a Jira ID
**Folder:** `chapter_07_Blast_Framework/Test_Plan_Agent/`
**Protocol:** BLAST (Blueprint · Link · Architect · Stylize · Trigger)
**Current phase:** ✅ **Phases 0–4 complete + template rework** — prototype
delivered, template-driven, and verified **live** end-to-end against real Jira +
Groq (`KAN-3`). See `findings.md` §12.

---

## 1. North Star

> **Given a Jira issue ID, automatically produce a complete, enterprise-grade,
> traceable Test Plan document — deterministically, without inventing facts.**

One input → one test plan, through a simple UI. If we can point at a Jira key
and get a plan a QA lead would sign off on, the mission is complete.

---

## 2. Goals & Non-Goals

### Goals
- [x] G-1 Fetch a Jira issue by key via REST API v3 (auth: email + API token).
- [x] G-2 Normalise the raw Jira payload into a single `JiraIssue` schema,
      flattening ADF to plain text.
- [x] G-3 Generate a **Test Plan** driven by the user's template
      (`templates/testplan_template.md`), with test cases in the master's format.
- [x] G-4 Enforce anti-hallucination: facts only, missing data labelled
      `Not specified`, inferences labelled.
- [x] G-5 Guarantee determinism: stable prompt ordering + low temperature +
      structural validation.
- [x] G-6 LLM via **Groq** (`openai/gpt-oss-120b`) — *changed from Ollama-first
      per the Phase-1 prompt.*
- [x] G-7 Zero hardcoded secrets; `.env`-driven config.
- [x] G-8 Every tool independently runnable + testable.

### Non-Goals (explicitly out of scope for v1)
- [ ] NG-1 Executing tests / integrating with a test runner.
- [ ] NG-2 Writing the generated plan back to Jira/Confluence/Slack.
- [ ] NG-3 Multi-tenant auth / hosted service.
- [ ] NG-4 Epic-wide roll-up (v1 handles a single ticket + its children/links).

---

## 3. BLAST Phases → checklists

### 🟢 Protocol 0 — Initialization ✅
- [x] Create `task_plan.md` (this file)
- [x] Create `findings.md` (research + curl requests)
- [x] Create `progress.md` (running log)
- [x] Create `LLM.md` (constitution: schemas, rules, architecture)
- [x] Answer the Discovery Questions (§7 below)
- [x] Approve the Data Schema in `LLM.md` §2
- [x] Approve the Blueprint in §4 below

### 🔵 Phase 1 — B · Blueprint (Vision & Logic) ✅
- [x] DQ answers recorded (§7)
- [x] Define input schema `JiraIssue` (`LLM.md` §2.1)
- [x] Define output schema `TestPlan` + fixed section list (`LLM.md` §2.3)
- [x] Confirm section list & enterprise tone
- [x] Prior-art research (reused sibling `chapter_03_Jira_TestCase`)
- [x] Write `architecture/01_jira_fetch.md` (SOP)
- [x] Write `architecture/02_normalize_issue.md` (SOP)
- [x] Write `architecture/03_generate_test_plan.md` (SOP)
- [x] Blueprint sign-off (user instructed "do phase 1–4 in one go")

### 🔗 Phase 2 — L · Link (Connectivity) ✅ (code) / ⚠️ (live creds)
- [x] Provide `.env.example` (user supplies real values)
- [x] Build `tools/jira_client.py` with `test_connection()`
- [x] Build `tools/groq_client.py` with `test_connection()`
- [x] Wire both connection tests into the UI Settings panel
- [x] Offline handshake: normalisation + validation verified with fixtures
- [ ] ⚠️ Live Jira fetch → **needs real credentials** (user action)
- [ ] ⚠️ Live Groq generation → **needs real API key** (user action)
- [x] **Gate:** generation logic built only after the link contracts were fixed

### ⚙️ Phase 3 — A · Architect (3-Layer Build) ✅
- [x] Layer 1: three SOPs written in `architecture/`
- [x] Layer 3: `tools/config_manager.py` (defaults ← json ← env)
- [x] Layer 3: `tools/jira_client.py` (fetch + ADF flatten + error taxonomy)
- [x] Layer 3: `tools/groq_client.py` (chat + connection test)
- [x] Layer 3: `tools/plan_generator.py` (prompt → LLM → validate)
- [x] Fixed-section generation rules as code constants
- [x] Structural validator (all 14 sections present)
- [x] Traceability matrix required via prompt rules (AC → test type/coverage)
- [x] Groq orchestration
- [x] UI entry point (`app.py`)
- [ ] Route outputs through `.tmp/` — **simplified**: plan is returned in-memory
      and offered as a `.md` download (no `.tmp/` promotion needed in v1)

### ✨ Phase 4 — S · Stylize (Refinement & UI) ✅
- [x] Markdown layout (headings, tables, consistent spacing) via prompt rules
- [x] Deterministic metadata header block (key, URL, timestamp, model)
- [x] Streamlit single-screen, two-panel layout
- [x] Settings panel with Jira + Groq fields and connection tests
- [x] `.md` download button
- [ ] Present stylized output to the user for live feedback

### 🚀 Phase 5 — T · Trigger (Automation) ✅
- [x] One command runs: `streamlit run app.py`
- [x] Full Jira→plan run verified live (`KAN-3`)
- [ ] (Optional) watch/schedule hook for "new ticket → plan"

### 🔁 Phase 6 — Template Rework (post-Phase-4 feedback) ✅
Triggered by feedback *"the plan is not detailed enough"* + two user reference files.
- [x] Add `templates/testplan_template.md` + `templates/VWO_Test_Plan.md`
- [x] New `tools/template_loader.py` — outline, per-section structure, master digest
- [x] Rewire `plan_generator` to the template outline + master test-case format
- [x] Fix thin output: per-section minimums, 8+ suites / 25+ cases (detailed)
- [x] Fix heading hierarchy (`#` title, `##` sections, `###` x.y, `####` x.y.z)
- [x] Fix table placement — each template table attached to its own heading
- [x] Respect Groq's 8k TPM limit (condensed prompt ≈3.3k tokens) + 413 handling
- [x] UI: plan-depth selector + template-status caption
- [x] Verify live end-to-end (`KAN-3`): 40–64 test cases, 0 missing sections

---

## 4. Blueprint (as-built)

```
INPUT:  Jira issue key parsed from the user's prompt (e.g. "fetch VWO-49 ...")
          │
          ▼
[tools/jira_client.py]
  GET /rest/api/3/issue/{key}?fields=...    (Basic auth)
  GET /rest/api/3/issue/{key}/comment
  GET /rest/api/3/field                      (custom-field catalogue, cached)
          │
          ▼  normalise + ADF→text
    JiraIssue JSON  (LLM.md §2.1)
          │
          ▼
[tools/plan_generator.py]
  build deterministic prompt (rules = code constants)
  call Groq /chat/completions  (openai/gpt-oss-120b, temp 0.2)
          │
          ▼  raw markdown
  validate: all 14 sections present?
          │
          ▼
    app.py: render on screen + offer TestPlan_VWO-49.md download
```

**Layer mapping:** `app.py` (Layer 2 navigation) → `tools/*` (Layer 3). SOPs in
`architecture/` (Layer 1) describe the why/how and are updated before code.

---

## 5. Definition of Done

- [x] Modules import and byte-compile cleanly (`compileall` → COMPILE_OK)
- [x] Output contract enforced: 14 sections validated (`validate_plan`)
- [x] Prompt requires every section to cite Jira content or say `Not specified`
- [x] Traceability matrix mandated by prompt rules
- [x] Anti-hallucination rules embedded (facts-only + `Inference (low confidence)`)
- [x] Re-running yields a structurally identical plan (temp 0.2 + sorted inputs)
- [x] No secrets in code/logs; `.env` + `settings.json` gitignored
- [x] `progress.md` records each step, error, and result
- [x] Live end-to-end run on a real ticket (`KAN-3`) — 22–28k chars, 40–64 cases
- [x] Output follows the user's template structure with tables correctly placed
- [x] Prompt stays within Groq's 8k TPM limit (asserted in the offline test suite)

---

## 6. Milestones

| # | Milestone | Phase | Status |
|---|---|---|---|
| M0 | Protocol 0 artifacts created | 0 | `[x]` |
| M1 | Discovery answers + schema/blueprint approved | 0→1 | `[x]` |
| M2 | Jira/Groq link code + connection tests built | 2 | `[x]` |
| M3 | `JiraIssue` normalisation verified (fixtures) | 2/3 | `[x]` |
| M4 | Test-plan generator + validator built | 3 | `[x]` |
| M5 | Anti-hallucination + determinism rules encoded | 3 | `[x]` |
| M6 | UI stylized (two-panel, settings, download) | 4 | `[x]` |
| M7 | App runs locally (HTTP 200) | 4 | `[x]` |
| M8 | Live end-to-end run on a real ticket | 5 | `[x]` |
| M9 | Template-driven structure + depth rework | 6 | `[x]` |

---

## 7. Discovery Questions — ANSWERS (from the Phase-1 prompt)

1. **North Star** → A **simple UI**: user types "fetch this Jira and create a
   test plan"; the app fetches Jira and generates the plan automatically.
2. **Integrations** → **Jira** (API email + token, with a *Test connection*
   button) and **Groq** (API key, model `openai/gpt-oss-120b`, with a *Test
   connection* button).
3. **Source of Truth** → a single Jira issue (subtasks/links/comments pulled in
   as context).
4. **Delivery Payload** → rendered in the UI **and** downloadable as `.md`.
5. **Behavioral Rules** → enterprise QA tone; fixed 14-section plan; facts only;
   missing data labelled `Not specified`.

---

## 8. Risks (top 5 — full list in findings.md §10)

| ID | Risk | Mitigation | Status |
|---|---|---|---|
| R-1 | Hallucinated requirements in the plan | Facts-only prompt + `Not specified` labelling | mitigated |
| R-4 | Jira search API deprecation | Only single-issue fetch is used in v1 | n/a v1 |
| R-3 | Site-specific custom fields | Runtime field-catalogue discovery | mitigated |
| R-5 | Jira rate limiting | Single fetch; friendly 429 message | monitored |
| R-6 | Secret leakage | `.env` + `config/settings.json` gitignored | mitigated |

---

## 9. Change Log

| Date | Change | By |
|---|---|---|
| 2026-09-13 | Protocol 0 initialized; all four artifacts created | System Pilot |
| 2026-09-13 | Phases 1–4 implemented: tools, UI, docs; verified offline; app runs locally | System Pilot |
| 2026-09-13 | Template rework: `template_loader` + template-driven generation; live E2E verified on KAN-3 | System Pilot |
