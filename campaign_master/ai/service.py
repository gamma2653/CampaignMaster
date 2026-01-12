"""
AI Completion Service - orchestrates AI text completion requests.

Provides a singleton service that manages agent configuration loading,
provider instantiation, and completion request routing.
"""

import os
from threading import Lock
from typing import Any, Callable, Iterator, cast

from PySide6.QtCore import QObject, Qt, QThread, Signal

from ..content import api as content_api
from ..content import planning
from ..util import get_basic_logger
from .protocol import CompletionRequest, CompletionResponse
from .providers import get_provider
from .providers.base import BaseProvider

logger = get_basic_logger(__name__)


class CompletionWorker(QObject):
    """Worker for performing AI completions in a background thread."""

    finished = Signal(object)

    def __init__(self, service: "AICompletionService", prompt: str, context: dict):
        super().__init__()
        self._service = service
        self._prompt = prompt
        self._context = context

    def run(self):
        """Execute the completion request."""
        try:
            result = self._service.complete(self._prompt, self._context)
            self.finished.emit(result)
        except Exception as e:
            logger.error("Worker thread error: %s", e)
            self.finished.emit(
                CompletionResponse(
                    text="",
                    finish_reason="error",
                    error_message=str(e),
                )
            )


class AICompletionService:
    """
    Singleton service for managing AI text completions.

    Handles loading agent configurations from the database,
    instantiating providers, and routing completion requests.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._enabled = True
        self._default_agent: planning.AgentConfig | None = None
        self._provider: BaseProvider | None = None
        self._proto_user_id = 0  # GUI uses global scope
        self._active_workers: list = []  # Keep references to prevent GC

    @classmethod
    def instance(cls) -> "AICompletionService":
        """Get the singleton instance."""
        return cls()

    def is_enabled(self) -> bool:
        """Check if AI completions are enabled."""
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable AI completions."""
        self._enabled = enabled
        logger.info("AI completions %s", "enabled" if enabled else "disabled")

    def get_default_agent(self) -> planning.AgentConfig | None:
        """Get the current default agent configuration."""
        return self._default_agent

    def load_default_agent(self) -> planning.AgentConfig | None:
        """
        Load the default agent configuration from the database.

        Returns the default agent if found, or the first enabled agent,
        or None if no agents are configured.
        """
        try:
            # Get all agent configs
            agents = content_api.retrieve_objects(
                planning.AgentConfig,
                proto_user_id=self._proto_user_id,
            )
            agents = cast(list[planning.AgentConfig], agents)

            if not agents:
                logger.debug("No agent configurations found in database")
                self._default_agent = None
                self._provider = None
                return None

            # Find the default agent, or use the first enabled one
            default_agent = None
            for agent in agents:
                if agent.is_default and agent.is_enabled:
                    default_agent = agent
                    break
                elif agent.is_enabled and default_agent is None:
                    default_agent = agent

            if default_agent:
                self._set_active_agent(default_agent)
            else:
                logger.warning("No enabled agents found")
                self._default_agent = None
                self._provider = None

            return self._default_agent

        except Exception as e:
            logger.error("Error loading default agent: %s", e)
            return None

    def _set_active_agent(self, agent: planning.AgentConfig) -> None:
        """Set the active agent and instantiate its provider."""
        self._default_agent = agent

        # Resolve API key if it's an environment variable reference
        api_key = agent.api_key
        if api_key.startswith("$"):
            env_var = api_key[1:]
            api_key = os.environ.get(env_var, "")
            if not api_key:
                logger.warning(
                    "Environment variable %s not set for agent %s",
                    env_var,
                    agent.name,
                )

        try:
            self._provider = get_provider(
                provider_type=agent.provider_type,
                api_key=api_key,
                base_url=agent.base_url,
                model=agent.model,
            )
            logger.info(
                "Loaded agent '%s' with provider %s",
                agent.name,
                agent.provider_type,
            )
        except ValueError as e:
            logger.error("Failed to create provider for agent %s: %s", agent.name, e)
            self._provider = None

    def set_default_agent_by_id(self, agent_id: str) -> bool:
        """
        Set a specific agent as the default by ID.

        Args:
            agent_id: The object ID of the agent to set as default

        Returns:
            True if successful, False otherwise
        """
        try:
            agent = content_api.retrieve_object(
                planning.ID.from_str(agent_id),
                proto_user_id=self._proto_user_id,
            )
            agent = cast(planning.AgentConfig | None, agent)
            if agent and agent.is_enabled:
                self._set_active_agent(agent)
                return True
            return False
        except Exception as e:
            logger.error("Error setting default agent: %s", e)
            return False

    def get_all_agents(self) -> list[planning.AgentConfig]:
        """Get all configured agents."""
        try:
            return cast(
                list[planning.AgentConfig],
                content_api.retrieve_objects(
                    planning.AgentConfig,
                    proto_user_id=self._proto_user_id,
                ),
            )
        except Exception as e:
            logger.error("Error retrieving agents: %s", e)
            return []

    def complete(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> CompletionResponse | None:
        """
        Perform a synchronous text completion.

        Args:
            prompt: The text to complete
            context: Optional context dictionary (field_name, entity_type, etc.)
            max_tokens: Override max tokens from agent config
            temperature: Override temperature from agent config

        Returns:
            CompletionResponse if successful, None if disabled or no agent
        """
        if not self._enabled:
            logger.debug("AI completions disabled")
            return None

        if not self._provider or not self._default_agent:
            # Try to load default agent
            if not self.load_default_agent():
                logger.warning("No AI agent configured for completion")
                return None
        default_agent = cast(planning.AgentConfig, self._default_agent)
        provider = cast(BaseProvider, self._provider)

        request = CompletionRequest(
            prompt=prompt,
            context=context or {},
            max_tokens=max_tokens or default_agent.max_tokens,
            temperature=temperature or default_agent.temperature,
            system_prompt=default_agent.system_prompt,
        )
        logger.debug("Sending completion request to provider %s", default_agent.provider_type)
        try:
            response = provider.complete(request)
            logger.debug("Received completion response: %s", response.text[:50])
            return response
        except Exception as e:
            logger.error("Completion error: %s", e)
            return CompletionResponse(
                text="",
                finish_reason="error",
                error_message=str(e),
            )

    def complete_streaming(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> Iterator[str] | None:
        """
        Perform a streaming text completion.

        Args:
            prompt: The text to complete
            context: Optional context dictionary
            max_tokens: Override max tokens from agent config
            temperature: Override temperature from agent config

        Yields:
            Text chunks as they are generated
        """
        if not self._enabled:
            return None

        if not self._provider or not self._default_agent:
            if not self.load_default_agent():
                return None
        provider = cast(BaseProvider, self._provider)
        default_agent = cast(planning.AgentConfig, self._default_agent)

        request = CompletionRequest(
            prompt=prompt,
            context=context or {},
            max_tokens=max_tokens or default_agent.max_tokens,
            temperature=temperature or default_agent.temperature,
            system_prompt=default_agent.system_prompt,
        )

        try:
            return provider.complete_streaming(request)
        except Exception as e:
            logger.error("Streaming completion error: %s", e)
            return None

    def complete_async(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        callback: Callable[[CompletionResponse], None] | None = None,
    ) -> None:
        """
        Perform an asynchronous text completion (for GUI use).

        This method is designed to be called from the main GUI thread.
        It performs the completion in a worker thread and calls the
        callback with the result.

        Args:
            prompt: The text to complete
            context: Optional context dictionary
            callback: Function to call with the completion result
        """
        # Create worker and thread
        worker = CompletionWorker(self, prompt, context or {})
        thread = QThread()
        worker.moveToThread(thread)

        # Store references to prevent garbage collection
        worker_entry = {"worker": worker, "thread": thread}
        self._active_workers.append(worker_entry)

        def cleanup():
            """Remove worker from active list after thread has finished."""
            logger.debug("Cleaning up AI completion worker")
            try:
                self._active_workers.remove(worker_entry)
            except ValueError:
                pass  # Already removed

        # Connect signals - callback first to ensure it runs before cleanup
        if callback:
            worker.finished.connect(callback, Qt.ConnectionType.QueuedConnection)

        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)  # Tell thread event loop to stop

        # Only clean up after thread has actually finished running
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(cleanup)
        thread.finished.connect(thread.deleteLater)

        # Start the thread
        logger.debug("Starting AI completion worker thread")
        thread.start()

    def test_connection(self, provider_type: str, api_key: str, base_url: str, model: str) -> tuple[bool, str]:
        """
        Test connection to an AI provider.

        Args:
            provider_type: The provider type (anthropic, openai, ollama)
            api_key: The API key
            base_url: The base URL
            model: The model to use

        Returns:
            Tuple of (success, message)
        """
        try:
            provider = get_provider(
                provider_type=provider_type,
                api_key=api_key,
                base_url=base_url,
                model=model,
            )

            # First validate the config
            is_valid, error = provider.validate_config(api_key, base_url, model)
            if not is_valid:
                return False, error

            # Try a simple completion
            request = CompletionRequest(
                prompt="Hello",
                context={},
                max_tokens=10,
                temperature=0.0,
            )
            response = provider.complete(request)

            if response.finish_reason == "error":
                return False, response.error_message or "Unknown error"

            return True, f"Connection successful! Response: {response.text[:50]}..."

        except Exception as e:
            return False, str(e)
