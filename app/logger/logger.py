"""
logger.py
---------

Centralised logging configuration.

Every operation is recorded to a rotating log file in the user's config
directory and, when running from a console, echoed to stderr. The log format
matches the style shown in the GitMate spec, e.g.::

    21:14 VS Code Closed
    21:14 8 files changed
    21:14 AI generated: feat(weather): improve forecast UI
    21:14 Commit Created
    21:14 Push Successful
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.config.settings import default_config_dir

_CONFIGURED = False


def setup_logging(
    level: int = logging.INFO,
    log_dir: Optional[Path] = None,
    console: bool = True,
) -> Path:
    """Configure root logging once and return the log file path."""
    global _CONFIGURED

    log_dir = log_dir or (default_config_dir() / "logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "gitmate.log"

    if _CONFIGURED:
        return log_file

    root = logging.getLogger("gitmate")
    root.setLevel(level)
    root.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    if console:
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        root.addHandler(stream)

    _CONFIGURED = True
    return log_file


def get_logger(name: str = "gitmate") -> logging.Logger:
    """Return a namespaced child logger."""
    if name == "gitmate":
        return logging.getLogger("gitmate")
    return logging.getLogger(f"gitmate.{name}")
