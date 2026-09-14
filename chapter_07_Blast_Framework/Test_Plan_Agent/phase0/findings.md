# findings.md — Research & Discoveries

> B.L.A.S.T. Protocol 0 artifact. This file records **what we learned**, the
> **exact Jira requests** we will use, and the **constraints** that shape the
> Test Plan Creator. It is written before any code, per BLAST Protocol 0.

**Project:** Test Plan Creator from a Jira ID
**Location:** `chapter_07_Blast_Framework/Test_Plan_Agent/`
**Author:** System Pilot
**Started:** 2026-09-13 19:08 IST

---

## 1. Objective (restated)

Given a **Jira issue key** (e.g. `VWO-49`), fetch the issue from Jira and
generate a **complete, enterprise-grade Test Plan document** — not a single
flat table of test cases, but a structured plan (scope, strategy, environments,
entry/exit criteria, risks, traceability to requirements, metrics).

This is deliberately more ambitious than `chapter_03_Jira_TestCase`, which
produces a Markdown **test-case table**. Here we produce a **test plan**.

---

## 2. Discovery: what already exists in this repo

We are not starting from zero. The repository already contains a working Jira
integration we can mine for proven patterns.

| Artifact | Path | What we can reuse |
|---|---|---|
| Jira REST v3 client | `chapter_03_Jira_TestCase/jira_client.py` | Basic-auth request, ADF→plain-text flattening, error taxonomy (401/403/404/timeout), base-URL normalisation |
| LLM fallback handler | `chapter_03_Jira_TestCase/llm_handler.py` | Ollama-first → Groq-fallback pattern, prompt-as-code rules, `LLMError` taxonomy |
| Config manager | `chapter_03_Jira_TestCase/config_manager.py` | Precedence `defaults ← settings.json ← .env`, no hardcoded secrets |
| Prior plan | `chapter_03_Jira_TestCase/plan.md` | Approved approach for the sibling (test-case) project |
| Master protocol | `Test_Plan_Agent/BLAST.md` | The build methodology we must follow |

**Key deduction:** the Jira connectivity problem is already solved in this repo.
The new work is (a) shaping a **test-plan JSON schema**, and (b) engineering a
**deterministic plan generator** with strict output rules.

---

## 3. How we fetch data from Jira (the core finding)

### 3.1 Authentication

Jira Cloud uses **HTTP Basic auth with an Atlassian API token**:

- Username = the Atlassian account **email**
- Password = an **API token** (created at
  `https://id.atlassian.com/manage-profile/security/api-tokens`) — *not* the
  account password.

Header form: `Authorization: Basic base64(email:api_token)`.
In `curl`, `-u "email:token"` produces this automatically.

> `requests` equivalent: `requests.get(url, auth=(email, token))`.

### 3.2 The endpoint we need — fetch one issue

```
GET {base_url}/rest/api/3/issue/{issueKey}
```

This is exactly what `chapter_03_Jira_TestCase/jira_client.py` already calls,
and it is confirmed working there. We will keep REST **v3** (Cloud). For Jira
Server/Data Center the path is `/rest/api/2/issue/{key}` — we will treat v3 as
the target and note v2 as a compatibility toggle.

### 3.3 curl — minimal fetch (exactly what we will use)

```bash
curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Accept: application/json" \
  "$JIRA_BASE_URL/rest/api/3/issue/PROJ-123"
```

### 3.4 curl — fetch only the fields a test plan needs (recommended)

A test plan needs structure: type, status, priority, components, fix versions,
labels, assignee, reporter, links, and acceptance criteria. Request exactly
those to keep the payload small and deterministic:

```bash
curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Accept: application/json" \
  -G \
  --data-urlencode "fields=summary,description,issuetype,status,priority,labels,components,fixVersions,assignee,reporter,issuelinks,parent,created,updated,duedate" \
  "$JIRA_BASE_URL/rest/api/3/issue/PROJ-123"
```

### 3.5 curl — include rendered fields (human-readable HTML of description)

Useful as a fallback when ADF flattening is imperfect:

```bash
curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Accept: application/json" \
  -G --data-urlencode "expand=renderedFields" \
  "$JIRA_BASE_URL/rest/api/3/issue/PROJ-123"
```

### 3.6 curl — subtasks / children / linked issues (scope discovery)

A test plan's **scope** is derived from the issue plus its children. Pull
subtasks and issue links:

```bash
# Children of an epic / parent, via JQL:
curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Accept: application/json" \
  -G \
  --data-urlencode 'jql=parent = PROJ-123 ORDER BY created ASC' \
  --data-urlencode 'maxResults=100' \
  --data-urlencode 'fields=summary,status,issuetype,priority,components,fixVersions' \
  "$JIRA_BASE_URL/rest/api/3/search/jql"
```

