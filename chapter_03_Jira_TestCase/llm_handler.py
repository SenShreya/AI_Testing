"""LLM handler: turn a fetched Jira ticket into test cases.

Strategy (per the product spec):
    1. Try the local Ollama server first.
    2. If that fails for *any* reason, fall back to the Groq cloud API.
    3. If both fail, raise a user-presentable LLMError.

The generation rules (table format, priorities, numbering, etc.) live in
this file as prompt text; no template file is consulted.
"""

from __future__ import annotations

import re
from typing import Tuple

import requests

# Generation rules embedded in the prompt (the user's app does not read any
# template file - rules are code constants so behaviour is predictable).
_GENERATION_RULES = """
You are a Senior QA Engineer.  Generate test cases ONLY from the ticket
information provided below.

Strict rules (follow exactly):
- Output ONLY a Markdown table.  No preamble, no closing notes, no extra text.
- Column headers must be exactly:
  | Test ID | Description | Pre-conditions | Steps | Expected Result | Priority |
- Test ID format: TC-001, TC-002, ... (sequential).
- Priority must be one of: High, Medium, Low.
- Steps must be a numbered list: 1. ... 2. ... 3. ...
- Pre-conditions and Steps must be concise - one sentence per point.
- Description must be one short phrase summarising the scenario.
- Use ONLY the requirements given.  If information is missing, write
  "Not specified" in that cell - never invent features or behaviours.
- Every test case must cover a distinct scenario.  No duplicates.
"""


class LLMError(Exception):
    """Raised when neither Ollama nor Groq could generate a response."""


class OllamaError(Exception):
    """Internal: Ollama failed; triggers the Groq fallback."""


def _build_user_prompt(ticket: dict, num_cases: int) -> str:
    parts = [
        f"Ticket key: {ticket['key']}",
        f"Summary: {ticket['summary']}",
        f"Type: {ticket['issue_type'] or 'Not specified'}",
        f"Status: {ticket['status'] or 'Not specified'}",
        f"Priority: {ticket['priority'] or 'Not specified'}",
        "",
        "Description:",
        ticket.get("description") or "Not specified",
    ]
    if ticket.get("acceptance_criteria"):
        parts += ["", "Acceptance criteria:", ticket["acceptance_criteria"]]
    parts += [
        "",
        f"Generate exactly {num_cases} test cases as a Markdown table.",
    ]
    return "\n".join(parts)


def build_messages(ticket: dict, num_cases: int) -> Tuple[str, str]:
    """Return (system_prompt, user_prompt)."""
    return _GENERATION_RULES.strip(), _build_user_prompt(ticket, num_cases)


def _strip_code_fences(text: str) -> str:
    """Remove ``` wrappers some models add around the table."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
    if text.endswith("```"):
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _looks_like_error(payload: dict) -> bool:
    """Heuristic: Ollama sometimes returns 200 with an error message body."""
    error = payload.get("error")
    if isinstance(error, dict):
        return bool(error.get("message"))
    if isinstance(error, str):
        return bool(error.strip())
    response = payload.get("response")
    if isinstance(response, str) and response.strip().lower().startswith("error"):
        return True
    return False


# ------------------------------------------------------------------ Ollama
def _call_ollama(settings: dict, system_prompt: str, user_prompt: str) -> str:
    url = (settings.get("ollama_url") or "http://localhost:11434").strip().rstrip("/")
    model = (settings.get("ollama_model") or "").strip()
    if not model:
        raise OllamaError("Ollama model name is not configured.")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.2},
    }
    try:
        response = requests.post(f"{url}/api/chat", json=payload, timeout=(3, 120))
    except requests.exceptions.RequestException as exc:
        raise OllamaError(f"Ollama unreachable at {url}: {exc}")

    if response.status_code != 200:
        raise OllamaError(f"Ollama returned HTTP {response.status_code}: "
                          f"{response.text[:300]}")
    try:
        data = response.json()
    except ValueError as exc:
        raise OllamaError(f"Ollama returned invalid JSON: {exc}")

    if _looks_like_error(data):
        message = data.get("error")
        if isinstance(message, dict):
            message = message.get("message", str(message))
        raise OllamaError(f"Ollama error: {message}")
    text = (data.get("message") or {}).get("content") or data.get("response") or ""
    if not text.strip():
        raise OllamaError("Ollama returned an empty response.")
    return _strip_code_fences(text)


# ------------------------------------------------------------------- Groq
def _call_groq(settings: dict, system_prompt: str, user_prompt: str) -> str:
    api_key = (settings.get("groq_api_key") or "").strip()
    model = (settings.get("groq_model") or "").strip()
    if not api_key:
        raise LLMError("Groq API key is not configured. Add it on the Settings "
                       "panel (or .env) to use the cloud fallback.")
    if not model:
        raise LLMError("Groq model name is not configured.")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions",
                                 json=payload, headers=headers, timeout=(5, 120))
    except requests.exceptions.RequestException as exc:
        raise LLMError(f"Groq unreachable: {exc}")

    if response.status_code == 401:
        raise LLMError("Groq rejected the API key (HTTP 401). Check it on the "
                       "Settings panel.")
    if response.status_code == 404:
        raise LLMError(f"Groq model '{model}' was not found. It may have been "
                       "deprecated - check https://console.groq.com/docs/models")
    if response.status_code >= 400:
        raise LLMError(f"Groq returned HTTP {response.status_code}: "
                       f"{response.text[:300]}")
    try:
        data = response.json()
    except ValueError as exc:
        raise LLMError(f"Groq returned invalid JSON: {exc}")

    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise LLMError("Groq response was missing content.")
    if not text.strip():
        raise LLMError("Groq returned an empty response.")
    return _strip_code_fences(text)


# ------------------------------------------------------------ public API ---
def generate_test_cases(settings: dict, ticket: dict,
                        num_cases: int = 5) -> Tuple[str, str]:
    """Generate test cases. Returns (provider_used, markdown_table).

    provider_used is 'ollama' or 'groq'.
    Raises LLMError when both backends fail.
    """
    system_prompt, user_prompt = build_messages(ticket, num_cases)

    try:
        text = _call_ollama(settings, system_prompt, user_prompt)
        return "ollama", text
    except OllamaError as ollama_exc:
        # Local LLM unavailable -> try the cloud fallback.
        try:
            text = _call_groq(settings, system_prompt, user_prompt)
            return "groq", text
        except LLMError as groq_exc:
            raise LLMError(f"Ollama failed ({ollama_exc}) and the Groq fallback "
                           f"also failed ({groq_exc}).") from groq_exc
