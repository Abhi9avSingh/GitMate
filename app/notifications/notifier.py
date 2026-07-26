"""
notifier.py
-----------

Cross-platform desktop notifications.

On Windows GitMate uses native toast notifications via ``win10toast`` (or
``plyer`` if present). On other platforms it degrades gracefully to logging so
the app remains fully testable off Windows.
"""

from __future__ import annotations

from app.logger.logger import get_logger


class Notifier:
    """Send desktop notifications, falling back to logs when unavailable."""

    def __init__(self, app_name: str = "GitMate") -> None:
        self.app_name = app_name
        self.log = get_logger("notifications")
        self._backend = self._detect_backend()

    # ------------------------------------------------------------------

    def _detect_backend(self) -> str:
        try:
            import win10toast  # noqa: F401

            return "win10toast"
        except Exception:
            pass
        try:
            import plyer  # noqa: F401

            return "plyer"
        except Exception:
            pass
        return "log"

    # ------------------------------------------------------------------

    def notify(self, title: str, message: str) -> None:
        """Display a notification (or log it if no backend is available)."""
        try:
            if self._backend == "win10toast":
                from win10toast import ToastNotifier

                ToastNotifier().show_toast(title, message, duration=5, threaded=True)
            elif self._backend == "plyer":
                from plyer import notification

                notification.notify(
                    title=title, message=message, app_name=self.app_name, timeout=5
                )
            else:
                self.log.info("NOTIFY: %s - %s", title, message)
        except Exception as exc:  # never let a notification crash the app
            self.log.warning("Notification failed (%s): %s", self._backend, exc)

    # Convenience helpers -------------------------------------------------

    def success(self, message: str) -> None:
        self.notify(self.app_name, f"\u2713 {message}")

    def error(self, message: str) -> None:
        self.notify(self.app_name, f"\u2717 {message}")
