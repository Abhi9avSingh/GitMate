"""Tests for RepositoryManager."""

from __future__ import annotations

import pytest

from app.git.repository import (
    InvalidRepositoryError,
    RepositoryManager,
    RepositoryNotFoundError,
)


def test_missing_path_raises(tmp_path):
    with pytest.raises(RepositoryNotFoundError):
        RepositoryManager(tmp_path / "does-not-exist")


def test_non_repo_raises(tmp_path):
    (tmp_path / "plain").mkdir()
    with pytest.raises(InvalidRepositoryError):
        RepositoryManager(tmp_path / "plain")


def test_clean_repo_has_no_changes(temp_repo):
    assert not temp_repo.has_changes()
    assert temp_repo.changed_files() == []


def test_detects_new_file(temp_repo):
    (temp_repo.repo_path / "new.py").write_text("print('hi')\n", encoding="utf-8")
    assert temp_repo.has_changes()
    assert "new.py" in temp_repo.changed_files()


def test_info_and_remote(temp_repo):
    info = temp_repo.info()
    assert info["name"] == temp_repo.name
    assert temp_repo.has_remote()
    assert temp_repo.remote_name == "origin"
