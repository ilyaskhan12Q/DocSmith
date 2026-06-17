"""AI orchestrator — manages provider selection and prompt execution."""

from __future__ import annotations

from rich.console import Console

from docsmith.ai.providers.base import BaseProvider
from docsmith.config.settings import AIProvider, DocSmithConfig

console = Console()


def get_provider(config: DocSmithConfig) -> BaseProvider:
    """Create and return the configured AI provider.

    Args:
        config: DocSmith configuration.

    Returns:
        Initialized provider instance.

    Raises:
        ValueError: If the provider is not configured or unknown.
    """
    provider_config = config.get_provider_config()
    api_key = provider_config.api_key
    model = config.get_model()

    if not api_key:
        raise ValueError(
            f"No API key configured for {config.active_provider.value}. "
            "Run `docsmith config` to set up your provider."
        )

    match config.active_provider:
        case AIProvider.GEMINI:
            from docsmith.ai.providers.gemini import GeminiProvider

            return GeminiProvider(
                api_key=api_key,
                model=model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
        case AIProvider.OPENAI:
            from docsmith.ai.providers.openai_provider import OpenAIProvider

            return OpenAIProvider(
                api_key=api_key,
                model=model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
        case AIProvider.ANTHROPIC:
            from docsmith.ai.providers.anthropic_provider import AnthropicProvider

            return AnthropicProvider(
                api_key=api_key,
                model=model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
        case AIProvider.MISTRAL:
            from docsmith.ai.providers.mistral_provider import MistralProvider

            return MistralProvider(
                api_key=api_key,
                model=model,
                max_tokens=provider_config.max_tokens,
                temperature=provider_config.temperature,
            )
        case _:
            raise ValueError(f"Unknown provider: {config.active_provider}")


def generate_with_retry(
    provider: BaseProvider,
    prompt: str,
    system_prompt: str = "",
    max_retries: int = 2,
) -> str:
    """Generate text with retry logic.

    Args:
        provider: The AI provider to use.
        prompt: User prompt.
        system_prompt: System prompt.
        max_retries: Maximum retry attempts.

    Returns:
        Generated text.

    Raises:
        RuntimeError: If all retries fail.
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return provider.generate(prompt, system_prompt)
        except RuntimeError as e:
            last_error = e
            if attempt < max_retries:
                console.print(
                    f"[yellow] Generation attempt {attempt + 1} failed, retrying...[/yellow]"
                )

    raise RuntimeError(f"Generation failed after {max_retries + 1} attempts: {last_error}")
