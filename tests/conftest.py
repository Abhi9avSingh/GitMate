"""Shared pytest fixtures.

Creates a throwaway Git repository (with a fake ``origin`` remote pointing at
another local bare repo) so the Git engine can be exercised end-to-end without
any network access.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make the project importable when running from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from git import Repo  # noqa: E402


@pytest.fixture()
def temp_repo(tmp_path):
    """Return a RepositoryManager pointing at a fresh repo with a remote."""
    from app.git.repository import RepositoryManager

    work = tmp_path / "work"
    work.mkdir()
    repo = Repo.init(work)
    repo.config_writer().set_value("user", "name", "Test").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    # Initial commit so HEAD exists.
    (work / "README.md").write_text("# Test\n", encoding="utf-8")
    repo.git.add(A=True)
    repo.index.commit("chore: initial commit")

    # Bare remote to push into.
    bare = tmp_path / "remote.git"
    Repo.init(bare, bare=True)
    repo.create_remote("origin", str(bare))

    return RepositoryManager(work)
