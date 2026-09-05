# Jira-to-Test-Case Generator — Implementation Plan

## Objective
Build a Streamlit web app in `chapter_03_Jira_TestCase` that:
- Lets a user type a natural-language request (e.g., "create tc for VWO-49") in a chat-style single input on Screen 1 and click **send**.
- Fetches the Jira ticket via Jira REST API.
- Generates test cases/test plan via **Ollama (local Gemma model) first**, falling back automatically to **Groq** if Ollama is unreachable.
- Screen 2 (Settings) lets the user enter/persist Jira email, Jira API token, Jira base URL, Ollama URL, and Groq API token — nothing hardcoded.
- Supports full `.env` read/load (via python-dotenv) and JSON persistence to `config/settings.json`.

## Key User Answers / Constraints
- **Do NOT use `template/Template.md`** — ignore it and the `templates/` fallback template folder logic entirely.
- **Consider only `src/Prompt.md` + `src/ApplicationScreenShot.png`** as the source of truth.
- The screenshot shows a **single-screen, two-panel layout** (NOT a multi-page Streamlit app):
  - Left panel: large output/chat text area (bottom), a text input with the current ticket prompt, and a **send** button.
  - Right panel: settings fields (Jira Email, Jira Token, Jira URL, Ollama URL, Groq Token) and a **Save Settings** button.
  - Footer credit: `TheTestingAcademy`.
- Full `.env` read + load support is required (not just JSON).
- Scope: everything — all modules, requirements.txt, README, `.env.example`, verification.

## Decisions / Deviations from the Prompt
| Prompt says | We build | Why |
|---|---|---|
| Multi-page (`app.py` + `pages/1_Settings.py`) | **Single Streamlit app file** (`app.py`) with two-column layout | The screenshot — explicitly declared the source of truth — shows panels side-by-side on one screen |
| `jira_client.py`, `llm_handler.py`, `settings/config persistence`, `test case generation logic` | Same logical modules as separate files, imported by `app.py` | Preserves separation of concerns |
| Template folder `template/` | **Ignored**. Templates handled by prompt engineering inside the app | User said: do not use `Template.md` |
| Hardcoded `gemma:31b`, Groq default | Configurable model names via settings + `.env`, with documented defaults | Production-usable, no secrets/model assumptions hardcoded |

## Deliverable File Layout (inside `chapter_03_Jira_TestCase/`)
```
chapter_03_Jira_TestCase/
├── app.py                      # Single Streamlit screen: chat input + output | settings panel
├── jira_client.py              # Jira REST API v3: auth, fetch issue, parse description/ADF
├── llm_handler.py              # Ollama-first, Groq-fallback generation + ticket→prompt builder
├── config_manager.py           # Load/save config: .env read + config/settings.json
├── requirements.txt
├── .env.example                # Documented env var names (no real values)
├── README.md                   # Setup, run, usage, architecture, troubleshooting
└── config/
    └── settings.json           # Runtime-persisted settings (gitignored? see below)
```

### Module-by-module design

**1. `config_manager.py`**
- Paths:
  - Root of project = directory containing `app.py` (resolved robustly).
  - `.env` path = `<project_root>/.env`.
  - `config/settings.json` path = `<project_root>/config/settings.json` (created if missing).
- `load_env()`: loads `.env` into `os.environ` using `python-dotenv` (`load_dotenv`).
- Settings keys (normalized): `jira_email`, `jira_token`, `jira_url`, `ollama_url` (default `http://localhost:11434`), `ollama_model` (default e.g. `gemma3` family), `groq_api_key`, `groq_model` (default a current Groq model; documented to check), plus `num_test_cases` (optional default 5).
- `load_settings()`: precedence — `.env` environment values **override** `config/settings.json` values (or merge: start from JSON, overlay non-empty env). Returns a dict.
- `save_settings(dict)`: persists to `config/settings.json` (JSON, `indent=2`). Never writes secrets to `.env` in this scope (env is treated as user-provided external input).
- Helper `get_setting(key)` for app code.

**2. `jira_client.py`**
- Class `JiraClient(email, token, base_url)`.
- Uses `requests`.
- `fetch_issue(issue_key)`:
  - GET `{base_url}/rest/api/3/issue/{issue_key}` with Basic Auth (`email:token`), `Accept: application/json`.
  - Robust error handling: HTTP 401/403 → clear credential error; 404 → "ticket not found"; network errors → friendly message; Jira `base_url` normalization (strip trailing `/`, support both server/cloud).
- `extract_description(issue_json)`:
  - Handle Jira **Atlassian Document Format** (`fields.description.type == "doc"`), flatten `content` recursively to plain text (headings, paragraphs, lists, code blocks, table cells → readable lines).
  - Fallback: if description is plain text already, return as-is.
  - Returns dict `{summary, description, issue_type, status, priority, acceptance_criteria_guess, url}` plus raw fields needed for prompt context.

**3. `llm_handler.py`**
- `build_test_case_prompt(ticket_info, template_rules, num_cases)`:
  - System prompt: senior QA engineer persona.
  - Injects ticket summary/description/type/status/priority/AC.
  - Embeds strict output rules (markdown table with headers `| Test ID | Description | Pre-conditions | Steps | Expected Result | Priority |`, priority High/Medium/Low, `TC-001…` IDs, numbered steps, "Not specified" for missing, no fabricated features, distinct scenarios).
  - NO reference to any template file — rules are in code strings only.
