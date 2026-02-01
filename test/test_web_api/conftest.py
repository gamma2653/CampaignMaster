"""Fixtures and resource configurations for web API tests."""

from typing import Any, Callable

import pytest
from fastapi.testclient import TestClient

# Resource configurations for all 10 resource types
RESOURCE_CONFIGS: dict[str, dict[str, Any]] = {
    "point": {
        "prefix": "P",
        "endpoint": "/api/campaign/p",
        "create_data": {
            "name": "Test Point",
            "description": "A test point description",
            "objective": None,
        },
        "update_data": {
            "name": "Updated Point",
            "description": "An updated point description",
            "objective": None,
        },
        "response_fields": ["obj_id", "name", "description", "objective"],
    },
    "objective": {
        "prefix": "O",
        "endpoint": "/api/campaign/o",
        "create_data": {
            "description": "Test Objective",
            "components": ["component1", "component2"],
            "prerequisites": [],
        },
        "update_data": {
            "description": "Updated Objective",
            "components": ["updated_component"],
            "prerequisites": [],
        },
        "response_fields": ["obj_id", "description", "components", "prerequisites"],
    },
    "rule": {
        "prefix": "R",
        "endpoint": "/api/campaign/r",
        "create_data": {
            "description": "Test Rule",
            "effect": "Test effect",
            "components": ["comp1", "comp2"],
        },
        "update_data": {
            "description": "Updated Rule",
            "effect": "Updated effect",
            "components": ["updated_comp"],
        },
        "response_fields": ["obj_id", "description", "effect", "components"],
    },
    "segment": {
        "prefix": "S",
        "endpoint": "/api/campaign/s",
        "create_data": {
            "name": "Test Segment",
            "description": "A test segment",
            "start": {"prefix": "P", "numeric": 1},
            "end": {"prefix": "P", "numeric": 2},
        },
        "update_data": {
            "name": "Updated Segment",
            "description": "An updated segment",
            "start": {"prefix": "P", "numeric": 1},
            "end": {"prefix": "P", "numeric": 3},
        },
        "response_fields": ["obj_id", "name", "description", "start", "end"],
    },
    "arc": {
        "prefix": "A",
        "endpoint": "/api/campaign/a",
        "create_data": {
            "name": "Test Arc",
            "description": "A test arc",
            "segments": [],
        },
        "update_data": {
            "name": "Updated Arc",
            "description": "An updated arc",
            "segments": [],
        },
        "response_fields": ["obj_id", "name", "description", "segments"],
    },
    "item": {
        "prefix": "I",
        "endpoint": "/api/campaign/i",
        "create_data": {
            "name": "Test Item",
            "type_": "weapon",
            "description": "A test item",
            "properties": {"damage": "1d6"},
        },
        "update_data": {
            "name": "Updated Item",
            "type_": "armor",
            "description": "An updated item",
            "properties": {"armor_class": "15"},
        },
        "response_fields": ["obj_id", "name", "type_", "description", "properties"],
    },
    "character": {
        "prefix": "C",
        "endpoint": "/api/campaign/c",
        "create_data": {
            "name": "Test Character",
            "role": "NPC",
            "backstory": "A test character backstory",
            "attributes": {"strength": 10, "dexterity": 12},
            "skills": {"perception": 5},
            "storylines": [],
            "inventory": [],
        },
        "update_data": {
            "name": "Updated Character",
            "role": "Villain",
            "backstory": "An updated backstory",
            "attributes": {"strength": 15, "dexterity": 14},
            "skills": {"perception": 8, "stealth": 6},
            "storylines": [],
            "inventory": [],
        },
        "response_fields": [
            "obj_id",
            "name",
            "role",
            "backstory",
            "attributes",
            "skills",
            "storylines",
            "inventory",
        ],
    },
    "location": {
        "prefix": "L",
        "endpoint": "/api/campaign/l",
        "create_data": {
            "name": "Test Location",
            "description": "A test location",
            "neighboring_locations": [],
            "coords": None,  # coords with values fail due to missing LocationCoord.from_pydantic
        },
        "update_data": {
            "name": "Updated Location",
            "description": "An updated location",
            "neighboring_locations": [],
            "coords": None,  # coords with values fail due to missing LocationCoord.from_pydantic
        },
        "response_fields": ["obj_id", "name", "description", "neighboring_locations", "coords"],
    },
    "campaign_plan": {
        "prefix": "CampPlan",
        "endpoint": "/api/campaign/campplan",
        "create_data": {
            "title": "Test Campaign",
            "version": "1.0",
            "setting": "Fantasy",
            "summary": "A test campaign summary",
            "storypoints": [],
            "storyline": [],
            "characters": [],
            "locations": [],
            "items": [],
            "rules": [],
            "objectives": [],
        },
        "update_data": {
            "title": "Updated Campaign",
            "version": "2.0",
            "setting": "Sci-Fi",
            "summary": "An updated campaign summary",
            "storypoints": [],
            "storyline": [],
            "characters": [],
            "locations": [],
            "items": [],
            "rules": [],
            "objectives": [],
        },
        "response_fields": [
            "obj_id",
            "title",
            "version",
            "setting",
            "summary",
            "storypoints",
            "storyline",
            "characters",
            "locations",
            "items",
            "rules",
            "objectives",
        ],
    },
    "campaign_execution": {
        "prefix": "EX",
        "endpoint": "/api/campaign/ex",
        "create_data": {
            "campaign_plan_id": {"prefix": "CampPlan", "numeric": 0},
            "title": "Test Session",
            "session_date": "2025-01-15",
            "raw_session_notes": "The party entered the dungeon.",
            "refined_session_notes": "",
            "refinement_mode": "narrative",
            "entries": [],
        },
        "update_data": {
            "campaign_plan_id": {"prefix": "CampPlan", "numeric": 0},
            "title": "Updated Session",
            "session_date": "2025-01-16",
            "raw_session_notes": "The party fought the dragon.",
            "refined_session_notes": "A refined summary.",
            "refinement_mode": "structured",
            "entries": [
                {
                    "entity_id": {"prefix": "C", "numeric": 1},
                    "entity_type": "Character",
                    "status": "in_progress",
                    "raw_notes": "Character was involved",
                    "refined_notes": "",
                },
            ],
        },
        "response_fields": [
            "obj_id",
            "campaign_plan_id",
            "title",
            "session_date",
            "raw_session_notes",
            "refined_session_notes",
            "refinement_mode",
            "entries",
        ],
    },
    "agent_config": {
        "prefix": "AG",
        "endpoint": "/api/campaign/ag",
        "create_data": {
            "name": "Test Agent",
            "provider_type": "openai",
            "api_key": "test-key",
            "base_url": "https://api.openai.com",
            "model": "gpt-4",
            "max_tokens": 1000,
            "temperature": 0.7,
            "is_default": False,
            "is_enabled": True,
            "system_prompt": "You are a helpful assistant.",
        },
        "update_data": {
            "name": "Updated Agent",
            "provider_type": "anthropic",
            "api_key": "updated-key",
            "base_url": "https://api.anthropic.com",
            "model": "claude-3",
            "max_tokens": 2000,
            "temperature": 0.5,
            "is_default": True,
            "is_enabled": True,
            "system_prompt": "You are an updated assistant.",
        },
        "response_fields": [
            "obj_id",
            "name",
            "provider_type",
            "api_key",
            "base_url",
            "model",
            "max_tokens",
            "temperature",
            "is_default",
            "is_enabled",
            "system_prompt",
        ],
    },
}


