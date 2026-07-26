"""GitMate application services.

The :class:`GitMateService` wires the watchers to the engine and exposes a
simple start/stop/push-now API that the tray UI (or a CLI) drives.
"""

from __future__ import annotations

from app.services.gitmate_service import GitMateService

__all__ = ["GitMateService"]
