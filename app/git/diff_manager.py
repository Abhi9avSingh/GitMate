"""
diff_manager.py
----------------

Handles Git diff generation for GitMate.

Responsibilities
----------------
- Generate repository diffs (staged / unstaged / full)
- Delegate file filtering to :class:`DiffFilter`
- Limit diff size
- Produce AI-ready output

This module NEVER:
- commits
- pushes
- stages files
"""

from __future__ import annotations

from typing import List, Optional

from git import Repo

from app.git.diff_filter import DiffFilter
from app.git.repository import RepositoryManager


class DiffManager:
    """Produce clean, AI-ready diffs from a repository."""

    MAX_DIFF_SIZE = 25_000  # characters
    MAX_FILE_SIZE = 1024 * 1024  # 1 MB

    def __init__(
        self,
        repository: RepositoryManager,
        diff_filter: Optional[DiffFilter] = None,
    ) -> None:
        self.repository = repository
        self.repo: Repo = repository.repo
        self.diff_filter = diff_filter or DiffFilter(
            repository.repo_path, max_file_size=self.MAX_FILE_SIZE
        )

    # -----------------------------------------------------

    def staged_diff(self) -> str:
        """Return staged changes."""
        return self.repo.git.diff("--cached")

    def unstaged_diff(self) -> str:
        """Return unstaged changes."""
        return self.repo.git.diff()

    def full_diff(self) -> str:
        """Return staged + unstaged diff."""
        return f"{self.staged_diff()}\n{self.unstaged_diff()}"

    # -----------------------------------------------------

    def changed_files(self) -> List[str]:
        return self.repository.changed_files()

    def relevant_files(self) -> List[str]:
        """Changed files with binary / large / ignored files removed."""
        return self.diff_filter.filter(self.changed_files())

    # -----------------------------------------------------

    def ai_ready_diff(self) -> str:
        """Return a cleaned diff suitable for AI commit generation.

        Pipeline: changed files -> filter -> per-file diff -> size cap.
        """
        files = self.relevant_files()
        if not files:
            return ""

        # Include new (untracked) files by diffing against the empty tree.
        tracked_diff_parts: List[str] = []
        untracked = set(self.repository.untracked_files())

        for file in files:
            try:
                if file in untracked:
                    diff = self.repo.git.diff(
                        "--no-index", "/dev/null", file, with_exceptions=False
                    )
                else:
                    diff = self.repo.git.diff("HEAD", "--", file)
                if diff and diff.strip():
                    tracked_diff_parts.append(diff)
            except Exception:
                # A single unreadable file must never break the whole diff.
                continue

        result = "\n".join(tracked_diff_parts)

        if len(result) > self.MAX_DIFF_SIZE:
            result = result[: self.MAX_DIFF_SIZE] + "\n\n... Diff Truncated ..."

        return result

    # -----------------------------------------------------

    def summary(self) -> dict:
        files = self.relevant_files()
        return {
            "changed_files": len(files),
            "files": files,
            "diff_size": len(self.ai_ready_diff()),
        }

    def has_changes(self) -> bool:
        return len(self.relevant_files()) > 0
