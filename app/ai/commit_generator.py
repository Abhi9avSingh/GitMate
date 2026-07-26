"""
commit_generator.py
-------------------

Converts a diff into a single, clean Conventional-Commit message.

The generator:
1. Builds the prompt from a cleaned diff.
2. Calls the configured :class:`AIProvider`.
3. Sanitises the response so only one bare commit line survives.
4. Falls back to a deterministic heuristic message if the AI is unavailable.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from app.ai.prompts import SYSTEM_PROMPT, build_user_prompt
from app.ai.provider import AIProvider, AIProviderError

_CONVENTIONAL_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)"
    r"(\([^)]+\))?!?:\s.+"
)


class CommitMessageGenerator:
    """Generate a commit message from a diff using an AI provider."""

    def __init__(self, provider: Optional[AIProvider] = None) -> None:
        self.provider = provider

    # ------------------------------------------------------------------

    def generate(self, diff: str, changed_files: Optional[List[str]] = None) -> str:
        """Return a single-line commit message for ``diff``.

        If no provider is configured or the AI call fails, a deterministic
        fallback message is produced from the changed files.
        """
        if self.provider and diff.strip():
            try:
                raw = self.provider.complete(SYSTEM_PROMPT, build_user_prompt(diff))
                cleaned = self._sanitise(raw)
                if cleaned:
                    return cleaned
            except AIProviderError:
                pass  # fall through to heuristic

        return self._fallback(changed_files or [])

    # ------------------------------------------------------------------

    @staticmethod
    def _sanitise(raw: str) -> str:
        """Reduce a raw model response to one bare commit line."""
        if not raw:
            return ""
        text = raw.strip()
        # Strip code fences / backticks the model may have added.
        text = text.strip("`").strip()
        # Keep the first non-empty line only.
        first_line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
        # Remove surrounding quotes and any trailing period.
        first_line = first_line.strip('"\'').rstrip(".").strip()
        return first_line

    @staticmethod
    def _fallback(changed_files: List[str]) -> str:
        """Deterministic commit message when the AI is not available."""
        if not changed_files:
            return "chore: update project files"

        exts = {Path(f).suffix.lower() for f in changed_files}
        names = {Path(f).name.lower() for f in changed_files}

        if names & {"readme.md", "changelog.md"} or exts == {".md"}:
            return "docs: update documentation"
        if exts <= {".css", ".scss", ".sass", ".less"} and exts:
            return "style: update styles"
        if exts & {".test.js", ".spec.js"} or any("test" in n for n in names):
            return "test: update tests"
        if exts & {".js", ".jsx", ".ts", ".tsx", ".py"}:
            scope = Path(changed_files[0]).stem
            return f"chore({scope}): update code"
        return "chore: update project files"

    @staticmethod
    def is_conventional(message: str) -> bool:
        """Return True if ``message`` looks like a Conventional Commit."""
        return bool(_CONVENTIONAL_RE.match(message.strip()))