- `generate_test_cases(settings, ticket_info, num_cases)`:
  - **Ollama first**: POST `{ollama_url}/api/generate` or `/api/chat` via `requests`, payload with `model`, `prompt`, `stream=False`, `format="json"` optional. Short timeout (e.g., `connect=3s`, `read=90s`) so fallback is snappy.
  - Detect failure: connection refused/timeout, non-200, empty `response`, model-not-found error text → raise typed exception.
  - **Groq fallback**: `POST https://api.groq.com/openai/v1/chat/completions` with `Authorization: Bearer {groq_api_key}`, model from settings, `temperature` ~0.2, `max_tokens` generous. Requires groq key; if absent, surface friendly error.
  - Returns `(provider_used, raw_text)` so UI can display which engine ran.
- Keep API calls synchronous (Streamlit-friendly), no async complexity.

**4. `app.py`** (Streamlit, single file)
- `st.set_page_config(page_title=..., layout="wide")`.
- Layout via `st.columns([2, 1])`:
  - **Left column (chat/output)**:
    - `st.title`/`st.header`, small helper text.
    - `st.text_area` or `st.text_input` for the user request, prefilled example `create tc for VWO-49`.
    - Optional `st.number_input` for number of test cases (default 5).
    - **send** button.
    - On click: parse Jira ID from the typed text with a regex (e.g., `\b[A-Z][A-Z0-9]+-\d+\b`); call `jira_client.fetch_issue`; then `llm_handler.generate_test_cases`; render result in a large output area (`st.markdown` for the table).
    - Chat history kept in `st.session_state` so prior results remain visible; show which provider answered.
    - If ticket isn't found / Ollama + Groq both fail, show a clean `st.error` and keep the app usable.
  - **Right column (settings panel)**:
    - Header, e.g., `Configuration`.
    - Inputs: Jira Email, Jira Token (password), Jira URL, Ollama URL, Ollama Model, Groq API Key (password), Groq Model.
    - **Save Settings** button → `config_manager.save_settings(...)` + `st.success`.
    - Pre-fill widget values from current `config_manager.load_settings()` (so saved/env values show).
    - Footer credit in bottom right: `TheTestingAcademy`.
- On startup (top of file): call `config_manager.load_env()` then `load_settings()` so env + saved values are available.

**5. `requirements.txt`**
- `streamlit`
- `requests`
- `python-dotenv`
- (pin minimum versions sensible for current Python; no hard pins unless needed)

**6. `.env.example`**
```
JIRA_EMAIL=
JIRA_API_TOKEN=
JIRA_BASE_URL=https://your-domain.atlassian.net
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:12b        # adjust to your pulled Gemma model
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
```
- Never commit real `.env`.

**7. `README.md`**
- What it does, screenshot reference.
- Setup: `pip install -r requirements.txt`, `streamlit run app.py`.
- Config: Settings screen or `.env`.
- Usage: "create tc for VWO-49".
- Architecture diagram (UI / config / Jira / LLM fallback).
- Troubleshooting: Ollama not running, wrong model name (`ollama list`), Groq model deprecated.

## Security / Credential Handling
- No secrets hardcoded.
- `.env` and `config/settings.json` should NOT be committed.
- Recommend adding to repo root `.gitignore` (repo has a `.gitignore` at root already):
  - `.env`
  - `chapter_03_Jira_TestCase/config/settings.json`
- Password inputs in Streamlit (`type="password"`).
- Jira token used only for the API call in-memory.

## Edge Cases / Error Handling
- Ollama down/timeout → automatic Groq fallback with visible notice.
- Both engines fail → clear error (config problem) not a traceback.
- Invalid/missing Jira ID → prompt user.
- Jira ticket without description or ADF content → handle empty content gracefully ("No description available").
- Secrets with whitespace → strip when loading.
- `base_url` trailing slashes → normalize.
- Groq model listed as deprecated → README troubleshooting note; model configurable.

## Verification
1. `pip install -r requirements.txt` inside `chapter_03_Jira_TestCase`.
2. `python -c "import app, jira_client, llm_handler, config_manager"` (no syntax errors).
3. Optional unit sanity: `python -m compileall .` on the new `.py` files.
4. Create a `.env` from `.env.example` with a valid test Jira ID/token (user provides).
5. `streamlit run app.py` → both panels render; Settings pre-fills from env.
6. Click **send** with e.g. `create tc for VWO-49`:
   - Confirm Ollama attempt first (visible provider label), fallback works if Ollama is stopped (kill Ollama, retry → Groq path).
7. Confirm the generated output renders as a markdown table in the left panel with the exact required headers.
8. Confirm credentials persist after **Save Settings** (restart app → values still there).
9. Confirm `.env` values override JSON settings.
10. Confirm no secrets appear in `git status`/committed files (`.env`, `settings.json` gitignored).

## Open Assumption (flag to user before coding)
- `template/Template.md` is **explicitly ignored** per your answer. The generation rules/prompt live in `llm_handler.py` instead. If you later want template-file-driven generation, that's an easy add (read any `.md` in a `templates/` folder into the system prompt).
