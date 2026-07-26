"""Tests for the AI provider factory (no network)."""

from __future__ import annotations

import pytest

from app.ai.provider import (
    AIProviderError,
    GeminiProvider,
    OpenAIProvider,
    build_provider,
)


def test_build_gemini_default_model():
    provider = build_provider("gemini", api_key="x")
    assert isinstance(provider, GeminiProvider)
    assert provider.model == "gemini-1.5-flash"


def test_build_openai():
    provider = build_provider("openai", api_key="x", model="gpt-4o-mini")
    assert isinstance(provider, OpenAIProvider)


def test_unknown_provider_raises():
    with pytest.raises(AIProviderError):
        build_provider("llama", api_key="x")


def test_gemini_requires_key():
    with pytest.raises(AIProviderError):
        GeminiProvider(api_key="")
