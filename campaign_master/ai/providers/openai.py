"""
OpenAI provider implementation.
"""

from typing import Iterator

from ..protocol import CompletionRequest, CompletionResponse
from .base import BaseProvider, logger


class OpenAIProvider(BaseProvider):
    """AI provider using OpenAI's GPT models."""

    # Default models available from OpenAI
    DEFAULT_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ]

    @property
    def name(self) -> str:
        return "OpenAI"

    @property
    def provider_type(self) -> str:
        return "openai"

    def validate_config(self, api_key: str, base_url: str, model: str) -> tuple[bool, str]:
        """Validate OpenAI configuration."""
        if not api_key:
            return False, "API key is required for OpenAI"

        if not api_key.startswith("sk-"):
            return False, "Invalid API key format. OpenAI keys start with 'sk-'"

        if not model:
            return False, "Model selection is required"

        return True, ""

    def get_available_models(self) -> list[str]:
        """Return list of available GPT models."""
        return self.DEFAULT_MODELS.copy()

    def _get_client(self):
        """Get or create OpenAI client."""
        try:
            import openai

            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            return openai.OpenAI(**kwargs)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Perform completion using OpenAI API."""
        try:
            client = self._get_client()

            system_prompt = self.build_system_prompt(request)
            user_prompt = self.build_user_prompt(request)

            logger.debug(
                "OpenAI request: model=%s, max_tokens=%d",
                self.model,
                request.max_tokens,
            )

            response = client.chat.completions.create(
                model=self.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

            # Extract text from response
            text = ""
            if response.choices:
                text = response.choices[0].message.content or ""

            # Map finish reason
            finish_reason = "stop"
            if response.choices and response.choices[0].finish_reason == "length":
                finish_reason = "length"

            usage = None
            if response.usage:
                usage = {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                }

            return CompletionResponse(
                text=text,
                finish_reason=finish_reason,
                usage=usage,
            )

        except Exception as e:
            logger.error("OpenAI completion error: %s", e)
            return CompletionResponse(
                text="",
                finish_reason="error",
                error_message=str(e),
            )

    def complete_streaming(self, request: CompletionRequest) -> Iterator[str]:
        """Perform streaming completion using OpenAI API."""
        try:
            client = self._get_client()

            system_prompt = self.build_system_prompt(request)
            user_prompt = self.build_user_prompt(request)

            stream = client.chat.completions.create(
                model=self.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error("OpenAI streaming error: %s", e)
            yield f"[Error: {e}]"
