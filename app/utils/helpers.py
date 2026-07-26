"""
helpers.py
----------

Small, dependency-free helper functions used across GitMate.
"""

from __future__ import annotations

import time
from typing import Optional


def human_size(num_bytes: int) -> str:
    """Return a human-readable file size, e.g. ``1.2 MB``."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def truncate(text: str, limit: int, suffix: str = "...") -> str:
    """Truncate ``text`` to ``limit`` characters."""
    if len(text) <= limit:
        return text
    return text[: max(0, limit - len(suffix))] + suffix


def format_relative_time(timestamp: Optional[float], now: Optional[float] = None) -> str:
    """Return a friendly relative time such as ``2 minutes ago``."""
    if timestamp is None:
        return "never"
    now = now if now is not None else time.time()
    delta = int(max(0, now - timestamp))

    if delta < 5:
        return "just now"
    if delta < 60:
        return f"{delta} seconds ago"
    minutes = delta // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ago"
