"""
provider.py
-----------

AI provider abstraction.

``AIProvider`` defines the minimal interface GitMate needs: given a system
prompt and a user prompt, return a plain-text completion.

Two backends ship with GitMate:

- :class:`GeminiProvider` (default) - Google Gemini. Uses the official
  ``google-generativeai`` SDK when installed, and transparently falls back to
  a raw REST call via ``requests``.
- :class:`OpenAIProvider` - OpenAI chat completions (kept for those who want
  it), with the same SDK-or-REST fallback.
"""

from __future__ import annotations

import abc
from typing import Optional


class AIProviderError(Exception):
    """Raised when the AI provider cannot produce a completion."""


class AIProvider(abc.ABC):
    """Minimal interface every AI backend must implement."""

    name: str = "base"

    @abc.abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Return the model's plain-text completion."""
        raise NotImplementedError


class GeminiProvider(AIProvider):
    """Google Gemini backed provider.

    Get a free API key at https://aistudio.google.com/app/apikey
    """

    name = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-flash",
        temperature: float = 0.2,
        max_tokens: int = 60,
        timeout: int = 30,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
    ) -> None:
        if not api_key:
            raise AIProviderError("A Gemini API key is required.")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        try:
            return self._complete_with_sdk(system_prompt, user_prompt)
        except ImportError:
            return self._complete_with_rest(system_prompt, user_prompt)

    # ------------------------------------------------------------------

    def _complete_with_sdk(self, system_prompt: str, user_prompt: str) -> str:
        import google.generativeai as genai  # imported lazily; may be absent

        genai.configure(api_key=self.api_key)
        try:
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                },
            )
            response = model.generate_content(
                user_prompt,
                request_options={"timeout": self.timeout},
            )
        except Exception as exc:  # network / auth / rate-limit
            raise AIProviderError(f"Gemini request failed: {exc}") from exc

        text = getattr(response, "text", None)
        if not text:
            raise AIProviderError("Gemini returned an empty completion.")
        return text

    def _complete_with_rest(self, system_prompt: str, user_prompt: str) -> str:
        import requests  # part of the minimal dependency set

        url = f"{self.base_url}/models/{self.model}:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens,
            },
        }
        try:
            resp = requests.post(
                url, headers=headers, params=params, json=payload, timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            raise AIProviderError(f"Gemini request failed: {exc}") from exc

        try:
            content = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise AIProviderError("Unexpected Gemini response shape.") from exc

        if not content:
            raise AIProviderError("Gemini returned an empty completion.")
        return content


class OpenAIProvider(AIProvider):
    """OpenAI chat-completions backed provider."""

    name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,
        max_tokens: int = 60,
        timeout: int = 30,
        base_url: str = "https://api.openai.com/v1",
    ) -> None:
        if not api_key:
            raise AIProviderError("An OpenAI API key is required.")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        try:
            return self._complete_with_sdk(messages)
        except ImportError:
            return self._complete_with_rest(messages)

    # ------------------------------------------------------------------

    def _complete_with_sdk(self, messages: list[dict]) -> str:
        from openai import OpenAI  # imported lazily; may be absent

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )
        except Exception as exc:  # network / auth / rate-limit
            raise AIProviderError(f"OpenAI request failed: {exc}") from exc

        content = response.choices[0].message.content
        if not content:
            raise AIProviderError("OpenAI returned an empty completion.")
        return content

    def _complete_with_rest(self, messages: list[dict]) -> str:
        import requests  # part of the minimal dependency set

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        try:
            resp = requests.post(
                url, headers=headers, json=payload, timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            raise AIProviderError(f"OpenAI request failed: {exc}") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise AIProviderError("Unexpected OpenAI response shape.") from exc

        if not content:
            raise AIProviderError("OpenAI returned an empty completion.")
        return content


# Default model per provider, used when the caller does not specify one.
_DEFAULT_MODELS = {
    "gemini": "gemini-1.5-flash",
    "openai": "gpt-4o-mini",
}


def build_provider(
    provider: str,
    api_key: str,
    model: Optional[str] = None,
    **kwargs,
) -> AIProvider:
    """Factory that returns a configured :class:`AIProvider`."""
    provider = (provider or "gemini").lower()
    model = model or _DEFAULT_MODELS.get(provider)

    if provider == "gemini":
        return GeminiProvider(api_key=api_key, model=model, **kwargs)
    if provider == "openai":
        return OpenAIProvider(api_key=api_key, model=model, **kwargs)
    raise AIProviderError(f"Unknown AI provider: {provider!r}")
