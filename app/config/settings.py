"""
settings.py
-----------

Application configuration.

Settings are stored as JSON in the user's config directory. The AI API key is
stored separately in the OS keyring when ``keyring`` is available, so it is
never written to disk in plain text. The lookup is provider-aware:

- Gemini : keyring "gemini_api_key", then env ``GEMINI_API_KEY`` /
  ``GOOGLE_API_KEY``.
- OpenAI : keyring "openai_api_key", then env ``OPENAI_API_KEY``.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

_KEYRING_SERVICE = "GitMate"

# Per-provider secret lookup: keyring username + ordered env-var fallbacks.
_PROVIDER_SECRETS = {
    "gemini": {
        "keyring_user": "gemini_api_key",
        "env_vars": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    },
    "openai": {
        "keyring_user": "openai_api_key",
        "env_vars": ("OPENAI_API_KEY",),
    },
}


def default_config_dir() -> Path:
    """Return the per-user config directory for GitMate."""
    if os.name == "nt":  # Windows
        base = os.environ.get("APPDATA", str(Path.home()))
    else:  # macOS / Linux
        base = os.environ.get(
            "XDG_CONFIG_HOME", str(Path.home() / ".config")
        )
    return Path(base) / "GitMate"


@dataclass
class Settings:
    """User-configurable settings for GitMate."""

    repository_path: str = ""
    branch: str = "main"
    remote: str = "origin"
    ai_provider: str = "gemini"
    ai_model: str = "gemini-1.5-flash"
    start_with_os: bool = True
    debounce_seconds: int = 15
    push_retry_interval: int = 30
    watch_editor_process: str = "Code"  # process name to detect (VS Code)

    # Not serialised to the JSON file - resolved at runtime.
    api_key: Optional[str] = field(default=None, repr=False)

    def to_public_dict(self) -> dict:
        """Return a dict safe to write to disk (without the API key)."""
        data = asdict(self)
        data.pop("api_key", None)
        return data


class SettingsStore:
    """Load and persist :class:`Settings`."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        self.config_dir = config_dir or default_config_dir()
        self.config_file = self.config_dir / "settings.json"

    # ------------------------------------------------------------------

    def load(self) -> Settings:
        settings = Settings()
        if self.config_file.exists():
            try:
                raw = json.loads(self.config_file.read_text(encoding="utf-8"))
                known = {f: raw[f] for f in raw if f in Settings.__annotations__}
                known.pop("api_key", None)
                settings = Settings(**known)
            except (json.JSONDecodeError, TypeError, OSError):
                settings = Settings()
        settings.api_key = self._load_api_key(settings.ai_provider)
        return settings

    def save(self, settings: Settings) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(
            json.dumps(settings.to_public_dict(), indent=2),
            encoding="utf-8",
        )
        if settings.api_key:
            self._save_api_key(settings.ai_provider, settings.api_key)

    # ------------------------------------------------------------------

    @staticmethod
    def _secret_config(provider: str) -> dict:
        return _PROVIDER_SECRETS.get(
            (provider or "gemini").lower(), _PROVIDER_SECRETS["gemini"]
        )

    def _load_api_key(self, provider: str) -> Optional[str]:
        cfg = self._secret_config(provider)
        try:
            import keyring

            stored = keyring.get_password(_KEYRING_SERVICE, cfg["keyring_user"])
            if stored:
                return stored
        except Exception:
            pass
        for env_var in cfg["env_vars"]:
            value = os.environ.get(env_var)
            if value:
                return value
        return None

    def _save_api_key(self, provider: str, api_key: str) -> None:
        cfg = self._secret_config(provider)
        try:
            import keyring

            keyring.set_password(_KEYRING_SERVICE, cfg["keyring_user"], api_key)
        except Exception:
            # Keyring unavailable - the key simply won't be persisted; the
            # user can still supply it via an environment variable.
            pass
