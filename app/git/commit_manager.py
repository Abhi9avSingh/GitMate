"""
commit_manager.py
-----------------

Stages files and creates commits.

This is where GitMate starts becoming useful::

    AI  ->  "feat(weather): add hourly forecast"  ->  CommitManager
        ->  git add .  ->  git commit  ->  return commit hash

This module NEVER pushes; that belongs to :class:`PushManager`.
"""

from __future__ import annotations

from typing import Optional

from git import Repo

from app.git.repository import RepositoryError, RepositoryManager


class CommitError(RepositoryError):
    """Raised when a commit cannot be created."""


class CommitManager:
    """Stage changes and create commits."""

    def __init__(self, repository: RepositoryManager) -> None:
        self.repository = repository
        self.repo: Repo = repository.repo

    # ------------------------------------------------------------------

    def stage_all(self) -> None:
        """Stage every change, equivalent to ``git add -A``."""
        self.repo.git.add(A=True)

    def has_staged_changes(self) -> bool:
        """Return True if there is something staged to commit."""
        return bool(self.repo.git.diff("--cached", "--name-only").strip())

    # ------------------------------------------------------------------

    def commit(self, message: str, stage: bool = True) -> Optional[str]:
        """Create a commit and return its hash.

        Parameters
        ----------
        message:
            The commit message. Must be non-empty.
        stage:
            When True (default) all changes are staged before committing.

        Returns
        -------
        The new commit hash, or ``None`` when there was nothing to commit.
        """
        if not message or not message.strip():
            raise CommitError("Refusing to commit with an empty message.")

        if stage:
            self.stage_all()

        if not self.has_staged_changes():
            # Nothing to commit - this is a safe no-op, not an error.
            return None

        commit = self.repo.index.commit(message.strip())
        return commit.hexsha

    def __repr__(self) -> str:
        return f"CommitManager(repo={self.repository.name})"
