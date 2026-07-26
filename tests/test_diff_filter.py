"""Tests for DiffFilter."""

from __future__ import annotations

from app.git.diff_filter import DiffFilter


def test_ignores_known_dirs(tmp_path):
    f = DiffFilter(tmp_path)
    assert f.is_ignored("node_modules/react/index.js")
    assert f.is_ignored("dist/bundle.js")
    assert f.is_ignored(".venv/lib/site.py")


def test_ignores_binary_extensions(tmp_path):
    f = DiffFilter(tmp_path)
    assert f.is_ignored("assets/logo.png")
    assert f.is_ignored("app.exe")


def test_keeps_source_files(tmp_path):
    f = DiffFilter(tmp_path)
    assert not f.is_ignored("src/app.py")
    assert not f.is_ignored("components/Card.tsx")


def test_filter_list(tmp_path):
    f = DiffFilter(tmp_path)
    files = ["src/app.py", "node_modules/x.js", "logo.png", "README.md"]
    assert f.filter(files) == ["src/app.py", "README.md"]
