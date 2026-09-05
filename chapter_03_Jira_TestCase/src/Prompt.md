RICEPOT Prompt: Jira-to-Test-Case Generator Application
Layer	What it Demands
Role	Senior Python full-stack developer with expertise in QA tooling, LLM integration (local + API-based), and Jira REST API automation
Instructions	Build a simple Python web application with a front-end (Streamlit or equivalent) that connects to Jira, fetches ticket details via a provided Jira ID, and auto-generates test cases/test plans based on a template. Must support a local LLM (Ollama) as primary engine with a cloud fallback (Groq)
Context	User will separately provide: Jira API token, Jira email ID, Jira base URL, Groq API token. Ollama is already installed and running locally with a Gemma model already pulled. A template folder already exists containing the test case/test plan template format to follow
Example	ChatGPT-style single input interface: a text box where the user enters a Jira Ticket ID and clicks "Send" → app fetches ticket details from Jira → app generates a test plan/test cases based on the fetched ticket content, using the template in the template folder
Parameters	Two-screen flow: Screen 1 — chat-like interface for entering Jira ID and generating test cases; Screen 2 — Settings/Configuration screen for entering & saving Jira email ID, Jira API token, Jira base URL, and Groq API token. LLM logic: attempt Ollama (local, model: Gemma, already running) first; if Ollama is unavailable/unreachable, fall back to Groq API using the stored token. All credentials must be configurable and persisted from the settings screen — not hardcoded
Output	A working Python application with: (1) a Streamlit front-end file, (2) a Jira integration module (fetch ticket by ID using email + token + URL), (3) an LLM handler module implementing Ollama-first/Groq-fallback logic, (4) a settings/config persistence module (e.g., JSON or .env-based), (5) test case generation logic that reads from the existing template folder
Tone	Clean, production-usable code; clear separation of concerns (UI / Jira client / LLM client / config); no hardcoded secrets; robust error handling for failed Jira fetches and failed Ollama connections


Build the multi-page Streamlit app per the spec:

Structure

app.py — Home page, chat-style input for a Jira ID → fetches ticket → generates test cases
pages/1_Settings.py — second screen for Jira email/token/URL + Ollama + Groq config, persisted to config/settings.json
jira_client.py — fetches ticket via Jira REST API v3 (handles Atlassian Document Format parsing for descriptions)
llm_handler.py — tries Ollama (gemma:31b, already running locally) first, falls back to Groq automatically on any failure
templates/default_template.md — fallback template if your template folder is empty; your own templates in that folder get picked up automatically

To run: pip install -r requirements.txt then streamlit run app.py. Fill in credentials once on the Settings page — nothing is hardcoded.

One thing worth flagging: the Groq default model I used (llama-3.3-70b-versatile) may have changed by the time you run this — worth a quick check against Groq's current model list before your first real run.