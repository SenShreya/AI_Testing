"""Jira-to-Test-Case Generator - Streamlit front end.

Single screen with two panels (mirrors the approved wireframe):
  * Left:  chat-style input ("create tc for VWO-49") + generated table output.
  * Right: settings panel - Jira / Ollama / Groq configuration + Save.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import re

import streamlit as st

import config_manager
import jira_client
import llm_handler

# ---------------------------------------------------------------- helpers --
def _parse_jira_key(text: str) -> str | None:
    """Pull the first Jira-style key (PROJ-123) out of free text."""
    match = re.search(r"\b[A-Z][A-Z0-9]+-\d{1,6}\b", text or "", re.IGNORECASE)
    return match.group(0).upper() if match else None


def _run_generation(settings: dict, raw_request: str, num_cases: int) -> None:
    key = _parse_jira_key(raw_request)
    if not key:
        st.error("No Jira ticket ID found in your message. "
                 "Try something like: create test cases for VWO-49")
        return

    with st.spinner(f"Fetching {key} from Jira ..."):
        try:
            client = jira_client.JiraClient(
                settings["jira_email"],
                settings["jira_api_token"],
                settings["jira_base_url"],
            )
            ticket = client.get_ticket(key)
        except jira_client.JiraError as exc:
            st.error(str(exc))
            return

    with st.spinner("Generating test cases (Ollama first, Groq fallback) ..."):
        try:
            provider, table_md = llm_handler.generate_test_cases(
                settings, ticket, num_cases=num_cases)
        except llm_handler.LLMError as exc:
            st.error(str(exc))
            return

    st.session_state.results.append(
        {"request": raw_request, "ticket": ticket, "provider": provider,
         "table": table_md}
    )


# ------------------------------------------------------------------- state
config_manager.load_env()  # read .env into os.environ (overrides nothing)
SETTINGS = config_manager.load_settings()

if "results" not in st.session_state:
    st.session_state.results = []


# --------------------------------------------------------------- settings --
def render_settings_panel() -> None:
    st.markdown("## Configuration")
    st.caption("Credentials are saved locally to config/settings.json. "
               "Values already present in a .env file override them.")

    jira_email = st.text_input("Jira Email", value=SETTINGS["jira_email"],
                               placeholder="you@company.com")
    jira_token = st.text_input("Jira API Token", value=SETTINGS["jira_api_token"],
                               type="password",
                               help="Atlassian API token (not your password).")
    jira_url = st.text_input("Jira Base URL", value=SETTINGS["jira_base_url"],
                             placeholder="https://your-domain.atlassian.net")

    st.markdown("---")
    st.markdown("**LLM configuration**")
    ollama_url = st.text_input("Ollama URL", value=SETTINGS["ollama_url"])
    ollama_model = st.text_input("Ollama Model", value=SETTINGS["ollama_model"],
                                 help="Run `ollama list` to see available models.")
    groq_key = st.text_input("Groq API Key", value=SETTINGS["groq_api_key"],
                             type="password")
    groq_model = st.text_input("Groq Model", value=SETTINGS["groq_model"])

    if st.button("Save Settings", type="primary"):
        config_manager.save_settings({
            "jira_email": jira_email,
            "jira_api_token": jira_token,
            "jira_base_url": jira_url,
            "ollama_url": ollama_url,
            "ollama_model": ollama_model,
            "groq_api_key": groq_key,
            "groq_model": groq_model,
        })
        st.success("Settings saved to config/settings.json")


# ------------------------------------------------------------- main panel --
def render_chat_panel() -> None:
    st.title(":material/smart_toy: QA Test Case Generator")
    st.caption("Type a Jira ticket request, e.g. "
               "`create tc for VWO-49`, and press **Send**.")

    with st.form("request_form", clear_on_submit=False):
        cols = st.columns([5, 1, 2])
        request = cols[0].text_input(
            "Your request", label_visibility="collapsed",
            placeholder="create tc for VWO-49")
        num_cases = cols[1].number_input("Count", min_value=1, max_value=50,
                                         value=5, label_visibility="collapsed")
        submitted = cols[2].form_submit_button("Send", type="primary",
                                               use_container_width=True)

    if submitted and request.strip():
        _run_generation(SETTINGS, request.strip(), int(num_cases))

    # Chat history (newest at top).
    for entry in reversed(st.session_state.results):
        provider = entry["provider"]
        provider_label = ("Ollama (local)" if provider == "ollama"
                          else "Groq (cloud fallback)")
        with st.expander(f"{entry['ticket']['key']} - "
                         f"{entry['ticket']['summary']}",
                         expanded=True):
            st.markdown(f"*Generated by*: **{provider_label}**  \n"
                        f"*Request*: {entry['request']}")
            st.markdown(entry["table"])


# ------------------------------------------------------------------- main --
def main() -> None:
    st.set_page_config(page_title="QA Test Case Generator",
                       page_icon=":material/smart_toy:", layout="wide")

    if not config_manager.is_configured(SETTINGS):
        st.warning("Jira credentials are not configured yet. "
                   "Fill in the panel on the right and click Save Settings, "
                   "or provide them via a .env file.")

    left, right = st.columns([2, 1], gap="large")
    with left:
        render_chat_panel()
    with right:
        with st.container(border=True):
            render_settings_panel()
        st.caption("")
        st.markdown(
            "<div style='text-align:right; color:gray;'>TheTestingAcademy</div>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
