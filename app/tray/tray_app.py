"""
tray_app.py
-----------

The only UI GitMate has: a system-tray icon with a small menu::

    GitMate
    Status       \u25cf Watching
    Repository   WeatherApp
    Last Push    2 minutes ago
    -------------
    Push Now
    Open Logs
    Settings
    Exit

Built on ``pystray`` + ``Pillow``. If those libraries are unavailable (for
example in a headless/test environment) the class still constructs so it can be
unit-tested; only :meth:`run` requires the GUI stack.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional

from app.config.settings import default_config_dir
from app.logger.logger import get_logger
from app.services.gitmate_service import GitMateService
from app.utils.helpers import format_relative_time


class TrayApp:
    """System-tray front-end for :class:`GitMateService`."""

    def __init__(self, service: GitMateService) -> None:
        self.service = service
        self.log = get_logger("tray")
        self._icon = None

    # ------------------------------------------------------------------
    # Menu callbacks
    # ------------------------------------------------------------------

    def _status_text(self, _item=None) -> str:
        return "\u25cf Watching" if self.service.is_running else "\u25cb Paused"

    def _repo_text(self, _item=None) -> str:
        return f"Repository: {self.service.engine.repository.name}"

    def _last_push_text(self, _item=None) -> str:
        ts = self.service.engine.last_push_time
        return f"Last Push: {format_relative_time(ts)}"

    def _on_push_now(self, _icon=None, _item=None) -> None:
        threading.Thread(target=self.service.push_now, daemon=True).start()

    def _on_open_logs(self, _icon=None, _item=None) -> None:
        log_file = default_config_dir() / "logs" / "gitmate.log"
        self._open_path(log_file)

    def _on_settings(self, _icon=None, _item=None) -> None:
        self._open_path(default_config_dir() / "settings.json")

    def _on_exit(self, _icon=None, _item=None) -> None:
        self.service.stop()
        if self._icon:
            self._icon.stop()

    @staticmethod
    def _open_path(path: Path) -> None:
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(path))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Icon
    # ------------------------------------------------------------------

    def _build_image(self):
        from PIL import Image, ImageDraw

        size = 64
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((4, 4, size - 4, size - 4), fill=(34, 139, 87, 255))
        draw.ellipse((26, 12, 38, 24), fill=(255, 255, 255, 255))
        draw.rectangle((30, 22, 34, 52), fill=(255, 255, 255, 255))
        return image

    def _build_menu(self):
        from pystray import Menu, MenuItem

        return Menu(
            MenuItem(lambda item: "GitMate", None, enabled=False),
            MenuItem(self._status_text, None, enabled=False),
            MenuItem(self._repo_text, None, enabled=False),
            MenuItem(self._last_push_text, None, enabled=False),
            Menu.SEPARATOR,
            MenuItem("Push Now", self._on_push_now),
            MenuItem("Open Logs", self._on_open_logs),
            MenuItem("Settings", self._on_settings),
            Menu.SEPARATOR,
            MenuItem("Exit", self._on_exit),
        )

    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start the service and the tray icon (blocking)."""
        try:
            import pystray  # noqa: F401
            from PIL import Image  # noqa: F401
        except Exception as exc:
            raise RuntimeError(
                "The tray UI requires 'pystray' and 'Pillow'. "
                "Install them or run GitMate in headless/CLI mode."
            ) from exc

        import pystray

        self.service.start()
        self._icon = pystray.Icon(
            "GitMate",
            icon=self._build_image(),
            title="GitMate",
            menu=self._build_menu(),
        )
        self.log.info("Starting tray icon.")
        self._icon.run()
