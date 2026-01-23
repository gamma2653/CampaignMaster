"""
Protocol definitions for AI completion providers.

Defines the interface that all AI providers must implement, along with
request/response dataclasses for completion operations.
"""

from dataclasses import dataclass, field
from typing import Any, Iterator, Protocol, runtime_checkable


@dataclass
class CompletionRequest:
    """Request for AI text completion."""

    prompt: str
    """The text to complete or the prompt to respond to."""

    context: dict[str, Any] = field(default_factory=dict)
    """
    Contextual information about the completion request.
    May include: field_name, entity_type, current_text, entity_data, campaign_context.

    campaign_context contains the full campaign data including:
    - title, setting, summary: Campaign metadata
    - characters: List of character objects with name, role, backstory, etc.
    - locations: List of location objects with name, description, etc.
    - storypoints: List of story point objects
    - storyline: List of arc objects
    - items: List of item objects
    - rules: List of rule objects
    - objectives: List of objective objects
    """

    max_tokens: int = 500
    """Maximum tokens to generate in the response."""

    temperature: float = 0.7
    """Sampling temperature (0.0 = deterministic, 1.0+ = creative)."""

    system_prompt: str = ""
    """Optional custom system prompt override."""


@dataclass
class CompletionResponse:
    """Response from AI text completion."""

    text: str
    """The generated completion text."""

    finish_reason: str
    """Why generation stopped: 'stop', 'length', or 'error'."""

    usage: dict[str, int] | None = None
    """Token usage statistics: input_tokens, output_tokens."""

    error_message: str = ""
    """Error message if finish_reason is 'error'."""


@runtime_checkable
class AIProvider(Protocol):
    """Protocol defining the interface for AI completion providers."""

    @property
    def name(self) -> str:
        """Human-readable provider name."""
        ...

    @property
    def provider_type(self) -> str:
        """Provider type identifier (anthropic, openai, ollama)."""
        ...

    def validate_config(self, api_key: str, base_url: str, model: str) -> tuple[bool, str]:
        """
        Validate the provider configuration.

        Args:
            api_key: API key for authentication
            base_url: Base URL for API calls
            model: Model identifier

        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is empty.
        """
        ...

    def get_available_models(self) -> list[str]:
        """Return list of available model identifiers for this provider."""
        ...

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """
        Perform synchronous text completion.

        Args:
            request: The completion request with prompt and context

        Returns:
            CompletionResponse with generated text
        """
        ...

    def complete_streaming(self, request: CompletionRequest) -> Iterator[str]:
        """
        Perform streaming text completion.

        Args:
            request: The completion request with prompt and context

        Yields:
            Text chunks as they are generated
        """
        ...
