"""OpenAI provider implementation."""

from __future__ import annotations

from docsmith.ai.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation."""

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using OpenAI API."""
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError(
                "openai package not installed. Install with: pip install 'docsmith-ai[openai]'"
            )

        client = OpenAI(api_key=self.api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {e}") from e
