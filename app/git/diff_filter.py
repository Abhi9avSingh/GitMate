"""
diff_filter.py
--------------

Decides which files are relevant when building a diff for the AI.

Keeping this logic separate from :class:`DiffManager` means the filtering
rules are reusable and easy to unit-test, and DiffManager can stay focused on
generating diffs.

Rules
-----
- Ignore common dependency / build / editor directories.
- Ignore binary and generated assets by extension.
- Ignore files above a configurable size.
- Respect the repository's ``.gitignore`` (Git already excludes those from
  tracked diffs; this adds belt-and-braces filtering for untracked files).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence

# Directory names that should never be sent to the AI.
DEFAULT_IGNORED_DIRS: frozenset[str] = frozenset(
    {
        "node_modules",
        "dist",
        "build",
        ".venv",
        "venv",
        "env",
        ".idea",
        ".vscode",
        "__pycache__",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".next",
        ".turbo",
        "coverage",
        "target",
        "out",
    }
)

# File extensions that are binary or generated and add no value to a diff.
DEFAULT_IGNORED_EXTENSIONS: frozenset[str] = frozenset(
    {
        # Images
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".svg",
        # Fonts
        ".woff", ".woff2", ".ttf", ".otf", ".eot",
        # Media
        ".mp4", ".mov", ".avi", ".mp3", ".wav", ".flac",
        # Archives
        ".zip", ".tar", ".gz", ".7z", ".rar",
        # Compiled / binary
        ".exe", ".dll", ".so", ".dylib", ".pyc", ".class", ".o", ".a",
        # Data / lock files that are usually noise
        ".lock", ".log",
        # Documents
        ".pdf",
    }
)


class DiffFilter:
    """Filter a list of changed files down to the ones worth diffing."""

    def __init__(
        self,
        repo_path: str | Path,
        max_file_size: int = 1024 * 1024,
        ignored_dirs: Iterable[str] | None = None,
        ignored_extensions: Iterable[str] | None = None,
    ) -> None:
        self.repo_path = Path(repo_path)
        self.max_file_size = max_file_size
        self.ignored_dirs = frozenset(ignored_dirs) if ignored_dirs else DEFAULT_IGNORED_DIRS
        self.ignored_extensions = (
            frozenset(e.lower() for e in ignored_extensions)
            if ignored_extensions
            else DEFAULT_IGNORED_EXTENSIONS
        )

    # ------------------------------------------------------------------

    def is_ignored(self, relative_path: str) -> bool:
        """Return True if ``relative_path`` should be excluded from a diff."""
        path = Path(relative_path)

        # Directory-based rules.
        parts = set(path.parts)
        if parts & self.ignored_dirs:
            return True

        # Extension-based rules.
        if path.suffix.lower() in self.ignored_extensions:
            return True

        # Size-based rules.
        absolute = self.repo_path / path
        try:
            if absolute.exists() and absolute.stat().st_size > self.max_file_size:
                return True
        except OSError:
            return True

        return False

    def filter(self, files: Sequence[str]) -> List[str]:
        """Return only the files that are relevant for a diff."""
        return [f for f in files if not self.is_ignored(f)]

    def __repr__(self) -> str:
        return (
            f"DiffFilter(max_file_size={self.max_file_size}, "
            f"ignored_dirs={len(self.ignored_dirs)}, "
            f"ignored_extensions={len(self.ignored_extensions)})"
        )
