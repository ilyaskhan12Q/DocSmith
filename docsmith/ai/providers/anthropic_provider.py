"""Anthropic Claude provider implementation."""

from __future__ import annotations

from docsmith.ai.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider implementation."""

    @property
    def provider_name(self) -> str:
        return "Anthropic"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using Anthropic API."""
        try:
            import anthropic
        except ImportError:
            raise RuntimeError(
                "anthropic package not installed. "
                "Install with: pip install 'docsmith-ai[anthropic]'"
            )

        client = anthropic.Anthropic(api_key=self.api_key)

        try:
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic generation failed: {e}") from e
