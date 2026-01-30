"""Tests for sequential ID generation across CampaignPlan components.

These tests verify that IDs are created sequentially starting from 1 when adding
components in a fresh database. This is critical for the React frontend to
display predictable IDs like P-000001, P-000002, etc.
"""

from typing import Any, Callable

import pytest
from fastapi.testclient import TestClient

from .conftest import RESOURCE_CONFIGS


class TestSequentialIDCreation:
    """Tests that IDs are created sequentially starting from 1."""

    @pytest.mark.parametrize(
        "resource_name",
        ["point", "objective", "rule", "segment", "arc", "item", "character", "location", "campaign_plan"],
    )
    def test_first_id_starts_at_one(
        self,
        test_client: TestClient,
        resource_name: str,
    ):
        """The first resource created in a fresh database should have numeric ID = 1."""
        config = RESOURCE_CONFIGS[resource_name]
        endpoint = config["endpoint"]
        create_data = config["create_data"]

        response = test_client.post(endpoint, json=create_data)
        assert response.status_code == 200

        result = response.json()
        assert (
            result["obj_id"]["numeric"] == 1
        ), f"First {resource_name} should have numeric ID 1, got {result['obj_id']['numeric']}"

    @pytest.mark.parametrize(
        "resource_name",
        ["point", "objective", "rule", "item", "character", "location"],
    )
    def test_five_sequential_ids(
        self,
        test_client: TestClient,
        resource_name: str,
    ):
        """Creating 5 resources should assign IDs 1, 2, 3, 4, 5 sequentially."""
        config = RESOURCE_CONFIGS[resource_name]
        endpoint = config["endpoint"]
        create_data = config["create_data"]

        numerics = []
        for i in range(5):
            response = test_client.post(endpoint, json=create_data)
            assert response.status_code == 200
            numerics.append(response.json()["obj_id"]["numeric"])

        assert numerics == [
            1,
            2,
            3,
            4,
            5,
        ], f"Expected sequential IDs [1, 2, 3, 4, 5] for {resource_name}, got {numerics}"

    def test_point_ids_sequential_from_fresh_database(
        self,
        test_client: TestClient,
    ):
        """Points should be assigned P-1, P-2, P-3 in a fresh database."""
        endpoint = "/api/campaign/p"
        create_data = {
            "name": "Test Point",
            "description": "A test point",
            "objective": None,
        }

        # Create 3 points
        ids = []
        for i in range(3):
            response = test_client.post(endpoint, json=create_data)
            assert response.status_code == 200
            result = response.json()
            ids.append(result["obj_id"])

        # Verify all have prefix "P" and sequential numerics
        assert all(id_["prefix"] == "P" for id_ in ids)
        assert [id_["numeric"] for id_ in ids] == [1, 2, 3]


class TestSequentialIDsPerUser:
    """Tests that each authenticated user has its own ID sequence starting from 1."""

    @pytest.mark.parametrize(
        "resource_name",
        ["point", "rule", "character"],
    )
    def test_different_users_get_independent_sequences(
        self,
        test_client: TestClient,
        register_user: Callable,
        resource_name: str,
    ):
        """Different users should each have their own ID sequence starting at 1."""
        config = RESOURCE_CONFIGS[resource_name]
        endpoint = config["endpoint"]
        create_data = config["create_data"]

        # Create 2 resources for default user
        response1_u0 = test_client.post(endpoint, json=create_data)
        response2_u0 = test_client.post(endpoint, json=create_data)

        # Create 2 resources for a different user
        client2, _ = register_user(f"seq_{resource_name}_u2", f"seq_{resource_name}_u2@example.com")
        response1_u1 = client2.post(endpoint, json=create_data)
        response2_u1 = client2.post(endpoint, json=create_data)

        # Default user should have IDs 1 and 2
        assert response1_u0.json()["obj_id"]["numeric"] == 1
        assert response2_u0.json()["obj_id"]["numeric"] == 2

        # User 2 should ALSO have IDs 1 and 2 (independent sequence)
        assert response1_u1.json()["obj_id"]["numeric"] == 1
        assert response2_u1.json()["obj_id"]["numeric"] == 2

    def test_interleaved_user_creation_maintains_sequences(
        self,
        test_client: TestClient,
        register_user: Callable,
    ):
        """Interleaving creation between users should maintain correct sequences."""
        endpoint = "/api/campaign/p"
        create_data = {"name": "Test Point", "description": "Test", "objective": None}

        client2, _ = register_user("interleave_u2", "interleave_u2@example.com")

        # Interleave creations: user0, user1, user0, user1, user0
        r1 = test_client.post(endpoint, json=create_data)  # user0: 1
        r2 = client2.post(endpoint, json=create_data)  # user1: 1
        r3 = test_client.post(endpoint, json=create_data)  # user0: 2
        r4 = client2.post(endpoint, json=create_data)  # user1: 2
        r5 = test_client.post(endpoint, json=create_data)  # user0: 3

        # Verify user 0 sequence
        assert r1.json()["obj_id"]["numeric"] == 1
        assert r3.json()["obj_id"]["numeric"] == 2
        assert r5.json()["obj_id"]["numeric"] == 3

        # Verify user 1 sequence
        assert r2.json()["obj_id"]["numeric"] == 1
        assert r4.json()["obj_id"]["numeric"] == 2


