"""Google Gemini AI provider."""

from __future__ import annotations

from docsmith.ai.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """Google Gemini provider implementation."""

    @property
    def provider_name(self) -> str:
        return "Google Gemini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using Gemini API."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise RuntimeError(
                "google-generativeai package not installed. "
                "Install with: pip install 'docsmith-ai[gemini]'"
            )

        genai.configure(api_key=self.api_key)

        generation_config = genai.GenerationConfig(
            max_output_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        model = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system_prompt if system_prompt else None,
            generation_config=generation_config,
        )

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {e}") from e
