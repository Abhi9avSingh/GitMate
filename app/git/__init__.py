"""GitMate Git engine.

This package contains every module that interacts with Git. Responsibilities
are deliberately split into small, single-purpose classes so the code stays
easy to test and maintain:

- ``RepositoryManager`` - represents and inspects a repository (read only).
- ``DiffFilter``        - decides which files are relevant for a diff.
- ``DiffManager``       - produces clean, AI-ready diffs.
- ``CommitManager``     - stages files and creates commits.
- ``PushManager``       - pushes commits to the remote with retries.
"""

from __future__ import annotations

from app.git.commit_manager import CommitError, CommitManager
from app.git.diff_filter import DiffFilter
from app.git.diff_manager import DiffManager
from app.git.push_manager import PushError, PushManager
from app.git.repository import (
    InvalidRepositoryError,
    RepositoryError,
    RepositoryManager,
    RepositoryNotFoundError,
)

__all__ = [
    "RepositoryManager",
    "RepositoryError",
    "RepositoryNotFoundError",
    "InvalidRepositoryError",
    "DiffFilter",
    "DiffManager",
    "CommitManager",
    "CommitError",
    "PushManager",
    "PushError",
]
