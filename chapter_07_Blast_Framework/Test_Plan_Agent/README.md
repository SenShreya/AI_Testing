# Test Plan Creator (from a Jira ID)

A simple Streamlit app: type a request like **"fetch VWO-49 and create a test
plan"**, and it fetches the Jira issue automatically and generates a complete,
enterprise-grade **Test Plan** with Groq (`openai/gpt-oss-120b`).

Built with the **B.L.A.S.T.** protocol (Protocol 0 → Stylize).

## Features

- **Chat-style input** — one text box + **Send**.
- **Automatic Jira fetch** — REST API v3, email + API token, Atlassian
  Document Format (ADF) descriptions flattened to plain text.
- **Template-driven Test Plan** — the document structure comes from
  `templates/testplan_template.md` (Introduction, Test Level, Reporting & Defect
  Tracking, Change Management, Test Planning, Customer Validation) and the
  test-case format from `templates/VWO_Test_Plan.md` (tagged P/N/B/E, "Actual
  Result" left blank).
- **Plan depth** — `standard` or `detailed` (detailed targets 8+ suites and
  25+ test cases, with risks and metrics tables).
- **Anti-hallucination** — facts only; missing data is labelled
  `Not specified`; inferences are labelled `Inference (low confidence)`.
- **Settings panel** — Jira email/token/URL and Groq key/model, with
  **Test Jira Connection** and **Test Groq Connection** buttons, plus Save.
- **Download** the generated plan as a `.md` file.

## Requirements

- Python 3.9+
- A Jira Cloud site + API token
- A Groq API key (https://console.groq.com/keys)

## Setup & run

```bash
cd chapter_07_Blast_Framework/Test_Plan_Agent
pip install -r requirements.txt

# Option A — enter credentials in the UI (saved to config/settings.json)
streamlit run app.py

# Option B — use a .env file (values override the UI-saved settings)
cp .env.example .env   # then fill in real values
streamlit run app.py
```

Then open http://localhost:8501.

## Usage

1. In the right-hand **Settings** panel, fill in Jira Email, Jira API Token,
   Jira Base URL, Groq API Key, and Groq Model.
2. Click **Test Jira Connection** and **Test Groq Connection** — both should
   report success.
3. Click **Save Settings**.
4. In the left panel, type `fetch VWO-49 and create a test plan` and press
   **Send**.
5. The generated Test Plan appears below; use **Download test plan (.md)**.

## Architecture (A.N.T. 3-layer)

```
app.py                      Layer 2 — navigation / UI (Streamlit)
  └── tools/                Layer 3 — deterministic Python
      ├── config_manager.py   defaults <- settings.json <- .env
      ├── jira_client.py      REST v3 fetch + ADF flatten -> JiraIssue
      ├── groq_client.py      Groq /chat/completions + connection test
      ├── template_loader.py  templates/ -> structure + test-case format
      └── plan_generator.py   JiraIssue + template -> prompt -> Test Plan + validation
architecture/               Layer 1 — SOPs (the "how")
  ├── 01_jira_fetch.md
  ├── 02_normalize_issue.md
  └── 03_generate_test_plan.md
templates/                  Reference inputs (edit these to change the output)
  ├── testplan_template.md  Required document structure
  └── VWO_Test_Plan.md      Master example: depth + test-case table format
```

> **Note:** Groq's free tier limits `openai/gpt-oss-120b` to 8,000 tokens/minute
> (prompt only). The template and master are condensed into digests rather than
> embedded verbatim — see `phase0/findings.md` §12.2.

Project memory (BLAST Protocol 0): [`phase0/`](phase0/) — `task_plan.md`,
`findings.md`, `progress.md`, `LLM.md`.

## Troubleshooting

- **Jira 401/403** — use an API token (not your password); the email must
  belong to that token.
- **Ticket not found (404)** — check the project key and that your account can
  see the issue.
- **Groq model not found** — model names change; check
  https://console.groq.com/docs/models and update the model in Settings.
- **Secrets** — `.env` and `config/settings.json` are gitignored.
