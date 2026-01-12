"""
Base provider class with common functionality.

Provides shared implementation for building prompts and handling
TTRPG-specific context in AI completions.
"""

from abc import ABC, abstractmethod
from typing import Iterator

from ...util import get_basic_logger
from ..protocol import CompletionRequest, CompletionResponse

logger = get_basic_logger(__name__)


class BaseProvider(ABC):
    """
    Abstract base class for AI providers.

    Provides common functionality for building prompts and handling
    TTRPG-specific context, while requiring subclasses to implement
    the actual API calls.
    """

    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        """
        Initialize the provider.

        Args:
            api_key: API key for authentication
            base_url: Base URL for API calls (optional for some providers)
            model: Model identifier
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        ...

    @property
    @abstractmethod
    def provider_type(self) -> str:
        """Provider type identifier."""
        ...

    @abstractmethod
    def validate_config(self, api_key: str, base_url: str, model: str) -> tuple[bool, str]:
        """Validate the provider configuration."""
        ...

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Return list of available model identifiers."""
        ...

    @abstractmethod
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Perform synchronous text completion."""
        ...

    @abstractmethod
    def complete_streaming(self, request: CompletionRequest) -> Iterator[str]:
        """Perform streaming text completion."""
        ...

    def build_system_prompt(self, request: CompletionRequest) -> str:
        """
        Build the system prompt with TTRPG context.

        Args:
            request: The completion request

        Returns:
            System prompt string
        """
        base_prompt = """You are an AI assistant helping a Game Master create content for a tabletop RPG campaign.

Your role:
- Provide creative, evocative completions that fit fantasy/RPG settings
- Be concise but descriptive - aim for quality over quantity
- Match the tone and style of any existing content
- Consider the context of the entity type being edited

When completing text:
- Continue naturally from where the user left off
- Maintain consistency with any provided entity data
- Use appropriate vocabulary for the field type (e.g., dramatic for backstories, precise for rules)"""

        if request.system_prompt:
            return f"{base_prompt}\n\nAdditional instructions:\n{request.system_prompt}"
        return base_prompt

    def build_user_prompt(self, request: CompletionRequest) -> str:
        """
        Build the user prompt with context information.

        Args:
            request: The completion request

        Returns:
            User prompt string with context
        """
        parts = []
        context = request.context

        # Add field context
        if "field_name" in context:
            parts.append(f"Field: {context['field_name']}")

        if "entity_type" in context:
            parts.append(f"Entity Type: {context['entity_type']}")

        # Add entity data if available
        if "entity_data" in context and context["entity_data"]:
            entity_info = []
            for key, value in context["entity_data"].items():
                if value:  # Only include non-empty values
                    entity_info.append(f"  {key}: {value}")
            if entity_info:
                parts.append("Current Entity Data:\n" + "\n".join(entity_info))

        # Add the actual prompt/text to complete
        if request.prompt:
            if parts:
                parts.append(f"\nText to complete:\n{request.prompt}")
            else:
                parts.append(request.prompt)

        # Add instruction
        parts.append(
            "\nProvide a natural continuation or completion. " "Respond with only the completion text, no explanations."
        )

        return "\n".join(parts)
