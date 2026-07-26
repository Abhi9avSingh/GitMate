"""End-to-end engine test using a local repo + bare remote (no network)."""

from __future__ import annotations

from app.config.settings import Settings
from app.core.engine import GitMateEngine


def _settings_for(repo):
    return Settings(
        repository_path=str(repo.repo_path),
        branch=repo.current_branch,
        remote="origin",
        api_key=None,  # forces deterministic fallback message
    )


def test_sync_no_changes(temp_repo):
    engine = GitMateEngine(_settings_for(temp_repo))
    result = engine.sync(push=False)
    assert not result.committed
    assert result.skipped_reason == "no_changes"


def test_sync_commits_and_pushes(temp_repo):
    (temp_repo.repo_path / "feature.py").write_text("x = 1\n", encoding="utf-8")
    engine = GitMateEngine(_settings_for(temp_repo))
    result = engine.sync(push=True)

    assert result.committed
    assert result.pushed
    assert result.commit_hash
    assert result.message  # fallback message present
