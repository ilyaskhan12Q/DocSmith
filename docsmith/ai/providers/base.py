"""Base provider interface for all AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract base class for AI providers.

    All providers must implement the `generate` method.
    """

    def __init__(self, api_key: str, model: str, max_tokens: int = 4096, temperature: float = 0.3):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text from a prompt.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system/instruction prompt.

        Returns:
            Generated text response.

        Raises:
            RuntimeError: If generation fails.
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name."""
        ...
