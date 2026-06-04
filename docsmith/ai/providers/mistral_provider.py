"""Mistral AI provider implementation."""

from __future__ import annotations

from docsmith.ai.providers.base import BaseProvider


class MistralProvider(BaseProvider):
    """Mistral AI provider implementation."""

    @property
    def provider_name(self) -> str:
        return "Mistral AI"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using Mistral API."""
        try:
            from mistralai import Mistral
        except ImportError:
            raise RuntimeError(
                "mistralai package not installed. Install with: pip install 'docsmith-ai[mistral]'"
            )

        client = Mistral(api_key=self.api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.complete(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"Mistral generation failed: {e}") from e
