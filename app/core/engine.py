"""
engine.py
---------

The orchestrator that ties every module together. This is the heart of
GitMate: it runs the full pipeline described in the spec::

    detect changes -> build AI-ready diff -> generate message
        -> commit -> push (with retries) -> notify + log

The engine is deliberately UI-agnostic so it can be driven by the tray app,
the CLI, or the test-suite in exactly the same way.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Optional

from app.ai.commit_generator import CommitMessageGenerator
from app.ai.provider import build_provider
from app.config.settings import Settings
from app.git.commit_manager import CommitManager
from app.git.diff_filter import DiffFilter
from app.git.diff_manager import DiffManager
from app.git.push_manager import PushError, PushManager
from app.git.repository import RepositoryManager
from app.logger.logger import get_logger
from app.notifications.notifier import Notifier


@dataclass
class SyncResult:
    """Outcome of a single sync (commit + push) run."""

    committed: bool
    pushed: bool
    message: Optional[str] = None
    commit_hash: Optional[str] = None
    changed_files: int = 0
    error: Optional[str] = None
    skipped_reason: Optional[str] = None


class GitMateEngine:
    """Coordinate the whole commit-and-push pipeline."""

    def __init__(
        self,
        settings: Settings,
        notifier: Optional[Notifier] = None,
    ) -> None:
        self.settings = settings
        self.log = get_logger("engine")
        self.notifier = notifier or Notifier()
        self._lock = threading.Lock()
        self.last_push_time: Optional[float] = None

        self.repository = RepositoryManager(settings.repository_path)

        diff_filter = DiffFilter(self.repository.repo_path)
        self.diff_manager = DiffManager(self.repository, diff_filter)
        self.commit_manager = CommitManager(self.repository)
        self.push_manager = PushManager(
            self.repository, retry_interval=settings.push_retry_interval
        )
        self.generator = CommitMessageGenerator(self._build_provider(settings))

    # ------------------------------------------------------------------

    @staticmethod
    def _build_provider(settings: Settings):
        if not settings.api_key:
            return None
        try:
            return build_provider(
                settings.ai_provider, settings.api_key, settings.ai_model
            )
        except Exception:
            return None

    # ------------------------------------------------------------------

    def sync(self, push: bool = True) -> SyncResult:
        """Run one full commit (+ optional push) cycle.

        Thread-safe: overlapping triggers are serialised so we never create
        competing commits.
        """
        with self._lock:
            return self._sync_locked(push=push)

    def _sync_locked(self, push: bool) -> SyncResult:
        # 1. Push protection: nothing to do when there are no changes.
        if not self.repository.has_changes():
            self.log.info("No changes - nothing to commit.")
            return SyncResult(
                committed=False, pushed=False, skipped_reason="no_changes"
            )

        changed = self.diff_manager.relevant_files()
        self.log.info("%d file(s) changed", len(changed))

        # 2. Build the AI-ready diff and generate a commit message.
        diff = self.diff_manager.ai_ready_diff()
        message = self.generator.generate(diff, changed)
        self.log.info("AI generated: %s", message)

        # 3. Commit.
        try:
            commit_hash = self.commit_manager.commit(message)
        except Exception as exc:
            self.log.exception("Commit failed: %s", exc)
            self.notifier.error("Commit failed")
            return SyncResult(
                committed=False, pushed=False, message=message, error=str(exc)
            )

        if commit_hash is None:
            return SyncResult(
                committed=False, pushed=False, skipped_reason="nothing_staged"
            )

        self.log.info("Commit created: %s", commit_hash[:7])

        if not push:
            return SyncResult(
                committed=True,
                pushed=False,
                message=message,
                commit_hash=commit_hash,
                changed_files=len(changed),
            )

        # 4. Push with retries (handled inside PushManager).
        try:
            self.push_manager.push(
                branch=self.settings.branch or None,
                remote_name=self.settings.remote or None,
            )
        except PushError as exc:
            self.log.error("Push failed: %s", exc)
            self.notifier.error("Push failed")
            return SyncResult(
                committed=True,
                pushed=False,
                message=message,
                commit_hash=commit_hash,
                changed_files=len(changed),
                error=str(exc),
            )

        self.last_push_time = time.time()
        self.log.info("Push successful")
        self.notifier.success("Successfully pushed to GitHub")
        return SyncResult(
            committed=True,
            pushed=True,
            message=message,
            commit_hash=commit_hash,
            changed_files=len(changed),
        )

    # ------------------------------------------------------------------

    def status(self) -> dict:
        """Return a snapshot suitable for the tray UI / dashboard."""
        info = self.repository.info()
        info["last_push_time"] = self.last_push_time
        info["ai_enabled"] = self.generator.provider is not None
        return info
