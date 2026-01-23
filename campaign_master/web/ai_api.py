"""
AI API endpoints for web frontend.

Provides endpoints for AI text completion, connection testing,
and provider/model information.
"""

import os
from typing import Any

import fastapi
from fastapi import HTTPException
from pydantic import BaseModel

from ..ai.protocol import CompletionRequest, CompletionResponse
from ..ai.providers import PROVIDER_REGISTRY, get_available_provider_types, get_provider
from ..util import get_basic_logger

logger = get_basic_logger(__name__)

router = fastapi.APIRouter()


class CompletionRequestModel(BaseModel):
    """Request model for AI text completion."""

    prompt: str
    context: dict[str, Any] = {}
    max_tokens: int = 500
    temperature: float = 0.7
    system_prompt: str = ""
    # Agent config to use (optional - uses these settings directly)
    provider_type: str = ""
    api_key: str = ""
    base_url: str = ""
    model: str = ""


class CompletionResponseModel(BaseModel):
    """Response model for AI text completion."""

    text: str
    finish_reason: str
    usage: dict[str, int] | None = None
    error_message: str = ""


class TestConnectionRequest(BaseModel):
    """Request model for testing AI provider connection."""

    provider_type: str
    api_key: str
    base_url: str = ""
    model: str


class TestConnectionResponse(BaseModel):
    """Response model for connection test."""

    success: bool
    message: str


class ProviderInfo(BaseModel):
    """Information about an AI provider."""

    name: str
    type: str


class ModelInfo(BaseModel):
    """Information about a model."""

    id: str
    name: str


@router.post("/ai/complete", response_model=CompletionResponseModel)
def complete_text(request: CompletionRequestModel):
    """
    Request AI text completion.

    Requires provider_type, api_key, and model to be specified.
    """
    try:
        if not request.provider_type or not request.model:
            raise HTTPException(status_code=400, detail="provider_type and model are required")

        # Resolve API key if it's an environment variable reference
        api_key = request.api_key
        if api_key.startswith("$"):
            env_var = api_key[1:]
            api_key = os.environ.get(env_var, "")
            if not api_key:
                raise HTTPException(status_code=400, detail=f"Environment variable {env_var} not set")

        # Get the provider
        provider = get_provider(
            provider_type=request.provider_type,
            api_key=api_key,
            base_url=request.base_url,
            model=request.model,
        )

        # Create completion request
        completion_request = CompletionRequest(
            prompt=request.prompt,
            context=request.context,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system_prompt=request.system_prompt,
        )

        # Execute completion
        response = provider.complete(completion_request)

        return CompletionResponseModel(
            text=response.text,
            finish_reason=response.finish_reason,
            usage=response.usage,
            error_message=response.error_message,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Completion error: %s", e)
        return CompletionResponseModel(
            text="",
            finish_reason="error",
            error_message=str(e),
        )


@router.post("/ai/test", response_model=TestConnectionResponse)
def test_connection(request: TestConnectionRequest):
    """
    Test connection to an AI provider.

    Validates configuration and attempts a simple completion.
    """
    try:
        # Resolve API key if it's an environment variable reference
        api_key = request.api_key
        if api_key.startswith("$"):
            env_var = api_key[1:]
            api_key = os.environ.get(env_var, "")
            if not api_key:
                return TestConnectionResponse(success=False, message=f"Environment variable {env_var} not set")

        # Get the provider
        provider = get_provider(
            provider_type=request.provider_type,
            api_key=api_key,
            base_url=request.base_url,
            model=request.model,
        )

        # Validate config
        is_valid, error = provider.validate_config(api_key, request.base_url, request.model)
        if not is_valid:
            return TestConnectionResponse(success=False, message=error)

        # Try a simple completion
        test_request = CompletionRequest(
            prompt="Hello",
            context={},
            max_tokens=10,
            temperature=0.0,
        )
        response = provider.complete(test_request)

        if response.finish_reason == "error":
            return TestConnectionResponse(success=False, message=response.error_message or "Unknown error")

        return TestConnectionResponse(success=True, message=f"Connection successful! Response: {response.text[:50]}...")

    except ValueError as e:
        return TestConnectionResponse(success=False, message=str(e))
    except Exception as e:
        logger.error("Connection test error: %s", e)
        return TestConnectionResponse(success=False, message=str(e))


@router.get("/ai/providers", response_model=list[ProviderInfo])
def list_providers():
    """List available AI providers."""
    providers = []
    for provider_type in get_available_provider_types():
        provider_class = PROVIDER_REGISTRY[provider_type]
        # Create a temporary instance to get the name
        try:
            temp_provider = provider_class(api_key="", base_url="", model="")
            name = temp_provider.name
        except Exception:
            name = provider_type.capitalize()

        providers.append(ProviderInfo(name=name, type=provider_type))

    return providers


@router.get("/ai/models/{provider_type}", response_model=list[ModelInfo])
def list_models(provider_type: str):
    """List available models for a provider."""
    try:
        provider_class = PROVIDER_REGISTRY.get(provider_type)
        if not provider_class:
            raise HTTPException(status_code=404, detail=f"Unknown provider: {provider_type}")

        # Create a temporary instance to get models
        temp_provider = provider_class(api_key="", base_url="", model="")
        models = temp_provider.get_available_models()

        return [ModelInfo(id=m, name=m) for m in models]

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error listing models: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
