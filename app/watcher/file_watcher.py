"""
file_watcher.py
---------------

Watches the repository for file changes using ``watchdog`` and fires a
debounced callback. This is an optional secondary trigger (the primary trigger
is the editor closing) and can be used for "commit after N seconds of
inactivity" style behaviour.

If ``watchdog`` is not installed the watcher becomes a no-op.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable, Optional

from app.logger.logger import get_logger


class FileWatcher:
    """Debounced repository file watcher."""

    def __init__(
        self,
        repo_path: str | Path,
        on_change: Callable[[], None],
        debounce_seconds: float = 15.0,
    ) -> None:
        self.repo_path = str(Path(repo_path))
        self.on_change = on_change
        self.debounce_seconds = debounce_seconds
        self.log = get_logger("watcher.files")

        self._observer = None
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------------

    def _schedule(self) -> None:
        """(Re)start the debounce timer on each change event."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_seconds, self._fire)
            self._timer.daemon = True
            self._timer.start()

    def _fire(self) -> None:
        try:
            self.on_change()
        except Exception as exc:
            self.log.exception("on_change callback failed: %s", exc)

    # ------------------------------------------------------------------

    def start(self) -> None:
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except Exception:
            self.log.warning("watchdog not available - file watching disabled.")
            return

        watcher = self

        class _Handler(FileSystemEventHandler):
            def on_any_event(self, event):
                if ".git" in Path(event.src_path).parts:
                    return
                watcher._schedule()

        self._observer = Observer()
        self._observer.schedule(_Handler(), self.repo_path, recursive=True)
        self._observer.start()
        self.log.info("Watching files in %s", self.repo_path)

    def stop(self) -> None:
        with self._lock:
            if self._timer:
                self._timer.cancel()
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
