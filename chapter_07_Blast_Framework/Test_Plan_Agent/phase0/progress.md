# progress.md — Running Activity Log

> B.L.A.S.T. Protocol 0 artifact. Append-only log of **what was done**, every
> **error encountered**, and every **result observed**. Short interval logs
> (10 / 30 / 60 min) so nothing is lost between sessions.
>
> **Format:** `[YYYY-MM-DD HH:MM TZ] · TAG · entry`
> **Tags:** `DONE` · `ERR` · `RESULT` · `DECISION` · `BLOCK` · `TODO`

**Project:** Test Plan Creator from a Jira ID
**Folder:** `chapter_07_Blast_Framework/Test_Plan_Agent/`
**All times IST (+05:30)** unless stated.

---

## Session 1 — Protocol 0 Initialization · 2026-09-13

### 19:05 — START
- `DONE` Opened the project brief (`Prompt_used.md`) and master protocol
  (`BLAST.md`).
- `DECISION` Scope chosen: **Protocol 0 only** — create the four memory files.
  No code in `tools/` yet (BLAST forbids it until Protocol 0 exits).

### 19:06 — Reconnaissance
- `DONE` Listed `chapter_07_Blast_Framework/` → found only
  `Test_Plan_Agent/{BLAST.md, Prompt_used.md}`. Confirmed no existing code here.
- `RESULT` So this is a greenfield build; every artifact is new.

### 19:07 — Reuse discovery (key finding)
- `DONE` Read the sibling project `chapter_03_Jira_TestCase/` (7 files:
  `app.py`, `jira_client.py`, `llm_handler.py`, `config_manager.py`,
  `plan.md`, `README.md`, `.env.example`).
- `RESULT` A **working Jira REST v3 client already exists** — basic auth,
  ADF→plain-text flattening, 401/403/404/timeout error taxonomy, base-URL
  normalisation. Also a proven **Ollama-first → Groq-fallback** LLM pattern.
- `DECISION` Reuse those patterns rather than reinvent. The new work is the
  **test-plan schema + deterministic generation**, not Jira connectivity.

### 19:08 — Artifacts written
- `DONE` Created `findings.md` — Jira API research, exact curl requests
  (fetch issue, filtered fields, `expand=renderedFields`, JQL children, search,
  comments, attachments, field catalogue), ADF parsing notes, error taxonomy,
  rate-limit/pagination findings, LLM strategy, risks.
- `DONE` Captured system timestamp: **2026-09-13 19:08:07 +05:30**.
- `DONE` Created `LLM.md` — the constitution: `JiraIssue` / `PlanRequest` /
  `TestPlan` / `Config` JSON schemas, 14-section output contract, generation &
  determinism rules, 8 architectural invariants, directory layout, tech
  decisions, open decisions D-1..D-5.
- `DONE` Created `task_plan.md` — North Star, goals/non-goals, per-phase
  checklists, blueprint, Definition of Done, milestones, discovery blockers,
  risk register.
- `DONE` Created `progress.md` (this file).
- `RESULT` Protocol 0 file set complete: `task_plan.md`, `findings.md`,
  `progress.md`, `LLM.md` (the brief's rename of BLAST's `gemini.md`).

### 19:09 — Status snapshot
- `BLOCK` Execution is halted by design. Three gates must clear before any
  Layer-3 tool is written:
  1. Discovery Questions answered (`task_plan.md` §7)
  2. Data schema approved (`LLM.md` §2)
  3. Blueprint approved (`task_plan.md` §4)
- `TODO` Awaiting user answers to DQ-1..DQ-5.

---

## Interval log (continue appending)

### Template — copy for each entry
```
### HH:MM — <short title>
- `DONE`   <what was done>
- `ERR`    <what failed / error text>
- `RESULT` <observable outcome>
- `DECISION` <choice + reason>
- `BLOCK`  <what is stopping progress>
- `TODO`   <next action>
```

