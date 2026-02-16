"""
Base provider class with common functionality.

Provides shared implementation for building prompts and handling
TTRPG-specific context in AI completions.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Iterator

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

You will receive a structured JSON context with two sections:
- "campaign": The full campaign data including all entities (characters, locations, items, etc.)
- "entity": The specific entity and field you need to complete

Your role:
- Provide creative, evocative completions that fit fantasy/RPG settings
- Be concise but descriptive - aim for quality over quantity
- Match the tone and style of any existing content
- Use the campaign context to maintain consistency with existing characters, locations, and story elements
- Reference existing campaign entities when appropriate

Respond with ONLY the completion text for the specified field. No explanations, no prefixes, no formatting."""

        if request.system_prompt:
            return f"{base_prompt}\n\nAdditional instructions:\n{request.system_prompt}"
        return base_prompt

    def _format_campaign_summary(self, campaign: dict[str, Any]) -> str:
        """Build a human-readable campaign summary from the campaign context dict."""
        parts = []

        if campaign.get("title"):
            parts.append(f"Campaign: {campaign['title']}")
        if campaign.get("version"):
            parts.append(f"Version: {campaign['version']}")
        if campaign.get("setting"):
            parts.append(f"Setting: {campaign['setting']}")
        if campaign.get("summary"):
            parts.append(f"Summary: {campaign['summary']}")

        for key, label in [
            ("characters", "Characters"),
            ("locations", "Locations"),
            ("storypoints", "Story Points"),
            ("storyline", "Story Arcs"),
            ("items", "Items"),
            ("rules", "Rules"),
            ("objectives", "Objectives"),
        ]:
            items = campaign.get(key)
            if items:
                names = [
                    i.get("name") or i.get("description", "") for i in items if i.get("name") or i.get("description")
                ]
                if names:
                    parts.append(f"{label}: {', '.join(names)}")

        return "\n".join(parts)

    def build_user_prompt(self, request: CompletionRequest) -> str:
        """
        Build the user prompt with structured campaign and entity context.

        Expects request.context to have the structure:
        {
            "campaign": { ... full campaign data ... },
            "entity": { "obj_id": ..., "field": "...", "current_value": "..." }
        }

        Args:
            request: The completion request

        Returns:
            User prompt string with context
        """
        context = request.context
        campaign = context.get("campaign", {})
        entity = context.get("entity", {})

        parts = []

        # Include full campaign context as JSON
        if campaign:
            parts.append(f"Campaign context:\n{json.dumps(campaign, indent=2, default=str)}")

        # Entity completion instruction
        field = entity.get("field", "unknown")
        obj_id = entity.get("obj_id", "unknown")
        current_value = entity.get("current_value", "")

        parts.append(f"Complete the '{field}' field for entity {obj_id}.")

        if current_value:
            parts.append(f"Current value: {current_value}")

        parts.append(
            "Provide a natural continuation or completion. " "Respond with only the completion text, no explanations."
        )

        return "\n\n".join(parts)
