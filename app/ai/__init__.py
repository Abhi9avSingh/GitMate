"""GitMate AI layer.

Turns a Git diff into a single Conventional-Commit message. The provider
abstraction keeps GitMate independent of any specific vendor so new backends
(Gemini, OpenAI, local models, etc.) can be added without touching the rest of
the app.
"""

from __future__ import annotations

from app.ai.commit_generator import CommitMessageGenerator
from app.ai.provider import (
    AIProvider,
    AIProviderError,
    GeminiProvider,
    OpenAIProvider,
    build_provider,
)

__all__ = [
    "AIProvider",
    "AIProviderError",
    "GeminiProvider",
    "OpenAIProvider",
    "build_provider",
    "CommitMessageGenerator",
]