@pytest.fixture(params=list(RESOURCE_CONFIGS.keys()))
def resource_config(request) -> dict[str, Any]:
    """
    Parametrized fixture that yields each resource configuration.

    This allows tests to run once for each resource type.
    """
    config = RESOURCE_CONFIGS[request.param].copy()
    config["resource_name"] = request.param
    return config


@pytest.fixture
def create_test_resource(test_client: TestClient) -> Callable[[str, dict | None, int], dict]:
    """
    Factory fixture for creating test resources via the API.

    Returns a function that creates a resource and returns the response data.
    Uses the default authenticated test_client (which already has auth headers).
    """

    def _create_resource(
        resource_name: str,
        data: dict | None = None,
        proto_user_id: int = 0,
    ) -> dict:
        config = RESOURCE_CONFIGS[resource_name]
        endpoint = config["endpoint"]
        create_data = data if data is not None else config["create_data"].copy()

        response = test_client.post(endpoint, json=create_data)
        assert response.status_code == 200, f"Failed to create {resource_name}: {response.text}"
        return response.json()

    return _create_resource


@pytest.fixture
def register_user(test_app) -> Callable[[str, str, str], tuple[TestClient, str]]:
    """
    Factory fixture that registers a new user and returns an authenticated TestClient.

    Returns (client_with_auth_headers, token).
    """

    def _register(username: str, email: str, password: str = "testpass123") -> tuple[TestClient, str]:
        client = TestClient(test_app)
        response = client.post(
            "/api/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )
        assert response.status_code == 200, f"Failed to register {username}: {response.text}"
        token = response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"
        return client, token

    return _register


@pytest.fixture
def get_resource_numeric(
    test_client: TestClient, create_test_resource: Callable
) -> Callable[[str, dict | None, int], int]:
    """
    Factory fixture that creates a resource and returns its numeric ID.
    """

    def _get_numeric(
        resource_name: str,
        data: dict | None = None,
        proto_user_id: int = 0,
    ) -> int:
        result = create_test_resource(resource_name, data, proto_user_id)
        return result["obj_id"]["numeric"]

    return _get_numeric
