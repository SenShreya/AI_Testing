"""Configuration persistence module.

Loads settings from (in increasing precedence):
  1. Built-in defaults
  2. config/settings.json  (saved from the Settings panel)
  3. Environment variables / a project-level .env file

Secrets are never hardcoded.  The .env file is treated as user-provided
input and is only *read*; the Settings panel persists to settings.json.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency missing
    load_dotenv = None

# ---------------------------------------------------------------- paths ----
# Project root is the folder that contains this file (chapter_03_Jira_TestCase).
PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = PROJECT_ROOT / "config"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
ENV_FILE = PROJECT_ROOT / ".env"

# ------------------------------------------------------------------ keys ----
# Canonical (lower-case) setting keys.  The matching environment variable
# is the UPPER_SNAKE version of the key.
SETTING_KEYS = [
    "jira_email",
    "jira_api_token",
    "jira_base_url",
    "ollama_url",
    "ollama_model",
    "groq_api_key",
    "groq_model",
]

DEFAULT_OLLAMA_URL = "http://localhost:11434"
# Change these defaults to the models actually available on your machine /
# on Groq.  Run `ollama list` to see pulled models.
DEFAULT_OLLAMA_MODEL = "gemma3:12b"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"


def _defaults() -> dict:
    return {
        "jira_email": "",
        "jira_api_token": "",
        "jira_base_url": "",
        "ollama_url": DEFAULT_OLLAMA_URL,
        "ollama_model": DEFAULT_OLLAMA_MODEL,
        "groq_api_key": "",
        "groq_model": DEFAULT_GROQ_MODEL,
    }


# ------------------------------------------------------------- env layer ----
def env_var_name(key: str) -> str:
    return key.upper()


def load_env() -> None:
    """Load the project .env file into os.environ (does not override)."""
    if load_dotenv is not None and ENV_FILE.exists():
        load_dotenv(ENV_FILE, override=False)


def read_env_overrides() -> dict:
    """Return the subset of settings that are present in os.environ."""
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
        return {k: str(v).strip() if v is not None else "" for k, v in data.items() if k in SETTING_KEYS}
    except (json.JSONDecodeError, OSError):
        return {}


def save_json_settings(settings: dict) -> None:
    """Persist settings to config/settings.json (creates dir/file as needed)."""
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


def save_settings(settings: dict) -> None:
    """Persist a settings dict.  Stored in JSON only; .env is read-only here."""
    save_json_settings(settings)


def get_setting(key: str) -> str:
    """Convenience helper for callers holding a settings dict."""
    return load_settings().get(key, "")


def is_configured(settings: dict) -> bool:
    """True when the settings needed for a Jira fetch are present."""
    return bool(settings.get("jira_email") and settings.get("jira_api_token")
                and settings.get("jira_base_url"))