### Placeholder — next check-in (10/30/60 min cadence)
- `TODO` [ ] Answer Discovery Questions DQ-1..DQ-5
- `TODO` [ ] Approve `JiraIssue` + `TestPlan` schemas
- `TODO` [ ] Approve Blueprint
- `TODO` [ ] Then: Phase 2 Link handshake (live Jira fetch)

---

## Error ledger

| Time | Where | Error | Cause | Resolution | Status |
|---|---|---|---|---|---|
| — | — | — | — | — | *(none yet)* |

---

## Decision log

| # | Time | Decision | Rationale |
|---|---|---|---|
| AD-1 | 19:05 | Protocol 0 documents only; no code yet | BLAST Protocol 0 forbids `tools/` scripts before sign-off |
| AD-2 | 19:07 | Reuse chapter-3 Jira client & LLM-fallback patterns | Proven working in this repo; avoids reinventing |
| AD-3 | 19:08 | Name the constitution `LLM.md` (not `gemini.md`) | Explicit project brief overrides BLAST default |
| AD-4 | 19:08 | Output = fixed 14-section Markdown test plan | Deterministic, machine-checkable, enterprise tone |
| AD-5 | 19:08 | Target `/rest/api/3/search/jql`, fall back to `/search` | Atlassian is deprecating the legacy search endpoint |

---

## Metrics

| Metric | Value |
|---|---|
| Artifacts created | 4 (`task_plan.md`, `findings.md`, `progress.md`, `LLM.md`) |
| Tools written | 0 *(halted — correct for Protocol 0)* |
| Blockers open | 1 (Discovery answers) |
| Milestones complete | M0 |

---

## Session 2 — Phases 1–4 Implementation · 2026-09-13

### 19:10 — Phase 1 (Blueprint)
- `DONE` Read the Phase-1 brief
  (`Promt_Used_for_Phase1_Actual_Creation.md`).
- `DECISION` North Star resolved: **Streamlit UI** → fetch Jira by ID → generate
  a Test Plan automatically; Settings must show Jira + Groq and **test both
  connections**.
- `DECISION` LLM engine is **Groq only**, default `openai/gpt-oss-120b`
  (the "OpenGPT 120B" the user specified). Ollama dropped.
- `DONE` Wrote Layer-1 SOPs (SOP-before-code, per BLAST):
  `architecture/01_jira_fetch.md`, `02_normalize_issue.md`,
  `03_generate_test_plan.md`.

### 19:25 — Phase 2/3 (Link + Architect)
- `DONE` `tools/config_manager.py` — defaults ← `config/settings.json` ← `.env`.
- `DONE` `tools/jira_client.py` — REST v3 fetch, ADF→text, comments,
  field-catalogue acceptance-criteria discovery, `test_connection()`
  (via `/rest/api/3/myself`), typed `JiraError`s, `parse_issue_key()`.
- `DONE` `tools/groq_client.py` — `/chat/completions` + `test_connection()`
  (via `/openai/v1/models`, also checks the model exists), typed `GroqError`.
- `DONE` `tools/plan_generator.py` — deterministic prompt builder, 14-section
  contract, `validate_plan()`, deterministic metadata header, `chat` call.
- `DONE` `app.py` — two-panel Streamlit UI: chat/Send + plan output/download on
  the left; Settings (Jira + Groq + both connection tests + Save) on the right.
- `DONE` Added `requirements.txt`, `.env.example`, `.gitignore`, `README.md`.

### 19:55 — Verification
- `RESULT` `python -m compileall tools app.py` → **COMPILE_OK**.
- `RESULT` Offline tool smoke test (8 checks) → **ALL_SMOKE_TESTS_PASSED**:
  key parsing, config defaults, prompt build, `validate_plan` (14 sections +
  partial), generation vs a fake client, ADF flattening, bad-key rejection,
  missing-key rejection.