> **Finding / gotcha:** Atlassian is migrating the search API. The legacy
> `GET /rest/api/3/search` is being deprecated in favour of
> `GET /rest/api/3/search/jql`. We will target `/rest/api/3/search/jql` and
> fall back to `/rest/api/3/search` on HTTP 404/410.

### 3.7 curl — comments (often carry clarification / acceptance notes)

```bash
curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Accept: application/json" \
  -G --data-urlencode "maxResults=50" \
  "$JIRA_BASE_URL/rest/api/3/issue/PROJ-123/comment"
```

### 3.8 curl — attachment list (source docs, mockups, specs)

```bash
curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Accept: application/json" \
  "$JIRA_BASE_URL/rest/api/3/issue/PROJ-123?fields=attachment"
```

---

## 4. Finding: parsing the description (Atlassian Document Format)

Modern Jira Cloud does **not** return `description` as a string. It returns an
**ADF document**:

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    { "type": "paragraph", "content": [ { "type": "text", "text": "..." } ] },
    { "type": "bulletList", "content": [ { "type": "listItem", "content": [ ... ] } ] }
  ]
}
```

**Decision:** reuse the recursive ADF walker from
`chapter_03_Jira_TestCase/jira_client.py` (`_adf_to_lines` / `_node_text`).
It already handles `paragraph`, `heading`, `bulletList`, `orderedList`,
`listItem`, `codeBlock`, `blockquote`, `table`, `mediaSingle`, `rule`,
`hardBreak`, `inlineCard`, `mention`, and text marks (`code`, `strong`).
Rather than reinvent it, the Test Plan Agent will lift this into a shared
`jira_client` module in Layer 3 (`tools/`).

**Unverified / to confirm:** whether the target Jira site uses custom fields for
acceptance criteria. The chapter-3 code guesses by scanning field keys whose
name contains `"acceptance"`. This is a heuristic, not a guarantee — it must be
labelled as such (see `LLM.md > anti-hallucination`).

---

## 5. Finding: custom fields (acceptance criteria, story points, sprint)

Custom fields are not named in responses — they appear as
`customfield_10016`, `customfield_10020`, etc., and their **meaning is
site-specific**. To resolve names we would need:

```bash
# Field catalogue (id -> name -> schema)
curl -sS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -H "Accept: application/json" \
  "$JIRA_BASE_URL/rest/api/3/field"
```

**Decision:** do **not** hardcode custom-field IDs. Discover the field whose
`name` matches `/acceptance criteria/i` at runtime (cache the catalogue), and
otherwise fall back to scanning the issue's own fields. Mark anything found
this way as *inferred*.

---

## 6. Finding: error taxonomy to handle

Extracted from the proven chapter-3 implementation:

| Condition | HTTP | User-facing message | Retry? |
|---|---|---|---|
| Bad email/token | 401 / 403 | "Jira rejected the credentials" | No |
| Ticket missing | 404 | "Ticket 'X' was not found on this site" | No |
| Bad project key | 400 | Jira error text (first 300 chars) | No |
| Rate limited | 429 | Back off, honour `Retry-After` | Yes (bounded) |
| Jira outage | 5xx | "Jira returned HTTP 5xx" | Yes (bounded) |
| DNS/TLS/VPN | — | "Could not reach Jira at <url>" | No |
| Slow network | — | "Timed out connecting to Jira" | Once |
| Non-JSON body | 200 | "unreadable (non-JSON) response" | No |

**Timeouts used by the proven client:** `(connect=5s, read=30s)`. We keep these.

---

## 7. Finding: rate limits & pagination

- Jira Cloud enforces per-tenant rate limits; responses include
  `X-RateLimit-*` headers and may return **429** with `Retry-After`.
  **Rule:** one issue fetch per request + bounded exponential backoff; never
  hammer.
- Search endpoints paginate: `maxResults` (cap 100), and either
  `startAt` (legacy) or `nextPageToken` (`/search/jql`). We must follow the
  cursor until exhausted, with a hard page cap.

---

## 8. Finding: LLM strategy (reuse the proven fallback)

The sibling project proved a **local-first** strategy that we adopt unchanged:

1. **Ollama first** — `POST {ollama_url}/api/chat`, `stream=false`,
   `temperature≈0.2`, short connect timeout so fallback is snappy.
2. **Groq fallback** — `POST https://api.groq.com/openai/v1/chat/completions`
   with `Authorization: Bearer …`.
3. If both fail → typed, user-presentable error (no traceback).

**Why deterministic matters here (BLAST "Architecture" principle):** the LLM is
probabilistic; a *test plan* must be repeatable. So the generator must be
constrained to a **strict, machine-checkable Markdown structure** and fed only
facts from Jira — missing data must be labelled, never invented.

---

## 9. Constraints & open questions (BLOCKERS for Protocol 0 sign-off)

