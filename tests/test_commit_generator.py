"""Tests for the AI commit-message generator (no network)."""

from __future__ import annotations

from app.ai.commit_generator import CommitMessageGenerator
from app.ai.provider import AIProvider


class FakeProvider(AIProvider):
    name = "fake"

    def __init__(self, reply):
        self.reply = reply

    def complete(self, system_prompt, user_prompt):
        return self.reply


def test_sanitises_markdown_and_quotes():
    gen = CommitMessageGenerator(FakeProvider('```\n"feat(auth): add login."\n```'))
    assert gen.generate("diff") == "feat(auth): add login"


def test_fallback_docs():
    gen = CommitMessageGenerator(None)
    assert gen.generate("", ["README.md"]) == "docs: update documentation"


def test_fallback_style():
    gen = CommitMessageGenerator(None)
    assert gen.generate("", ["home.css"]) == "style: update styles"


def test_is_conventional():
    assert CommitMessageGenerator.is_conventional("feat(x): do thing")
    assert not CommitMessageGenerator.is_conventional("did a thing")