- `ERR` While testing the UI buttons: clicking **Test Groq Connection** with an
  empty API key raised an **uncaught `GroqError`** (the app would show a
  traceback). Cause: `GroqClient._headers()` raised *before* the guarded
  `requests` call, so the `except` never caught it.
- `DONE` Fixed `groq_client.test_connection()` to resolve headers inside a
  guarded block and return `(False, message)`.
- `RESULT` Headless Streamlit `AppTest` → **UI_SMOKE_TESTS_PASSED**: app runs
  with no exception; all 6 text inputs and 4 buttons present; the no-ticket path
  and the not-configured path both show friendly `st.error` messages.
- `RESULT` Connection-button test → **CONNECTION_TEST_SMOKE_PASSED**: empty
  Jira → "Jira base URL is not configured."; empty Groq → "Groq API key is not
  configured."; Save Settings → success. No exceptions.

### 20:04 — Local run
- `DONE` Started `streamlit run app.py --server.headless true --server.port 8501`.
- `RESULT` `http://localhost:8501` returned **HTTP 200** with the Streamlit
  marker. App is serving.
- `DONE` Stopped the server (port released) and removed the test-created
  `config/settings.json` so the project is clean.

### 20:05 — Status
- `DONE` Updated `task_plan.md`, `findings.md`, `LLM.md`, `progress.md`.
- `BLOCK` Live end-to-end (real Jira fetch + real Groq generation) **has not
  been exercised** — no credentials were supplied. Awaiting user keys.
- `TODO` User: open Settings, enter Jira email/token/URL + Groq key, run both
  connection tests, Save, then send `fetch <TICKET>`.

---

## Interval log (continue appending)

### Template — copy for each entry
```
### HH:MM — <short title>
- `DONE`   <what was done>
- `ERR`    <what failed / error text>
- `RESULT` <observable outcome>
- `DECISION` <choice + reason>
- `BLOCK`  <what is stopping progress>
- `TODO`   <next action>
```

### Next check-in
- `TODO` [ ] Live Jira connection test with real credentials
- `TODO` [ ] Live Groq connection test with real key
- `TODO` [ ] First real ticket → generated test plan review
- `TODO` [ ] Apply any feedback; re-verify determinism

---

## Error ledger

| Time | Where | Error | Cause | Resolution | Status |
|---|---|---|---|---|---|
| 19:55 | `groq_client.test_connection()` | Uncaught `GroqError` on empty key | `_headers()` raised outside the guarded call | Resolve headers inside a guarded block; return `(False, msg)` | fixed |

---

## Decision log

| # | Time | Decision | Rationale |
|---|---|---|---|
| AD-1 | 19:05 | Protocol 0 documents only; no code yet | BLAST Protocol 0 forbids `tools/` scripts before sign-off |
| AD-2 | 19:07 | Reuse chapter-3 Jira client & LLM-fallback patterns | Proven working in this repo; avoids reinventing |
| AD-3 | 19:08 | Name the constitution `LLM.md` (not `gemini.md`) | Explicit project brief overrides BLAST default |
| AD-4 | 19:08 | Output = fixed 14-section Markdown test plan | Deterministic, machine-checkable, enterprise tone |
| AD-5 | 19:08 | Target `/rest/api/3/search/jql`, fall back to `/search` | Atlassian is deprecating the legacy search endpoint |
| AD-6 | 19:12 | **Groq only**, model `openai/gpt-oss-120b`; drop Ollama | Phase-1 prompt mandates Groq + "OpenGPT 120B" |
| AD-7 | 19:15 | UI = single screen, two panels (chat + settings) | User asked for a "very simple UI" + a settings phase |
| AD-8 | 19:40 | Connection tests implemented in each tool, exposed as UI buttons | User explicitly asked to allow testing Jira and Groq |
| AD-9 | 20:04 | Stop the dev server after verification | Do not leave ports occupied |

---