Per BLAST Protocol 0 we **halt** until these are resolved:

1. **North Star outcome** — is the deliverable (a) a Markdown test plan file on
   disk, (b) a Streamlit UI like chapter 3, or (c) both? *(assumed: Markdown
   first, UI later)*
2. **Delivery payload** — where should the generated plan be delivered:
   local `.md` file, Jira comment, Confluence page, or Slack? *(assumed: local
   `.md` in `.tmp/` then promoted)*
3. **Source of truth** — one Jira ticket, or a Jira **epic + children**? Scope
   breadth changes the whole design. *(assumed: single ticket first)*
4. **Integrations & keys** — do we have a live Jira site + API token, Ollama
   running, and/or a Groq key available for verification?
5. **Behavioral rules** — required section list & tone for the plan
   (enterprise tone is implied by the sibling project / taste profile).

---

## 10. Risks

- **R-1 Hallucinated requirements.** LLM may invent scope. *Mitigation:*
  strict "facts only" prompt + explicit `Not specified` labelling.
- **R-2 ADF edge cases.** Unknown node types could drop content.
  *Mitigation:* reuse the tested walker; ignore-unknown is already handled.
- **R-3 Custom-field drift.** Site-specific field IDs. *Mitigation:* runtime
  field-catalogue discovery, no hardcoding.
- **R-4 Search API migration.** `/search` deprecation. *Mitigation:* target
  `/search/jql`, fall back on 404/410.
- **R-5 Rate limiting.** *Mitigation:* bounded backoff, honour `Retry-After`.
- **R-6 Secret leakage.** *Mitigation:* `.env` + `.tmp/` gitignored; no secrets
  in code or logs.

---

## 11. Phase 1–4 execution findings (2026-09-13)

These are findings discovered **while building and verifying**, not before.

### 11.1 LLM decision changed: Groq only (no Ollama)
The user's Phase-1 prompt **overrode** the earlier Ollama-first plan:
> "LLM connection that we will be using is GROq.com … an open GPT 120 billion
> parameter."

**Resolved:** use **Groq** exclusively, default model **`openai/gpt-oss-120b`**
(GPT-OSS 120B — the 120-billion-parameter open-weight model hosted on Groq).
The Ollama layer from `LLM.md` v0.1 was dropped to keep the build simple.

### 11.2 Connectivity-test endpoints (verified choices)

| Service | Test request | Success means |
|---|---|---|
| Jira | `GET {base}/rest/api/3/myself` | URL + credentials valid; returns `displayName` |
| Groq | `GET https://api.groq.com/openai/v1/models` | key valid **and** configured model is in the returned catalogue |

`/myself` is preferred over `/field` because it proves **auth** (not just
reachability) and returns a human name we can echo back to the user.

### 11.3 Bug found and fixed during verification
- **Symptom:** clicking *Test Groq Connection* with an empty key raised an
  uncaught `GroqError` instead of a friendly message, because
  `GroqClient._headers()` raised **before** the `requests` call that the
  `try/except` guarded.
- **Fix:** resolve the headers inside a guarded block and convert `GroqError`
  to `(False, message)`. The Jira path (`_get` raising `JiraError`) was
  already caught for the same reason.
- **Verified:** empty-credential clicks on both buttons now show
  `st.error(...)` with no exception.

### 11.4 Verification results (all green)
- `python -m compileall tools app.py` → **COMPILE_OK**
- Offline tool smoke test (8 checks) → **ALL_SMOKE_TESTS_PASSED**
  (key parsing, config defaults, prompt build, `validate_plan` on 14 sections,
  generation against a fake LLM client, ADF flattening, bad-key rejection,
  missing-key rejection)
- Headless Streamlit `AppTest` → **UI_SMOKE_TESTS_PASSED**
  (app runs, all 6 settings fields + 4 buttons present, no-ticket and
  not-configured paths degrade gracefully)
- Connection-button test → **CONNECTION_TEST_SMOKE_PASSED**
- Live server → `streamlit run app.py` served **HTTP 200** on
  `http://localhost:8501` (server stopped after verification).

### 11.5 Live connectivity — now CONFIRMED (see §12)
`test_connection()` and the full fetch→generate path were later verified against
live credentials. See §12.6 for results.

---

## 12. Template-driven rework findings (2026-09-13, later)

Triggered by user feedback: *"the test plan created for my Jira is not detailed
enough"*, followed by two reference files dropped into `templates/`.

