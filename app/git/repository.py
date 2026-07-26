"""
repository.py
-------------

Core Git repository abstraction used throughout GitMate.

Responsibilities
----------------
- Validate a repository
- Open an existing repository
- Read repository information
- Detect file changes
- Return changed files
- Expose branch & remote information

This class NEVER performs:
- commits
- pushes
- pulls

Those responsibilities belong to CommitManager and PushManager.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from git import InvalidGitRepositoryError, NoSuchPathError, Repo


class RepositoryError(Exception):
    """Base repository exception."""


class RepositoryNotFoundError(RepositoryError):
    """Raised when the repository path does not exist."""


class InvalidRepositoryError(RepositoryError):
    """Raised when the directory is not a Git repository."""


class RepositoryManager:
    """High level wrapper around GitPython.

    Example
    -------
    >>> repo = RepositoryManager("D:/Projects/WeatherApp")
    >>> if repo.has_changes():
    ...     print(repo.changed_files())
    """

    def __init__(self, repo_path: str | Path) -> None:
        self.repo_path = Path(repo_path).expanduser().resolve()

        if not self.repo_path.exists():
            raise RepositoryNotFoundError(
                f"Repository does not exist: {self.repo_path}"
            )

        try:
            self.repo = Repo(self.repo_path)
        except (InvalidGitRepositoryError, NoSuchPathError) as exc:
            raise InvalidRepositoryError(str(exc)) from exc

    # ---------------------------------------------------------
    # Repository Information
    # ---------------------------------------------------------

    @property
    def name(self) -> str:
        return self.repo_path.name

    @property
    def current_branch(self) -> str:
        try:
            return self.repo.active_branch.name
        except TypeError:
            # Detached HEAD state.
            return self.repo.head.commit.hexsha[:7]

    @property
    def current_commit(self) -> str:
        return self.repo.head.commit.hexsha

    @property
    def short_commit(self) -> str:
        return self.current_commit[:7]

    @property
    def remote_name(self) -> Optional[str]:
        if not self.repo.remotes:
            return None
        return self.repo.remotes[0].name

    @property
    def remote_url(self) -> Optional[str]:
        if not self.repo.remotes:
            return None
        return self.repo.remotes[0].url

    def has_remote(self) -> bool:
        return bool(self.repo.remotes)

    # ---------------------------------------------------------
    # Repository Status
    # ---------------------------------------------------------

    def is_dirty(self) -> bool:
        """Return True if the repo has modified, staged or untracked files."""
        return self.repo.is_dirty(untracked_files=True)

    def has_changes(self) -> bool:
        return self.is_dirty()

    def changed_files(self) -> List[str]:
        """Return a sorted list of changed file paths."""
        changed = set()

        # Modified / staged (relative to working tree and index).
        changed.update(self.repo.git.diff("--name-only").splitlines())
        changed.update(self.repo.git.diff("--cached", "--name-only").splitlines())

        # Untracked.
        changed.update(self.repo.untracked_files)

        return sorted(f for f in changed if f)

    def untracked_files(self) -> List[str]:
        return sorted(self.repo.untracked_files)

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def total_commits(self) -> int:
        try:
            return sum(1 for _ in self.repo.iter_commits())
        except ValueError:
            # Repository has no commits yet.
            return 0

    def last_commit_message(self) -> str:
        try:
            return self.repo.head.commit.message.strip()
        except ValueError:
            return ""

    def last_commit_author(self) -> str:
        try:
            return self.repo.head.commit.author.name
        except ValueError:
            return ""

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def exists(self) -> bool:
        return self.repo_path.exists()

    def is_git_repository(self) -> bool:
        return self.repo.git_dir is not None

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def info(self) -> dict:
        """Return repository information suitable for dashboards and logging."""
        return {
            "name": self.name,
            "path": str(self.repo_path),
            "branch": self.current_branch,
            "remote": self.remote_name,
            "remote_url": self.remote_url,
            "dirty": self.is_dirty(),
            "changed_files": len(self.changed_files()),
            "last_commit": self.short_commit if self.total_commits() else None,
        }

    def __repr__(self) -> str:
        return (
            f"RepositoryManager(name={self.name}, branch={self.current_branch})"
        )