## Metrics

| Metric | Session 1 | Session 2 |
|---|---|---|
| Artifacts created | 4 | 13 (4 tools + SOPs + UI + support files + docs updated) |
| Tools written | 0 | 4 (`config_manager`, `jira_client`, `groq_client`, `plan_generator`) |
| Tests run | 0 | 4 suites, **all passed** |
| Blockers open | 1 | 1 (live credentials) |
| Milestones complete | M0 | M0–M7 |

---

## Session 3 — Template Rework · 2026-09-13

### 20:50 — Feedback + templates
- `TODO` User feedback: *"the test plan created for my Jira is not detailed enough."*
- `DONE` User provided two reference files; verified in `templates/`:
  `testplan_template.md` (formal corporate template) and `VWO_Test_Plan.md`
  (master example).
- `DECISION` Template = authoritative **structure**; master = authoritative
  **test-case format**. Also raised Groq `max_tokens` 6000 → 16000.

### 20:55 — Phase 6 build
- `DONE` New `tools/template_loader.py` — reads both files; exposes
  `required_sections()`, `all_sections()`, `outline_text()`, `structure_digest()`,
  `master_digest()`.
- `DONE` Rewired `tools/plan_generator.py`: replaced the hardcoded 14-section
  contract with the template outline; added per-section minimums; added an
  8+ suites / 25+ case requirement for `detailed`.
- `DONE` UI: added a **Plan depth** selector (standard/detailed) and a
  template-status caption in Settings.
- `DONE` `groq_client.chat()` default `max_tokens` → 16000.

### 21:00 — First live end-to-end run → ❌ ERROR
- `DONE` Confirmed live credentials: Jira OK (`Shreya Sen`), Groq OK
  (`openai/gpt-oss-120b`).
- `ERR` **HTTP 413** on the live Groq call:
  `Request too large for model openai/gpt-oss-120b … tokens per minute (TPM): Limit 8000, Requested 12302`.
  Cause: embedding the **full** template + master verbatim ballooned the prompt
  to ~12.3k tokens.

### 21:02 — Root-cause probe
- `DONE` Empirical probe: tiny prompt with `max_tokens=16000` → **HTTP 200**.
- `RESULT` **`max_tokens` does not count toward TPM** — only the *prompt* is
  metered. So: shrink the prompt, keep the output budget large.

### 21:05 — Fix: condensed, derived prompt
- `DONE` Replaced verbatim embedding with two derived artefacts:
  `structure_digest()` (per-section headings + the exact table each section
  expects + placeholder guidance, ~5.6 KB) and `master_digest()` (test-case
  table header + ID scheme, ~0.5 KB).
- `RESULT` Prompt fell **12,302 → ~3,286 tokens** (under the 8,000 ceiling).
- `DONE` Added explicit **HTTP 413** handling in `groq_client` with an
  actionable message (free-tier TPM, upgrade advice).

### 21:07 — Live run #2 → structural defects found
- `RESULT` Generation succeeded: 28,380 chars, 4,653 words, 64 test-case rows.
- `ERR` Two structural defects:
  1. **Tables misfiled** — a dependency table under *2.1 Entry and Exit*, a
     metrics table under *5.2 Test Schedule* (only global formats were given).
  2. **Heading hierarchy** — every section emitted as `#` H1.
- `DONE` Fixes: each template table is now attached to *its own* heading
  ("use that table there and ONLY there"); added explicit heading-level rule.
- `DONE` Smaller fixes: dropped the empty `Appendix` from required sections
  (false warning); deduped repeated digest lines; directed metrics to the
  reporting section with `| Metric | Definition | Target | Report Cadence |`.

### 21:09 — Live run #3 (final) ✅
- `RESULT` **22,300 chars, 3,482 words, 40 test-case rows, 0 missing sections,
  14.4 s.** Verified structure: 6 `##` sections, 21 `###` sub-sections, 8 test
  suites, and correct tables under 2.1 / 5.1 / 5.2 / 5.5 / 6.1 / coverage matrix.
