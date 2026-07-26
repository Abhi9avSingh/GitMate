"""
vscode_watcher.py
-----------------

Detects when the editor (VS Code by default) transitions from running to
closed. GitMate uses this as its primary trigger: you close the editor, and a
few seconds later your work is committed and pushed.

The watcher polls the process list with ``psutil`` on a background thread. When
it sees the editor disappear it invokes the supplied ``on_closed`` callback.
On systems without ``psutil`` it degrades to a no-op so the rest of the app
stays importable and testable.
"""

from __future__ import annotations

import threading
from typing import Callable, Optional

from app.logger.logger import get_logger


class VSCodeWatcher:
    """Poll for the editor process and fire a callback when it closes."""

    def __init__(
        self,
        on_closed: Callable[[], None],
        process_name: str = "Code",
        poll_interval: float = 3.0,
    ) -> None:
        self.on_closed = on_closed
        self.process_name = process_name.lower()
        self.poll_interval = poll_interval
        self.log = get_logger("watcher.vscode")

        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._was_running = False

    # ------------------------------------------------------------------

    def is_editor_running(self) -> bool:
        """Return True if the editor process is currently running."""
        try:
            import psutil
        except Exception:
            return False

        needle = self.process_name
        for proc in psutil.process_iter(["name"]):
            try:
                name = (proc.info.get("name") or "").lower()
                if needle in name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    # ------------------------------------------------------------------

    def _run(self) -> None:
        # Establish the initial state so we only fire on a real transition.
        self._was_running = self.is_editor_running()
        while not self._stop.wait(self.poll_interval):
            running = self.is_editor_running()
            if self._was_running and not running:
                self.log.info("Editor closed - triggering GitMate.")
                try:
                    self.on_closed()
                except Exception as exc:
                    self.log.exception("on_closed callback failed: %s", exc)
            self._was_running = running

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run, name="VSCodeWatcher", daemon=True
        )
        self._thread.start()
        self.log.info("Watching for editor process: %s", self.process_name)

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.poll_interval + 1)
