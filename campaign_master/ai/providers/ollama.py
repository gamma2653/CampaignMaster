"""
Ollama local provider implementation.
"""

from typing import Iterator

from ..protocol import CompletionRequest, CompletionResponse
from .base import BaseProvider, logger


class OllamaProvider(BaseProvider):
    """AI provider using Ollama for local model inference."""

    DEFAULT_BASE_URL = "http://localhost:11434"

    # Common models that are often available in Ollama
    COMMON_MODELS = [
        "llama3.1",
        "llama3.1:70b",
        "llama3.2",
        "mistral",
        "mixtral",
        "codellama",
        "phi3",
        "qwen2.5",
    ]

    @property
    def name(self) -> str:
        return "Ollama (Local)"

    @property
    def provider_type(self) -> str:
        return "ollama"

    def _get_base_url(self) -> str:
        """Get the base URL, using default if not set."""
        return self.base_url or self.DEFAULT_BASE_URL

    def validate_config(self, api_key: str, base_url: str, model: str) -> tuple[bool, str]:
        """Validate Ollama configuration."""
        # Ollama doesn't require an API key
        if not model:
            return False, "Model selection is required"

        # Try to connect to Ollama
        try:
            import httpx

            url = base_url or self.DEFAULT_BASE_URL
            response = httpx.get(f"{url}/api/tags", timeout=5.0)
            if response.status_code != 200:
                return False, f"Could not connect to Ollama at {url}"
        except ImportError:
            return False, "httpx package not installed. Run: pip install httpx"
        except Exception as e:
            return False, f"Could not connect to Ollama: {e}"

        return True, ""

    def get_available_models(self) -> list[str]:
        """
        Return list of available models from Ollama.

        Queries the local Ollama instance for installed models.
        Falls back to common models list if connection fails.
        """
        try:
            import httpx

            url = self._get_base_url()
            response = httpx.get(f"{url}/api/tags", timeout=5.0)

            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                if models:
                    return models

        except Exception as e:
            logger.warning("Could not fetch Ollama models: %s", e)

        # Fall back to common models
        return self.COMMON_MODELS.copy()

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Perform completion using Ollama API."""
        try:
            import httpx

            url = self._get_base_url()

            system_prompt = self.build_system_prompt(request)
            user_prompt = self.build_user_prompt(request)

            logger.debug(
                "Ollama request: url=%s, model=%s",
                url,
                self.model,
            )

            # Ollama uses the /api/chat endpoint for chat completions
            response = httpx.post(
                f"{url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "stream": False,
                    "options": {
                        "num_predict": request.max_tokens,
                        "temperature": request.temperature,
                    },
                },
                timeout=120.0,  # Longer timeout for local models
            )

            if response.status_code != 200:
                return CompletionResponse(
                    text="",
                    finish_reason="error",
                    error_message=f"Ollama returned status {response.status_code}",
                )

            data = response.json()
            text = data.get("message", {}).get("content", "")

            # Ollama indicates completion with done=true
            finish_reason = "stop" if data.get("done", False) else "length"

            # Get token counts if available
            usage = None
            if "eval_count" in data:
                usage = {
                    "input_tokens": data.get("prompt_eval_count", 0),
                    "output_tokens": data.get("eval_count", 0),
                }

            return CompletionResponse(
                text=text,
                finish_reason=finish_reason,
                usage=usage,
            )

        except ImportError:
            return CompletionResponse(
                text="",
                finish_reason="error",
                error_message="httpx package not installed. Run: pip install httpx",
            )
        except Exception as e:
            logger.error("Ollama completion error: %s", e)
            return CompletionResponse(
                text="",
                finish_reason="error",
                error_message=str(e),
            )

    def complete_streaming(self, request: CompletionRequest) -> Iterator[str]:
        """Perform streaming completion using Ollama API."""
        try:
            import httpx

            url = self._get_base_url()

            system_prompt = self.build_system_prompt(request)
            user_prompt = self.build_user_prompt(request)

            with httpx.stream(
                "POST",
                f"{url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "stream": True,
                    "options": {
                        "num_predict": request.max_tokens,
                        "temperature": request.temperature,
                    },
                },
                timeout=120.0,
            ) as response:
                import json

                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if data.get("done", False):
                            break

        except Exception as e:
            logger.error("Ollama streaming error: %s", e)
            yield f"[Error: {e}]"
