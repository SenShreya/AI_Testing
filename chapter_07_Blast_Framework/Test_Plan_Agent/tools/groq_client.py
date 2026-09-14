"""Groq Cloud client (OpenAI-compatible API).

Used as the Test Plan Creator's LLM. Default model is ``openai/gpt-oss-120b``
(the 120B-parameter open-weight model hosted on Groq).

All failures raise ``GroqError`` with a user-presentable message.
"""

from __future__ import annotations

import requests

_API_BASE = "https://api.groq.com/openai/v1"
_TIMEOUT = (5, 120)


class GroqError(Exception):
    """Raised when a Groq request fails. Message is safe to show the user."""


class GroqClient:
    def __init__(self, api_key: str, model: str = "openai/gpt-oss-120b"):
        self.api_key = (api_key or "").strip()
        self.model = (model or "").strip()

    def _headers(self) -> dict:
        if not self.api_key:
            raise GroqError("Groq API key is not configured. Add it in Settings.")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------ connectivity ----
    def test_connection(self) -> tuple[bool, str]:
        """Verify the API key and that the configured model is available."""
        try:
            headers = self._headers()
        except GroqError as exc:
            return False, str(exc)
        try:
            response = requests.get(
                f"{_API_BASE}/models", headers=headers, timeout=(5, 30)
            )
        except requests.exceptions.Timeout:
            return False, "Timed out connecting to Groq."
        except requests.exceptions.ConnectionError:
            return False, "Could not reach api.groq.com. Check your network."
        except requests.exceptions.RequestException as exc:  # pragma: no cover
            return False, f"Unexpected error while contacting Groq: {exc}"

        if response.status_code == 401:
            return False, "Groq rejected the API key (HTTP 401). Check it in Settings."
        if response.status_code >= 400:
            return False, f"Groq returned HTTP {response.status_code}: {response.text[:200]}"

        try:
            models = [m.get("id", "") for m in response.json().get("data", [])]
        except ValueError:
            return False, "Groq returned an unreadable (non-JSON) response."

        if self.model and models and self.model not in models:
            return False, (
                f"API key is valid, but model '{self.model}' is not available on this "
                "account. Pick another from https://console.groq.com/docs/models"
            )
        return True, f"Connected to Groq. Model '{self.model}' is available."

    # ------------------------------------------------------------ chat ----
    def chat(self, system_prompt: str, user_prompt: str,
             temperature: float = 0.2, max_tokens: int = 16000) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if not self.model:
            raise GroqError("Groq model is not configured.")

        try:
            response = requests.post(
                f"{_API_BASE}/chat/completions",
                json=payload,
                headers=self._headers(),
                timeout=_TIMEOUT,
            )
        except requests.exceptions.Timeout:
            raise GroqError("Groq timed out while generating the test plan.")
        except requests.exceptions.ConnectionError:
            raise GroqError("Could not reach Groq. Check your network.")
        except requests.exceptions.RequestException as exc:  # pragma: no cover
            raise GroqError(f"Unexpected error while contacting Groq: {exc}")

        if response.status_code == 401:
            raise GroqError("Groq rejected the API key (HTTP 401). Check Settings.")
        if response.status_code == 404:
            raise GroqError(
                f"Groq model '{self.model}' was not found. It may have been "
                "deprecated - check https://console.groq.com/docs/models"
            )
        if response.status_code == 429:
            raise GroqError("Groq rate limit reached (HTTP 429). Try again shortly.")
        if response.status_code == 413:
            raise GroqError(
                "The request is too large for this Groq tier (HTTP 413). The free "
                "tier limits openai/gpt-oss-120b to 8,000 tokens per minute; this "
                "ticket's content plus the plan structure exceeded it. Try a "
                "shorter ticket, or upgrade your Groq tier."
            )
        if response.status_code >= 400:
            raise GroqError(
                f"Groq returned HTTP {response.status_code}: {response.text[:300]}"
            )

        try:
            data = response.json()
        except ValueError:
            raise GroqError("Groq returned an unreadable (non-JSON) response.")

        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise GroqError("Groq response was missing content.")
        if not text or not text.strip():
            raise GroqError("Groq returned an empty response.")
        return text.strip()
