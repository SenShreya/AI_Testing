# SOP 01 — Fetch a Jira Issue

**Layer:** 1 (Architecture)
**Tool:** `tools/jira_client.py`
**Status:** Active

---

## Goal

Given a Jira issue key, retrieve the issue and everything a Test Plan needs,
using the Jira Cloud REST API v3, and surface failures as clear, human-readable
errors.

## Inputs

| Input | Source | Required |
|---|---|---|
| `jira_email` | settings / `.env` | yes |
| `jira_api_token` | settings / `.env` | yes |
| `jira_base_url` | settings / `.env` | yes |
| `issue_key` | parsed from the user's prompt | yes |

## Auth

HTTP **Basic** auth: `Authorization: Basic base64(email:api_token)`.
The token is an **Atlassian API token**, never the account password.

## Requests (in order)

1. **Issue** — `GET {base}/rest/api/3/issue/{key}`
   with `fields=summary,description,issuetype,status,priority,labels,components,fixVersions,assignee,reporter,issuelinks,parent,created,updated,duedate,subtasks`.
2. **Comments** — `GET {base}/rest/api/3/issue/{key}/comment?maxResults=50`.
3. **Field catalogue** — `GET {base}/rest/api/3/field` (cached per run) to
   resolve the site-specific acceptance-criteria custom field by name.

All calls use `timeout=(5, 30)` and `Accept: application/json`.

## Connectivity test

`GET {base}/rest/api/3/myself` → 200 means the URL **and** credentials are
valid. This is what the UI's *Test Jira Connection* button calls.

## Edge cases

- Base URL missing scheme → prepend `https://`.
- Trailing slash → stripped.
- No `description` / no acceptance criteria → fields become empty strings
  (never `null`); downstream renders `Not specified`.
- Custom field whose name matches `/acceptance criteria/i` → used and marked as
  `customfield`. If none found, left empty and marked `none`.

## Errors (typed `JiraError`, never a raw traceback)

| HTTP / condition | Message |
|---|---|
| 401 / 403 | credentials rejected — check email / API token |
| 404 | ticket not found on this site |
| 400 | Jira returned the error text (first 300 chars) |
| 429 | rate limited — back off (honour `Retry-After`) |
| 5xx | Jira server error |
| timeout | timed out connecting to Jira |
| connection error | could not reach Jira — check URL / network / VPN |
| non-JSON body | unreadable (non-JSON) response |

## Golden rule

If this logic changes, **update this SOP before changing the code.**
