"""Jira REST API v3 integration.

Fetches a ticket (issue) by its key using email + API token + base URL and
normalises the payload into a small plain-text dict that is easy to hand to
an LLM.  Handles the Atlassian Document Format used for rich-text fields.

Example
-------
    client = JiraClient(email, token, "https://my.atlassian.net")
    info = client.get_ticket("VWO-49")
"""

from __future__ import annotations

import re
from typing import Any, Optional

import requests

# The jira base url + these paths.
_API_PATH = "/rest/api/3/issue"

_TIMEOUT = (5, 30)  # (connect, read) seconds


class JiraError(Exception):
    """Raised when a ticket cannot be fetched.  message is user-presentable."""


def _clean_base_url(url: str) -> str:
    url = (url or "").strip().rstrip("/")
    if url and not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


class JiraClient:
    def __init__(self, email: str, api_token: str, base_url: str):
        self.email = (email or "").strip()
        self.api_token = (api_token or "").strip()
        self.base_url = _clean_base_url(base_url)

    # ------------------------------------------------------------ fetch ----
    def get_ticket(self, issue_key: str) -> dict:
        """Fetch one issue and return a flattened, LLM-friendly dict.

        Raises JiraError with a human-readable message on any failure.
        """
        issue_key = (issue_key or "").strip().upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9]+-\d+", issue_key or ""):
            raise JiraError(f"'{issue_key}' does not look like a Jira ticket ID "
                            "(expected something like VWO-49).")
        if not self.base_url:
            raise JiraError("Jira base URL is not configured.")
        if not self.email or not self.api_token:
            raise JiraError("Jira email and API token are required. Save them on "
                            "the Settings panel or set them in the .env file.")

        url = f"{self.base_url}{_API_PATH}/{issue_key}"
        try:
            response = requests.get(
                url,
                auth=(self.email, self.api_token),
                headers={"Accept": "application/json"},
                timeout=_TIMEOUT,
            )
        except requests.exceptions.Timeout:
            raise JiraError(f"Timed out connecting to Jira at {self.base_url}. "
                            "Check the URL and your network.")
        except requests.exceptions.ConnectionError:
            raise JiraError(f"Could not reach Jira at {self.base_url}. Check the "
                            "URL, your network, or VPN.")
        except requests.exceptions.RequestException as exc:  # pragma: no cover
            raise JiraError(f"Unexpected error while contacting Jira: {exc}")

        if response.status_code == 404:
            raise JiraError(f"Ticket '{issue_key}' was not found on this Jira site.")
        if response.status_code in (401, 403):
            raise JiraError("Jira rejected the credentials (HTTP "
                            f"{response.status_code}). Check the email / API token "
                            "on the Settings panel.")
        if response.status_code >= 400:
            raise JiraError(f"Jira returned HTTP {response.status_code}: "
                            f"{response.text[:300]}")

        try:
            payload = response.json()
        except ValueError:
            raise JiraError("Jira returned an unreadable (non-JSON) response.")

        return self._flatten(issue_key, payload)

    # ------------------------------------------------------- flattening ----
    def _flatten(self, issue_key: str, payload: dict) -> dict:
        fields = payload.get("fields") or {}
        summary = (fields.get("summary") or "").strip()
        description = self._description_to_text(fields.get("description"))
        status = self._field_name(fields, "status")
        issue_type = self._field_name(fields, "issuetype")
        priority = self._field_name(fields, "priority")
        # Acceptance criteria often live in a custom field whose name contains
        # "acceptance"; pick the first non-empty one found.
        acceptance = self._find_acceptance_criteria(fields)

        if not description and not acceptance:
            description = "No description available for this ticket."

        return {
            "key": issue_key,
            "summary": summary or "Untitled ticket",
            "description": description,
            "acceptance_criteria": acceptance,
            "issue_type": issue_type,
            "status": status,
            "priority": priority,
            "url": f"{self.base_url}/browse/{issue_key}",
        }

    # ---------------------------------------------------------- helpers ----
    @staticmethod
    def _field_name(fields: dict, key: str) -> str:
        value = (fields.get(key) or {}).get("name") if isinstance(fields.get(key), dict) else fields.get(key)
        return str(value).strip() if value else ""

    def _find_acceptance_criteria(self, fields: dict) -> str:
        for field_key, value in fields.items():
            if "acceptance" not in field_key.lower():
                continue
            text = self._description_to_text(value)
            if text and text.lower() not in ("no description available",):
                return text
        return ""

    def _description_to_text(self, value: Any) -> str:
        """Convert ADF JSON (or a plain string) into readable plain text."""
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if not isinstance(value, dict):
            return ""
        if value.get("type") == "doc" and isinstance(value.get("content"), list):
            lines = self._adf_to_lines(value["content"])
            return "\n".join(lines).strip()
        return ""

    def _adf_to_lines(self, content: list, indent: int = 0) -> list:
        """Walk an ADF content tree and produce a list of text lines."""
        lines: list = []
        prefix = "  " * indent
        for node in content:
            node_type = node.get("type")
            node_text = self._node_text(node)
            if node_type == "paragraph":
                lines.append(f"{prefix}{node_text}")
            elif node_type == "heading":
                lines.append(f"{prefix}{node_text}")
            elif node_type in ("bulletList", "orderedList"):
                lines.extend(self._adf_to_lines(node.get("content") or [], indent))
            elif node_type == "listItem":
                lines.append(f"{prefix}- {node_text}")
                lines.extend(self._adf_to_lines(node.get("content") or [], indent + 1))
            elif node_type in ("codeBlock", "blockquote"):
                lines.append(f"{prefix}```")
                lines.extend(self._adf_to_lines(node.get("content") or [], indent))
                lines.append(f"{prefix}```")
            elif node_type == "table":
                for row in node.get("content") or []:
                    cells = [self._node_text(cell).replace("\n", " ")
                             for cell in (row.get("content") or [])
                             if cell.get("type") == "tableCell"
                             or cell.get("type") == "tableHeader"]
                    lines.append(" | ".join(cells))
            elif node_type == "mediaSingle":
                lines.append(f"{prefix}[image]")
            elif node_type in ("rule", "hardBreak"):
                lines.append("")
            elif node_text:
                lines.append(f"{prefix}{node_text}")
            # else: unknown node type -> ignore silently
        return lines

    def _node_text(self, node: dict) -> str:
        """Concatenate the text inside an ADF node (recurses into marks/inline)."""
        if node.get("type") == "text":
            text = node.get("text") or ""
            marks = node.get("marks") or []
            if any(m.get("type") == "code" for m in marks):
                text = f"`{text}`"
            elif any(m.get("type") == "strong" for m in marks):
                text = f"**{text}**"
            return text
        parts = []
        for child in node.get("content") or []:
            parts.append(self._node_text(child))
        if node.get("type") == "inlineCard":
            return node.get("attrs", {}).get("url", "") or "".join(parts)
        if node.get("type") == "mention":
            return f"@{node.get('attrs', {}).get('text', '')}"
        return "".join(parts)