- `RESULT` `compileall` OK; offline suite **ALL_TEMPLATE_TESTS_PASSED**
  (including a prompt-size guard asserting < ~7k tokens).

### 21:10 — Documentation sync
- `DONE` Updated `findings.md` (§12), `LLM.md` (§2.3, §5, §6, §7), `task_plan.md`
  (goals, Phase 6, DoD, milestones M8–M9, change log), `progress.md` (this log).
- `RESULT` Phase 0 files are back in sync with the code.

---

## Interval log (continue appending)

### Template
```
### HH:MM — <short title>
- `DONE`   <what was done>
- `ERR`    <what failed / error text>
- `RESULT` <observable outcome>
- `DECISION` <choice + reason>
- `BLOCK`  <what is stopping progress>
- `TODO`   <next action>
```

### Next check-in
- `TODO` [ ] User reviews the KAN-3 plan output and gives feedback
- `TODO` [ ] Consider pacing/multi-call generation if deeper output is needed
- `TODO` [ ] Re-run on a second ticket to confirm stability

---

## Error ledger

| Time | Where | Error | Cause | Resolution | Status |
|---|---|---|---|---|---|
| 19:55 | `groq_client.test_connection()` | Uncaught `GroqError` on empty key | `_headers()` raised outside the guarded call | Resolve headers in a guarded block | fixed |
| 21:00 | Groq `/chat/completions` | **HTTP 413** — 12,302 vs 8,000 TPM | Full template + master embedded verbatim | Condense to derived digests (~3.3k tokens) | fixed |
| 21:07 | Generated plan | Tables under wrong headings | Only global table formats given | Attach each table to its own heading | fixed |
| 21:07 | Generated plan | All sections emitted as `#` H1 | No heading-level rule | Explicit `#`/`##`/`###`/`####` rule | fixed |
| 21:07 | `validate_plan` | Spurious "Appendix omitted" warning | Empty template heading was required | Exclude un-numbered headings | fixed |

---

## Decision log (additions)

| # | Time | Decision | Rationale |
|---|---|---|---|
| AD-10 | 20:52 | Template = structure authority; master = test-case-format authority | User asked to use both files "primarily" |
| AD-11 | 21:05 | Condense template/master into derived digests rather than embed | Hard 8k TPM ceiling on Groq free tier |
| AD-12 | 21:05 | Keep `max_tokens=16000` despite the 413 | Probe proved only the prompt is metered |
| AD-13 | 21:07 | Validate only numbered top-level sections | Avoid false warnings on empty Appendix |

---

## Metrics

| Metric | Session 2 | Session 3 |
|---|---|---|
| Tools written | 4 | +1 (`template_loader`) |
| Live E2E runs | 0 | 3 (1 failed → 2 succeeded) |
| Best output | n/a | 28,380 chars · 64 test cases |
| Prompt size | n/a | ≈3,286 tokens (limit 8,000) |
| Errors found & fixed | 1 | 4 |
| Milestones complete | M0–M7 | M0–M9 |

---

## Session 4 — Housekeeping · 2026-09-13

### 21:20 — Group Protocol 0 artifacts
- `DONE` Moved the four BLAST Protocol 0 files into a dedicated folder:
  `phase0/{task_plan.md, findings.md, progress.md, LLM.md}`.
- `DONE` Updated cross-references from outside the folder: `README.md` (project
  memory + §12.2 pointer) and `templates/README.md` (§12.2 pointer), plus the
  layout block in `LLM.md`.
- `RESULT` No code impact — nothing in `app.py` or `tools/` reads these files.
  Intra-folder references stay valid (same directory).
- `DECISION` Left `BLAST.md` untouched — it is the given master protocol; its
  `task_plan.md` mentions describe the protocol, not project paths.

