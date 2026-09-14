"""Jira Cloud REST API v3 client.

Fetches one issue (plus comments and the field catalogue) and normalises it
into the stable ``JiraIssue`` shape defined in ``architecture/02_normalize_issue.md``.
All failures raise ``JiraError`` with a user-presentable message.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

import requests

_API_PATH = "/rest/api/3"
_TIMEOUT = (5, 30)  # (connect, read) seconds

# Only the fields a Test Plan needs.
_ISSUE_FIELDS = (
    "summary,description,issuetype,status,priority,labels,components,"
    "fixVersions,assignee,reporter,issuelinks,parent,created,updated,duedate,"
    "subtasks"
)


class JiraError(Exception):
    """Raised when a Jira request fails. Message is safe to show to the user."""


def _clean_base_url(url: str) -> str:
    url = (url or "").strip().rstrip("/")
    if url and not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def _iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


class JiraClient:
    def __init__(self, email: str, api_token: str, base_url: str):
        self.email = (email or "").strip()
        self.api_token = (api_token or "").strip()
        self.base_url = _clean_base_url(base_url)
        self._fields_cache: list | None = None

    # ---------------------------------------------------------- plumbing ----
    def _get(self, path: str, params: dict | None = None) -> requests.Response:
        if not self.base_url:
            raise JiraError("Jira base URL is not configured.")
        if not self.email or not self.api_token:
            raise JiraError(
                "Jira email and API token are required. Add them in Settings."
            )
        url = f"{self.base_url}{path}"
        try:
            return requests.get(
                url,
                auth=(self.email, self.api_token),
                headers={"Accept": "application/json"},
                params=params,
                timeout=_TIMEOUT,
            )
        except requests.exceptions.Timeout:
            raise JiraError(
                f"Timed out connecting to Jira at {self.base_url}. "
                "Check the URL and your network."
            )
        except requests.exceptions.ConnectionError:
            raise JiraError(
                f"Could not reach Jira at {self.base_url}. "
                "Check the URL, your network, or VPN."
            )
        except requests.exceptions.RequestException as exc:  # pragma: no cover
            raise JiraError(f"Unexpected error while contacting Jira: {exc}")

    @staticmethod
    def _raise_for_status(response: requests.Response, issue_key: str = "") -> None:
        code = response.status_code
        if code == 200:
            return
        if code == 404:
            raise JiraError(
                f"Ticket '{issue_key}' was not found on this Jira site."
                if issue_key else "The Jira endpoint was not found (HTTP 404)."
            )
        if code in (401, 403):
            raise JiraError(
                f"Jira rejected the credentials (HTTP {code}). "
                "Check the email / API token in Settings."
            )
        if code == 429:
            retry = response.headers.get("Retry-After", "a moment")
            raise JiraError(
                f"Jira is rate limiting this account (HTTP 429). "
                f"Retry after {retry}."
            )
        if code >= 500:
            raise JiraError(f"Jira server error (HTTP {code}). Try again shortly.")
        raise JiraError(f"Jira returned HTTP {code}: {response.text[:300]}")

    @staticmethod
    def _json(response: requests.Response) -> dict:
        try:
            return response.json()
        except ValueError:
            raise JiraError("Jira returned an unreadable (non-JSON) response.")

    # ------------------------------------------------------ connectivity ----
    def test_connection(self) -> tuple[bool, str]:
        """Verify the base URL and credentials. Returns (ok, message)."""
        try:
            response = self._get(f"{_API_PATH}/myself")
            self._raise_for_status(response)
            data = self._json(response)
        except JiraError as exc:
            return False, str(exc)
        name = data.get("displayName") or data.get("emailAddress") or "unknown user"
        site = data.get("accountId", "")
        return True, f"Connected to Jira as {name}{f' ({site})' if site else ''}."

    # ------------------------------------------------------------ fetch ----
    def get_issue(self, issue_key: str) -> dict:
        issue_key = (issue_key or "").strip().upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9]+-\d+", issue_key or ""):
            raise JiraError(
                f"'{issue_key}' does not look like a Jira ticket ID "
                "(expected something like VWO-49)."
            )

        issue_resp = self._get(
            f"{_API_PATH}/issue/{issue_key}", params={"fields": _ISSUE_FIELDS}
        )
        self._raise_for_status(issue_resp, issue_key)
        payload = self._json(issue_resp)

        fields = payload.get("fields") or {}
        acceptance, acceptance_source = self._find_acceptance_criteria(fields)

        return {
            "key": issue_key,
            "url": f"{self.base_url}/browse/{issue_key}",
            "summary": self._text(fields.get("summary")),
            "description": self._adf_to_text(fields.get("description")),
            "acceptance_criteria": acceptance,
            "acceptance_criteria_source": acceptance_source,
            "issue_type": self._named(fields.get("issuetype")),
            "status": self._named(fields.get("status")),
            "priority": self._named(fields.get("priority")),
            "labels": sorted(self._list_of_text(fields.get("labels"))),
            "components": sorted(
                self._list_of_text(fields.get("components"), key="name")
            ),
            "fix_versions": sorted(
                self._list_of_text(fields.get("fixVersions"), key="name")
            ),
            "assignee": self._person(fields.get("assignee")),
            "reporter": self._person(fields.get("reporter")),
            "created": self._text(fields.get("created")),
            "updated": self._text(fields.get("updated")),
            "due_date": fields.get("duedate") or None,
            "parent": self._parent(fields.get("parent")),
            "subtasks": self._subtasks(fields.get("subtasks")),
            "links": self._links(fields.get("issuelinks")),
            "comments": self._comments(issue_key),
            "fetched_at": _iso_now(),
        }

    # ---------------------------------------------------------- helpers ----
    @staticmethod
    def _text(value: Any) -> str:
        return str(value).strip() if value not in (None, "") else ""

    @classmethod
    def _named(cls, value: Any) -> str:
        if isinstance(value, dict):
            return cls._text(value.get("name") or value.get("value"))
        return cls._text(value)

    @classmethod
    def _person(cls, value: Any) -> str:
        if isinstance(value, dict):
            return cls._text(value.get("displayName") or value.get("name"))
        return ""

    @classmethod
    def _list_of_text(cls, value: Any, key: str | None = None) -> list:
        if not isinstance(value, list):
            return []
        out = []
        for item in value:
            text = cls._named(item) if key else cls._text(item)
            if text:
                out.append(text)
        return out

    @classmethod
    def _parent(cls, value: Any) -> dict | None:
        if not isinstance(value, dict):
            return None
        fields = value.get("fields") or {}
        return {
            "key": cls._text(value.get("key")),
            "summary": cls._text(fields.get("summary")),
        }

    @classmethod
    def _subtasks(cls, value: Any) -> list:
        if not isinstance(value, list):
            return []
        out = []
        for item in value:
            fields = item.get("fields") or {}
            out.append({
                "key": cls._text(item.get("key")),
                "summary": cls._text(fields.get("summary")),
                "status": cls._named(fields.get("status")),
            })
        return sorted(out, key=lambda s: s["key"])

    @classmethod
    def _links(cls, value: Any) -> list:
        if not isinstance(value, list):
            return []
        out = []
        for link in value:
            link_type = link.get("type") or {}
            if link.get("outwardIssue"):
                direction, issue = "outward", link["outwardIssue"]
                label = cls._text(link_type.get("outward"))
            elif link.get("inwardIssue"):
                direction, issue = "inward", link["inwardIssue"]
                label = cls._text(link_type.get("inward"))
            else:
                continue
            out.append({
                "type": label or cls._text(link_type.get("name")),
                "direction": direction,
                "key": cls._text(issue.get("key")),
                "summary": cls._text((issue.get("fields") or {}).get("summary")),
            })
        return sorted(out, key=lambda l: l["key"])

    def _comments(self, issue_key: str) -> list:
        try:
            response = self._get(
                f"{_API_PATH}/issue/{issue_key}/comment", params={"maxResults": 50}
            )
        except JiraError:
            return []  # comments are non-essential; never fail the whole fetch
        if response.status_code != 200:
            return []
        comments = (self._json(response) or {}).get("comments") or []
        out = []
        for comment in comments:
            body = self._adf_to_text(comment.get("body"))
            if not body:
                continue
            out.append({
                "author": self._person(comment.get("author")),
                "created": self._text(comment.get("created")),
                "body": body,
            })
        return out

    # -------------------------------------------- acceptance criteria ----
    def _field_catalogue(self) -> list:
        if self._fields_cache is not None:
            return self._fields_cache
        try:
            response = self._get(f"{_API_PATH}/field")
        except JiraError:
            self._fields_cache = []
            return self._fields_cache
        if response.status_code != 200:
            self._fields_cache = []
            return self._fields_cache
        self._fields_cache = self._json(response) or []
        return self._fields_cache

    def _find_acceptance_criteria(self, fields: dict) -> tuple[str, str]:
        """Return (text, source) where source is 'customfield' or 'none'."""
        for field in self._field_catalogue():
            name = self._text(field.get("name"))
            field_id = self._text(field.get("id"))
            if "acceptance" not in name.lower() or field_id not in fields:
                continue
            text = self._adf_to_text(fields.get(field_id))
            if text:
                return text, "customfield"
        return "", "none"

    # ---------------------------------------------------- ADF parsing ----
    def _adf_to_text(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if not isinstance(value, dict):
            return ""
        if value.get("type") == "doc" and isinstance(value.get("content"), list):
            return "\n".join(self._adf_to_lines(value["content"])).strip()
        return ""

    def _adf_to_lines(self, content: list, indent: int = 0) -> list:
        lines: list = []
        prefix = "  " * indent
        for node in content:
            node_type = node.get("type")
            node_text = self._node_text(node)
            if node_type in ("paragraph", "heading"):
                lines.append(f"{prefix}{node_text}")
            elif node_type in ("bulletList", "orderedList"):
                lines.extend(self._adf_to_lines(node.get("content") or [], indent))
            elif node_type == "listItem":
                lines.append(f"{prefix}- {node_text}")
                lines.extend(
                    self._adf_to_lines(node.get("content") or [], indent + 1)
                )
            elif node_type in ("codeBlock", "blockquote"):
                lines.append(f"{prefix}```")
                lines.extend(
                    self._adf_to_lines(node.get("content") or [], indent)
                )
                lines.append(f"{prefix}```")
            elif node_type == "table":
                for row in node.get("content") or []:
                    cells = [
                        self._node_text(cell).replace("\n", " ")
                        for cell in (row.get("content") or [])
                        if cell.get("type") in ("tableCell", "tableHeader")
                    ]
                    lines.append(" | ".join(cells))
            elif node_type == "mediaSingle":
                lines.append(f"{prefix}[image]")
            elif node_type in ("rule", "hardBreak"):
                lines.append("")
            elif node_text:
                lines.append(f"{prefix}{node_text}")
        return lines

    def _node_text(self, node: dict) -> str:
        if not isinstance(node, dict):
            return ""
        if node.get("type") == "text":
            text = node.get("text") or ""
            marks = node.get("marks") or []
            if any(m.get("type") == "code" for m in marks):
                return f"`{text}`"
            if any(m.get("type") == "strong" for m in marks):
                return f"**{text}**"
            return text
        parts = [self._node_text(child) for child in node.get("content") or []]
        if node.get("type") == "inlineCard":
            return (node.get("attrs") or {}).get("url", "") or "".join(parts)
        if node.get("type") == "mention":
            return f"@{(node.get('attrs') or {}).get('text', '')}"
        return "".join(parts)


def parse_issue_key(text: str) -> str | None:
    """Extract the first Jira-style key (PROJ-123) from free text."""
    match = re.search(r"\b[A-Z][A-Z0-9]+-\d{1,6}\b", text or "", re.IGNORECASE)
    return match.group(0).upper() if match else None
