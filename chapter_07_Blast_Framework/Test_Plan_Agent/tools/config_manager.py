"""Configuration persistence for the Test Plan Creator.

Precedence (increasing priority):
    1. Built-in defaults
    2. config/settings.json   (saved from the UI Settings panel)
    3. .env / environment variables

Secrets are never hardcoded; .env is only ever read, never written.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

# ---------------------------------------------------------------- paths ----
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
ENV_FILE = PROJECT_ROOT / ".env"

# ------------------------------------------------------------------ keys ----
SETTING_KEYS = [
    "jira_email",
    "jira_api_token",
    "jira_base_url",
    "jira_api_version",
    "groq_api_key",
    "groq_model",
    "plan_depth",
]

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
DEFAULT_PLAN_DEPTH = "standard"
DEFAULT_JIRA_API_VERSION = "3"


def _defaults() -> dict:
    return {
        "jira_email": "",
        "jira_api_token": "",
        "jira_base_url": "",
        "jira_api_version": DEFAULT_JIRA_API_VERSION,
        "groq_api_key": "",
        "groq_model": DEFAULT_GROQ_MODEL,
        "plan_depth": DEFAULT_PLAN_DEPTH,
    }


# ------------------------------------------------------------- env layer ----
def env_var_name(key: str) -> str:
    return key.upper()


def load_env() -> None:
    """Load the project .env into os.environ without overriding existing vars."""
    if load_dotenv is not None and ENV_FILE.exists():
        load_dotenv(ENV_FILE, override=False)


def read_env_overrides() -> dict:
    overrides = {}
    for key in SETTING_KEYS:
        value = os.environ.get(env_var_name(key))
        if value is not None and value.strip():
            overrides[key] = value.strip()
    return overrides


# ------------------------------------------------------------ json layer ----
def read_json_settings() -> dict:
    if not SETTINGS_FILE.exists():
        return {}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {}
    return {
        k: str(v).strip() if v is not None else ""
        for k, v in data.items()
        if k in SETTING_KEYS
    }


def save_settings(settings: dict) -> None:
    """Persist settings to config/settings.json (creates dir as needed)."""
    clean = {k: str(settings.get(k, "")).strip() for k in SETTING_KEYS}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
        json.dump(clean, fh, indent=2, sort_keys=True)


# ---------------------------------------------------------- public API -----
def load_settings() -> dict:
    """Merge defaults <- settings.json <- .env (env wins)."""
    merged = _defaults()
    merged.update(read_json_settings())
    merged.update(read_env_overrides())
    return merged


def is_jira_configured(settings: dict) -> bool:
    return bool(
        settings.get("jira_email")
        and settings.get("jira_api_token")
        and settings.get("jira_base_url")
    )


def is_groq_configured(settings: dict) -> bool:
    return bool(settings.get("groq_api_key") and settings.get("groq_model"))
