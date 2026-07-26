"""
gitmate_service.py
------------------

Application service layer.

Binds the triggers (editor-close watcher and optional file watcher) to the
:class:`GitMateEngine`, applies the configured debounce, and exposes a clean
lifecycle API: ``start()``, ``stop()`` and ``push_now()``.
"""

from __future__ import annotations

import threading
from typing import Optional

from app.config.settings import Settings
from app.core.engine import GitMateEngine, SyncResult
from app.logger.logger import get_logger
from app.notifications.notifier import Notifier
from app.watcher.vscode_watcher import VSCodeWatcher


class GitMateService:
    """High-level, UI-agnostic controller for GitMate."""

    def __init__(
        self,
        settings: Settings,
        engine: Optional[GitMateEngine] = None,
        notifier: Optional[Notifier] = None,
    ) -> None:
        self.settings = settings
        self.log = get_logger("service")
        self.notifier = notifier or Notifier()
        self.engine = engine or GitMateEngine(settings, self.notifier)

        self._watcher = VSCodeWatcher(
            on_closed=self._on_editor_closed,
            process_name=settings.watch_editor_process,
        )
        self._running = False

    # ------------------------------------------------------------------

    def _on_editor_closed(self) -> None:
        """Debounce, then run a sync when the editor is closed."""
        delay = max(0, int(self.settings.debounce_seconds))
        self.log.info("Editor closed - waiting %ds before syncing.", delay)
        timer = threading.Timer(delay, self._safe_sync)
        timer.daemon = True
        timer.start()

    def _safe_sync(self) -> Optional[SyncResult]:
        try:
            return self.engine.sync(push=True)
        except Exception as exc:
            self.log.exception("Sync failed: %s", exc)
            self.notifier.error("GitMate sync failed")
            return None

    # ------------------------------------------------------------------

    def push_now(self) -> Optional[SyncResult]:
        """Manually trigger a commit + push (used by the tray "Push Now")."""
        self.log.info("Manual push requested.")
        return self._safe_sync()

    def start(self) -> None:
        if self._running:
            return
        self._watcher.start()
        self._running = True
        self.log.info("GitMate service started - watching %s", self.engine.repository.name)

    def stop(self) -> None:
        if not self._running:
            return
        self._watcher.stop()
        self._running = False
        self.log.info("GitMate service stopped.")

    @property
    def is_running(self) -> bool:
        return self._running

    def status(self) -> dict:
        data = self.engine.status()
        data["running"] = self._running
        return data