class TestSequentialIDsAcrossResourceTypes:
    """Tests that different resource types have independent ID sequences."""

    def test_different_resource_types_have_independent_sequences(
        self,
        test_client: TestClient,
    ):
        """Points and Characters should each start at 1 independently."""
        point_endpoint = "/api/campaign/p"
        character_endpoint = "/api/campaign/c"

        point_data = {"name": "Test Point", "description": "Test", "objective": None}
        character_data = {
            "name": "Test Character",
            "role": "NPC",
            "backstory": "Test",
            "attributes": {},
            "skills": {},
            "storylines": [],
            "inventory": [],
        }

        # Create points first
        p1 = test_client.post(point_endpoint, json=point_data)
        p2 = test_client.post(point_endpoint, json=point_data)

        # Now create characters - should start at 1, not 3
        c1 = test_client.post(character_endpoint, json=character_data)
        c2 = test_client.post(character_endpoint, json=character_data)

        # Points should be 1, 2
        assert p1.json()["obj_id"]["prefix"] == "P"
        assert p1.json()["obj_id"]["numeric"] == 1
        assert p2.json()["obj_id"]["numeric"] == 2

        # Characters should also be 1, 2 (independent sequence)
        assert c1.json()["obj_id"]["prefix"] == "C"
        assert c1.json()["obj_id"]["numeric"] == 1
        assert c2.json()["obj_id"]["numeric"] == 2

    def test_all_campaign_components_start_at_one(
        self,
        test_client: TestClient,
    ):
        """All component types used in CampaignPlan should start at ID 1."""
        # Define all component types with their endpoints and minimal create data
        components = [
            ("/api/campaign/p", {"name": "Point", "description": "", "objective": None}),
            ("/api/campaign/o", {"description": "Objective", "components": [], "prerequisites": []}),
            ("/api/campaign/r", {"description": "Rule", "effect": "", "components": []}),
            (
                "/api/campaign/s",
                {
                    "name": "Segment",
                    "description": "",
                    "start": {"prefix": "P", "numeric": 1},
                    "end": {"prefix": "P", "numeric": 1},
                },
            ),
            ("/api/campaign/a", {"name": "Arc", "description": "", "segments": []}),
            ("/api/campaign/i", {"name": "Item", "type_": "misc", "description": "", "properties": {}}),
            (
                "/api/campaign/c",
                {
                    "name": "Character",
                    "role": "",
                    "backstory": "",
                    "attributes": {},
                    "skills": {},
                    "storylines": [],
                    "inventory": [],
                },
            ),
            ("/api/campaign/l", {"name": "Location", "description": "", "neighboring_locations": [], "coords": None}),
        ]

        for endpoint, create_data in components:
            response = test_client.post(endpoint, json=create_data)
            assert response.status_code == 200, f"Failed to create at {endpoint}: {response.text}"
            result = response.json()
            assert (
                result["obj_id"]["numeric"] == 1
            ), f"First resource at {endpoint} should have numeric 1, got {result['obj_id']['numeric']}"


class TestSequentialIDsAfterDeletion:
    """Tests that ID sequence continues after deletions (no reuse of deleted IDs)."""

    @pytest.mark.parametrize(
        "resource_name",
        ["point", "rule", "character"],
    )
    def test_deleted_ids_are_not_reused(
        self,
        test_client: TestClient,
        resource_name: str,
    ):
        """After deleting an ID, the next creation should continue the sequence."""
        config = RESOURCE_CONFIGS[resource_name]
        endpoint = config["endpoint"]
        create_data = config["create_data"]

        # Create 3 resources (IDs 1, 2, 3)
        r1 = test_client.post(endpoint, json=create_data)
        r2 = test_client.post(endpoint, json=create_data)
        r3 = test_client.post(endpoint, json=create_data)

        assert r1.json()["obj_id"]["numeric"] == 1
        assert r2.json()["obj_id"]["numeric"] == 2
        assert r3.json()["obj_id"]["numeric"] == 3

        # Delete ID 2
        delete_response = test_client.delete(f"{endpoint}/2")
        assert delete_response.status_code == 200

        # Create a new resource - should be ID 4, not 2
        r4 = test_client.post(endpoint, json=create_data)
        assert (
            r4.json()["obj_id"]["numeric"] == 4
        ), f"After deleting ID 2, next ID should be 4, got {r4.json()['obj_id']['numeric']}"

    def test_sequence_continues_after_deleting_last_id(
        self,
        test_client: TestClient,
    ):
        """Deleting the last ID should not reset the sequence."""
        endpoint = "/api/campaign/p"
        create_data = {"name": "Test Point", "description": "", "objective": None}

        # Create 2 points
        r1 = test_client.post(endpoint, json=create_data)
        r2 = test_client.post(endpoint, json=create_data)

        assert r1.json()["obj_id"]["numeric"] == 1
        assert r2.json()["obj_id"]["numeric"] == 2

        # Delete the last one (ID 2)
        delete_response = test_client.delete(f"{endpoint}/2")
        assert delete_response.status_code == 200

        # Create a new point - should be ID 3, not 2
        r3 = test_client.post(endpoint, json=create_data)
        assert r3.json()["obj_id"]["numeric"] == 3


class TestSequentialIDsListOrder:
    """Tests that listing resources returns them in creation order."""

    @pytest.mark.parametrize(
        "resource_name",
        ["point", "rule", "objective", "character"],
    )
    def test_list_returns_resources_in_id_order(
        self,
        test_client: TestClient,
        resource_name: str,
    ):
        """Listing resources should return them ordered by ID."""
        config = RESOURCE_CONFIGS[resource_name]
        endpoint = config["endpoint"]
        create_data = config["create_data"]

        # Create 5 resources
        for _ in range(5):
            test_client.post(endpoint, json=create_data)

        # List all resources
        response = test_client.get(endpoint)
        assert response.status_code == 200

        results = response.json()
        assert len(results) == 5

        # Extract numeric IDs and verify they are sequential
        numerics = [r["obj_id"]["numeric"] for r in results]
        assert numerics == [1, 2, 3, 4, 5] or numerics == sorted(
            numerics
        ), f"List should return IDs in order, got {numerics}"
