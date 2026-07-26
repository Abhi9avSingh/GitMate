"""
push_manager.py
---------------

Pushes commits to the remote with GitMate's "push protection" behaviour.

Push protection
---------------
- No changes            -> do not push.
- Push failed / offline -> retry every ``retry_interval`` seconds.
- Keep retrying until successful or ``max_retries`` is reached.
"""

from __future__ import annotations

import time
from typing import Callable, Optional

from git import GitCommandError, Repo

from app.git.repository import RepositoryError, RepositoryManager


class PushError(RepositoryError):
    """Raised when a push ultimately fails."""


class PushManager:
    """Push commits to the configured remote with retries."""

    def __init__(
        self,
        repository: RepositoryManager,
        retry_interval: int = 30,
        max_retries: Optional[int] = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.repository = repository
        self.repo: Repo = repository.repo
        self.retry_interval = retry_interval
        self.max_retries = max_retries  # None => retry indefinitely
        self._sleep = sleep

    # ------------------------------------------------------------------

    def _push_once(self, remote_name: str, branch: str) -> None:
        remote = self.repo.remote(name=remote_name)
        results = remote.push(refspec=f"{branch}:{branch}")

        if not results:
            raise PushError("Push returned no result information.")

        for result in results:
            if result.flags & result.ERROR:
                raise PushError(result.summary.strip() or "Unknown push error.")

    # ------------------------------------------------------------------

    def push(
        self,
        branch: Optional[str] = None,
        remote_name: Optional[str] = None,
    ) -> bool:
        """Push ``branch`` to ``remote_name`` with retries.

        Returns True on success. Raises :class:`PushError` if a remote is
        not configured or all retries are exhausted.
        """
        if not self.repository.has_remote():
            raise PushError("No remote is configured for this repository.")

        branch = branch or self.repository.current_branch
        remote_name = remote_name or self.repository.remote_name or "origin"

        attempt = 0
        while True:
            attempt += 1
            try:
                self._push_once(remote_name, branch)
                return True
            except (GitCommandError, PushError) as exc:
                last_error = exc
                if self.max_retries is not None and attempt >= self.max_retries:
                    raise PushError(
                        f"Push failed after {attempt} attempts: {last_error}"
                    ) from last_error
                self._sleep(self.retry_interval)

    def __repr__(self) -> str:
        return (
            f"PushManager(repo={self.repository.name}, "
            f"retry_interval={self.retry_interval}s)"
        )
