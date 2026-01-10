"""
Anthropic Claude provider implementation.
"""

from typing import Iterator

from ..protocol import CompletionRequest, CompletionResponse
from .base import BaseProvider, logger


class AnthropicProvider(BaseProvider):
    """AI provider using Anthropic's Claude models."""

    # Default models available from Anthropic
    DEFAULT_MODELS = [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
    ]

    @property
    def name(self) -> str:
        return "Anthropic Claude"

    @property
    def provider_type(self) -> str:
        return "anthropic"

    def validate_config(
        self, api_key: str, base_url: str, model: str
    ) -> tuple[bool, str]:
        """Validate Anthropic configuration."""
        if not api_key:
            return False, "API key is required for Anthropic"

        if not api_key.startswith("sk-ant-"):
            return False, "Invalid API key format. Anthropic keys start with 'sk-ant-'"

        if not model:
            return False, "Model selection is required"

        return True, ""

    def get_available_models(self) -> list[str]:
        """Return list of available Claude models."""
        return self.DEFAULT_MODELS.copy()

    def _get_client(self):
        """Get or create Anthropic client."""
        try:
            import anthropic

            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            return anthropic.Anthropic(**kwargs)
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Run: pip install anthropic"
            )

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Perform completion using Anthropic API."""
        try:
            client = self._get_client()

            system_prompt = self.build_system_prompt(request)
            user_prompt = self.build_user_prompt(request)

            logger.debug(
                "Anthropic request: model=%s, max_tokens=%d",
                self.model,
                request.max_tokens,
            )

            response = client.messages.create(
                model=self.model,
                max_tokens=request.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            # Extract text from response
            text = ""
            if response.content:
                text = response.content[0].text

            # Map stop reason
            finish_reason = "stop"
            if response.stop_reason == "max_tokens":
                finish_reason = "length"
            elif response.stop_reason == "error":
                finish_reason = "error"

            return CompletionResponse(
                text=text,
                finish_reason=finish_reason,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            )

        except Exception as e:
            logger.error("Anthropic completion error: %s", e)
            return CompletionResponse(
                text="",
                finish_reason="error",
                error_message=str(e),
            )

    def complete_streaming(self, request: CompletionRequest) -> Iterator[str]:
        """Perform streaming completion using Anthropic API."""
        try:
            client = self._get_client()

            system_prompt = self.build_system_prompt(request)
            user_prompt = self.build_user_prompt(request)

            with client.messages.stream(
                model=self.model,
                max_tokens=request.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error("Anthropic streaming error: %s", e)
            yield f"[Error: {e}]"
