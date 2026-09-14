"""Test Plan Creator — Streamlit UI.

Single screen, two panels:
  * Left  : chat-style request + generated test plan output (+ download).
  * Right : Settings — Jira credentials, Groq key, and connection tests.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from tools import (config_manager, groq_client, jira_client, plan_generator,
                   template_loader)

config_manager.load_env()
SETTINGS = config_manager.load_settings()


# --------------------------------------------------------------- settings --
def render_settings_panel() -> None:
    st.markdown("## Settings")
    st.caption("Saved locally to `config/settings.json`. Values in a `.env` file "
               "take precedence.")

    st.markdown("#### Jira")
    jira_email = st.text_input("Jira Email", value=SETTINGS["jira_email"],
                               placeholder="you@company.com")
    jira_token = st.text_input("Jira API Token", value=SETTINGS["jira_api_token"],
                               type="password",
                               help="Atlassian API token (not your password).")
    jira_url = st.text_input("Jira Base URL", value=SETTINGS["jira_base_url"],
                             placeholder="https://your-domain.atlassian.net")

    if st.button("Test Jira Connection", use_container_width=True):
        ok, message = jira_client.JiraClient(
            jira_email, jira_token, jira_url).test_connection()
        (st.success if ok else st.error)(message)

    st.markdown("---")
    st.markdown("#### Groq (LLM)")
    groq_key = st.text_input("Groq API Key", value=SETTINGS["groq_api_key"],
                             type="password",
                             help="Get one at https://console.groq.com/keys")
    groq_model = st.text_input("Groq Model", value=SETTINGS["groq_model"],
                               help="Default: openai/gpt-oss-120b")

    if st.button("Test Groq Connection", use_container_width=True):
        ok, message = groq_client.GroqClient(
            groq_key, groq_model).test_connection()
        (st.success if ok else st.error)(message)

    st.markdown("---")
    st.markdown("#### Test plan")
    depth_options = ["standard", "detailed"]
    current_depth = (SETTINGS["plan_depth"]
                     if SETTINGS["plan_depth"] in depth_options else "standard")
    plan_depth = st.selectbox(
        "Plan depth", depth_options, index=depth_options.index(current_depth),
        help="Detailed produces many more test cases and far greater depth.")
    if template_loader.template_available():
        master_note = (" + master example"
                       if template_loader.master_available() else "")
        st.caption(f"Template in use: `{template_loader.TEMPLATE_FILENAME}`{master_note}")
    else:
        st.caption("No template found in `templates/` — using the built-in outline.")

    st.markdown("---")
    if st.button("Save Settings", type="primary", use_container_width=True):
        config_manager.save_settings({
            "jira_email": jira_email,
            "jira_api_token": jira_token,
            "jira_base_url": jira_url,
            "jira_api_version": SETTINGS["jira_api_version"],
            "groq_api_key": groq_key,
            "groq_model": groq_model,
            "plan_depth": plan_depth,
        })
        st.success("Settings saved to config/settings.json")


# ------------------------------------------------------------ generation --
def _run_generation(raw_request: str) -> None:
    settings = config_manager.load_settings()
    key = jira_client.parse_issue_key(raw_request)
    if not key:
        st.error("No Jira ticket ID found in your message. "
                 "Try: fetch VWO-49 and create a test plan")
        return
    if not config_manager.is_jira_configured(settings):
        st.error("Jira is not configured. Add your email, API token, and base URL "
                 "in Settings, then click Save Settings.")
        return
    if not config_manager.is_groq_configured(settings):
        st.error("Groq is not configured. Add your API key in Settings and save.")
        return

    with st.spinner(f"Fetching {key} from Jira ..."):
        try:
            issue = jira_client.JiraClient(
                settings["jira_email"], settings["jira_api_token"],
                settings["jira_base_url"]).get_issue(key)
        except jira_client.JiraError as exc:
            st.error(str(exc))
            return

    with st.spinner(f"Generating test plan for {key} with Groq ..."):
        try:
            model, document = plan_generator.generate_test_plan(settings, issue)
        except groq_client.GroqError as exc:
            st.error(str(exc))
            return

    st.session_state.results.append({
        "request": raw_request,
        "issue": issue,
        "model": model,
        "document": document,
        "missing": plan_generator.validate_plan(document),
    })


# ------------------------------------------------------------- main panel --
def render_chat_panel() -> None:
    st.title("Test Plan Creator")
    st.caption("Describe what you want, e.g. "
               "`fetch VWO-49 and create a test plan`.")

    with st.form("request_form", clear_on_submit=False):
        cols = st.columns([5, 1])
        request = cols[0].text_input(
            "Your request", label_visibility="collapsed",
            placeholder="fetch VWO-49 and create a test plan")
        submitted = cols[1].form_submit_button(
            "Send", type="primary", use_container_width=True)

    if submitted and request.strip():
        _run_generation(request.strip())

    for entry in reversed(st.session_state.results):
        issue = entry["issue"]
        with st.expander(f"{issue['key']} — {issue['summary']}",
                         expanded=True):
            st.caption(f"Generated by Groq · {entry['model']}  |  "
                       f"Request: {entry['request']}")
            if entry["missing"]:
                st.warning("The model omitted these sections: "
                           + ", ".join(entry["missing"]))
            st.download_button(
                "Download test plan (.md)",
                data=entry["document"],
                file_name=plan_generator.suggested_filename(issue),
                mime="text/markdown",
                key=f"dl_{issue['key']}_{len(entry['document'])}",
            )
            st.markdown(entry["document"])


# ------------------------------------------------------------------- main --
def main() -> None:
    st.set_page_config(page_title="Test Plan Creator",
                       page_icon=":material/assignment:", layout="wide")

    if "results" not in st.session_state:
        st.session_state.results = []

    left, right = st.columns([2, 1], gap="large")
    with left:
        render_chat_panel()
    with right:
        with st.container(border=True):
            render_settings_panel()


if __name__ == "__main__":
    main()