### 12.1 The two reference files (user-provided)
| File | Role |
|---|---|
| `templates/testplan_template.md` | A formal corporate **Test Plan template** — the required document structure: doc-control table, Copyright, Revision History, Sign Off, ToC, then numbered sections **1. Introduction · 2. Test Level · 3. Test Reporting and Defect Tracking · 4. Change Management · 5. Test Planning · 6. Customer Validation Plan · Appendix**, with 31 numbered headings and 12 defined tables. |
| `templates/VWO_Test_Plan.md` | A **master example** (VWO login) showing the desired depth and, crucially, the **test-case table format**: `| Test case id | Description | Actual Result | Expected result | Requirement ID | Dependencies |` with **Actual Result left blank**, plus an ID scheme `<PROJECT>-<AREA>-<NNN>_<T>` tagged P/N/B/E. |

**Decision:** the template is the **authoritative structure**; the master is the
**authoritative test-case format**. Both are now read at generation time via a
new Layer-3 module `tools/template_loader.py`, so editing either file changes
the output without code changes.

### 12.2 ⚠️ CRITICAL: Groq free-tier token limit (HTTP 413)
The first attempt embedded **both files verbatim** in the prompt. Groq rejected it:

```
HTTP 413: Request too large for model `openai/gpt-oss-120b`
... tokens per minute (TPM): Limit 8000, Requested 12302
```

- **The limit is 8,000 tokens/minute (TPM)** for `openai/gpt-oss-120b` on the
  on-demand/free tier — ~12.3k tokens of template + master + facts exceeded it.
- **Measured finding:** `max_tokens` does **not** count toward TPM. A tiny
  prompt with `max_tokens=16000` returns **HTTP 200**. Only the **input**
  (prompt) is metered.
- **Consequence:** keep the *prompt* small (≤ ~7k tokens for headroom); the
  *output* budget can stay large (16k).

### 12.3 Fix: condense the prompt (derived, not embedded)
Rather than ship the files' prose, `template_loader` now derives two compact
artefacts from them:

| Function | Source | Output | Size |
|---|---|---|---|
| `structure_digest()` | `testplan_template.md` | Each heading + the **exact table it expects** (`table: | … |`) + its `<placeholder>` guidance | ~5.6 KB |
| `master_digest()` | `VWO_Test_Plan.md` | The test-case table header + the ID-scheme line only (deduped) | ~0.5 KB |

Result: the prompt fell from **12,302 → ~3,286 tokens**, comfortably inside the
8,000 TPM limit, while still being driven by the files.

### 12.4 Bug found: tables landing under the wrong headings
First template-driven run gave the model only a *global* list of table formats,
so it reused them everywhere — e.g. a dependency table under **2.1 Test Level –
Entry and Exit**, and a metrics table under **5.2 Test Schedule**.
**Fix:** `structure_digest()` now attaches each table to *its own heading*, and
the instructions say "use that table there and ONLY there". Verified: 2.1 now
gets `| Entry Level | Test Level | Exit Level |`, 5.2 gets
`| Task | Start Date | End Date | Resource | Deliverable |`.

### 12.5 Smaller fixes
- **Heading hierarchy:** first run emitted every section as `#` H1. Added an
  explicit rule (`#` title, `##` sections, `###` x.y, `####` x.y.z). Verified:
  6 `##` + 21–27 `###`.
- **False "Appendix" warning:** `Appendix` is an empty heading in the template,
  so requiring it produced a spurious "omitted sections" warning. Un-numbered
  headings (Copyright, Appendix) are now excluded from validation.
- **Duplicate format lines:** the master repeats its test-case header in all 10
  suites → 10 identical digest lines. Now deduped.
- **Metrics placement:** the template has no metrics section, so the model
  parked metrics under 5.5 Risk. Instructions now direct metrics to the
  reporting section with columns `| Metric | Definition | Target | Report Cadence |`
  (matches the master + the project taste for metrics with definitions + targets).

### 12.6 Live end-to-end verification (real Jira + real Groq)
Credentials were configured by the user via the UI. Confirmed:
- **Jira:** `Connected to Jira as Shreya Sen (accountId 712020:b15aaaa4…)`.
- **Groq:** `Connected to Groq. Model 'openai/gpt-oss-120b' is available.`

Live generation against real ticket **KAN-3** (`[VWO] Add Passkey and SSO Login
Options to VWO Login Page`):

| Run | Output | Words | Test-case rows | Sections missing | Time |
|---|---|---|---|---|---|
| 1st (verbose prompt) | 19,105 chars | 2,831 | 45 | Appendix (false) | 12.8 s |
| 2nd (per-section tables) | 28,380 chars | 4,653 | 64 | none | 18.8 s |
| 3rd (final) | 22,300 chars | 3,482 | 40 | none | 14.4 s |

**Verdict:** the earlier "not detailed enough" problem is resolved — output went
from a thin document to ~2.2–2.8k words with 40–64 tagged test cases across 8
suites, the correct 6-section template structure, and all tables in the right
places.

### 12.7 Constraint to remember
Any future change that puts more text into the prompt risks re-crossing the
8,000 TPM ceiling. The budget guard is asserted in the offline test suite
(`~3.3k tokens incl. user prompt`).
```
