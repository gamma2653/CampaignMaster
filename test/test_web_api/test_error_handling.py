"""Tests for error handling, validation, and edge cases in the web API."""

from typing import Callable

import pytest
from fastapi.testclient import TestClient


class TestValidationErrors:
    """Tests for request validation error handling."""

    def test_segment_missing_required_start(
        self,
        test_client: TestClient,
    ):
        """Creating a Segment without start should fail validation."""
        segment_data = {
            "name": "Invalid Segment",
            "description": "Missing start",
            # "start" is missing
            "end": {"prefix": "P", "numeric": 1},
        }

        response = test_client.post("/api/campaign/s", json=segment_data)
        assert response.status_code == 422  # Validation error

    def test_segment_missing_required_end(
        self,
        test_client: TestClient,
    ):
        """Creating a Segment without end should fail validation."""
        segment_data = {
            "name": "Invalid Segment",
            "description": "Missing end",
            "start": {"prefix": "P", "numeric": 1},
            # "end" is missing
        }

        response = test_client.post("/api/campaign/s", json=segment_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_field_type_string_for_int(
        self,
        test_client: TestClient,
    ):
        """Passing a string where an int is expected should fail validation."""
        character_data = {
            "name": "Invalid Character",
            "role": "Test",
            "backstory": "Test",
            "attributes": {"strength": "not_an_int"},  # Should be int
            "skills": {},
            "storylines": [],
            "inventory": [],
        }

        response = test_client.post("/api/campaign/c", json=character_data)
        assert response.status_code == 422

    def test_invalid_id_reference_format(
        self,
        test_client: TestClient,
    ):
        """Passing malformed ID references should fail validation."""
        point_data = {
            "name": "Point with bad objective",
            "description": "Test",
            "objective": {"wrong_key": "value"},  # Missing prefix/numeric
        }

        response = test_client.post("/api/campaign/p", json=point_data)
        # This should either fail validation or cause a 500 error when parsing
        assert response.status_code in [422, 500]

    def test_update_with_missing_obj_id(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """Updating without obj_id in body should fail validation."""
        rule = create_test_resource("rule")
        numeric = rule["obj_id"]["numeric"]

        update_data = {
            # "obj_id" is missing
            "description": "Updated",
            "effect": "Updated",
            "components": [],
        }

        response = test_client.put(f"/api/campaign/r/{numeric}", json=update_data)
        assert response.status_code == 422


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_string_fields(
        self,
        test_client: TestClient,
    ):
        """Creating resources with empty string fields should succeed."""
        rule_data = {
            "description": "",
            "effect": "",
            "components": [],
        }

        response = test_client.post("/api/campaign/r", json=rule_data)
        assert response.status_code == 200

        result = response.json()
        assert result["description"] == ""
        assert result["effect"] == ""

    def test_unicode_content(
        self,
        test_client: TestClient,
    ):
        """Creating resources with unicode content should work."""
        point_data = {
            "name": "日本語テスト",
            "description": "Ελληνικά текст émojis 🎮🎲",
            "objective": None,
        }

        response = test_client.post("/api/campaign/p", json=point_data)
        assert response.status_code == 200

        result = response.json()
        assert result["name"] == "日本語テスト"
        assert "🎮🎲" in result["description"]

    def test_large_text_fields(
        self,
        test_client: TestClient,
    ):
        """Creating resources with large text content should work."""
        large_text = "A" * 10000  # 10KB of text

        character_data = {
            "name": "Character with large backstory",
            "role": "Test",
            "backstory": large_text,
            "attributes": {},
            "skills": {},
            "storylines": [],
            "inventory": [],
        }

        response = test_client.post("/api/campaign/c", json=character_data)
        assert response.status_code == 200

        result = response.json()
        assert len(result["backstory"]) == 10000

    def test_empty_collections(
        self,
        test_client: TestClient,
    ):
        """Creating resources with empty collections should work."""
        character_data = {
            "name": "Minimal Character",
            "role": "",
            "backstory": "",
            "attributes": {},
            "skills": {},
            "storylines": [],
            "inventory": [],
        }

        response = test_client.post("/api/campaign/c", json=character_data)
        assert response.status_code == 200

        result = response.json()
        assert result["attributes"] == {}
        assert result["skills"] == {}
        assert result["storylines"] == []
        assert result["inventory"] == []

    def test_location_2d_coords(
        self,
        test_client: TestClient,
    ):
        """Creating a Location with 2D coordinates should work."""
        location_data = {
            "name": "2D Location",
            "description": "Location with 2D coords",
            "neighboring_locations": [],
            "coords": [10.5, 20.5],
        }

        response = test_client.post("/api/campaign/l", json=location_data)
        assert response.status_code == 200

        result = response.json()
        assert result["coords"] is not None
        assert len(result["coords"]) == 2

    def test_location_3d_coords(
        self,
        test_client: TestClient,
    ):
        """Creating a Location with 3D coordinates should work."""
        location_data = {
            "name": "3D Location",
            "description": "Location with 3D coords",
            "neighboring_locations": [],
            "coords": [10.5, 20.5, 30.5],
        }

        response = test_client.post("/api/campaign/l", json=location_data)
        assert response.status_code == 200

        result = response.json()
        assert result["coords"] is not None
        assert len(result["coords"]) == 3

    def test_location_null_coords(
        self,
        test_client: TestClient,
    ):
        """Creating a Location with null coordinates should work."""
        location_data = {
            "name": "No Coords Location",
            "description": "Location without coords",
            "neighboring_locations": [],
            "coords": None,
        }

        response = test_client.post("/api/campaign/l", json=location_data)
        assert response.status_code == 200

        result = response.json()
        assert result["coords"] is None

    def test_item_complex_properties(
        self,
        test_client: TestClient,
    ):
        """Creating an Item with complex properties dict should work."""
        item_data = {
            "name": "Complex Item",
            "type_": "artifact",
            "description": "An item with many properties",
            "properties": {
                "damage": "2d6+3",
                "range": "60ft",
                "weight": "5lbs",
                "rarity": "legendary",
                "attunement": "required",
            },
        }

        response = test_client.post("/api/campaign/i", json=item_data)
        assert response.status_code == 200

        result = response.json()
        assert len(result["properties"]) == 5
        assert result["properties"]["damage"] == "2d6+3"

    def test_agent_config_defaults(
        self,
        test_client: TestClient,
    ):
        """Creating an AgentConfig with minimal data should use defaults."""
        agent_data = {
            "name": "Minimal Agent",
            "provider_type": "openai",
            "api_key": "key",
            "base_url": "",
            "model": "gpt-3.5",
            # max_tokens, temperature should use defaults
        }

        response = test_client.post("/api/campaign/ag", json=agent_data)
        assert response.status_code == 200

        result = response.json()
        assert result["max_tokens"] == 500  # Default value
        assert result["temperature"] == 0.7  # Default value


class TestProtoUserIsolation:
    """Tests for proto_user_id isolation across all operations."""

    def test_independent_id_sequences_per_user(
        self,
        test_client: TestClient,
    ):
        """Each proto_user should have independent ID sequences."""
        rule_data = {
            "description": "Test Rule",
            "effect": "Effect",
            "components": [],
        }

        # Create rule for user 0
        response0 = test_client.post("/api/campaign/r", json=rule_data, params={"proto_user_id": 0})
        assert response0.status_code == 200
        user0_numeric = response0.json()["obj_id"]["numeric"]

        # Create rule for user 1
        response1 = test_client.post("/api/campaign/r", json=rule_data, params={"proto_user_id": 1})
        assert response1.status_code == 200
        user1_numeric = response1.json()["obj_id"]["numeric"]

        # Each user should have their own sequence starting at 1
        assert user0_numeric == 1
        assert user1_numeric == 1

    def test_cross_user_access_blocked_on_get(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """Resources cannot be accessed by other users."""
        # Create for user 0
        item = create_test_resource("item", proto_user_id=0)
        numeric = item["obj_id"]["numeric"]

        # Try to access as user 1 - should 404
        response = test_client.get(f"/api/campaign/i/{numeric}", params={"proto_user_id": 1})
        assert response.status_code == 404

        # Access as user 0 should work
        response = test_client.get(f"/api/campaign/i/{numeric}", params={"proto_user_id": 0})
        assert response.status_code == 200

    def test_cross_user_access_blocked_on_update(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """Resources cannot be updated by other users."""
        # Create for user 0
        item = create_test_resource("item", proto_user_id=0)
        numeric = item["obj_id"]["numeric"]

        update_data = {
            "obj_id": item["obj_id"],
            "name": "Hacked Item",
            "type_": "stolen",
            "description": "Attempted cross-user update",
            "properties": {},
        }

        # Try to update as user 1 - should 404
        response = test_client.put(
            f"/api/campaign/i/{numeric}", json=update_data, params={"proto_user_id": 1}
        )
        assert response.status_code == 404

        # Verify original still intact for user 0
        response = test_client.get(f"/api/campaign/i/{numeric}", params={"proto_user_id": 0})
        assert response.status_code == 200
        assert response.json()["name"] == item["name"]  # Unchanged

    def test_cross_user_access_blocked_on_delete(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """Resources cannot be deleted by other users."""
        # Create for user 0
        item = create_test_resource("item", proto_user_id=0)
        numeric = item["obj_id"]["numeric"]

        # Try to delete as user 1 - should 404
        response = test_client.delete(f"/api/campaign/i/{numeric}", params={"proto_user_id": 1})
        assert response.status_code == 404

        # Verify still exists for user 0
        response = test_client.get(f"/api/campaign/i/{numeric}", params={"proto_user_id": 0})
        assert response.status_code == 200

    def test_list_only_shows_own_resources(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """List endpoints only show resources for the requesting user."""
        # Create resources for multiple users
        create_test_resource("rule", proto_user_id=0)
        create_test_resource("rule", proto_user_id=0)
        create_test_resource("rule", proto_user_id=1)

        # List for user 0
        response0 = test_client.get("/api/campaign/r", params={"proto_user_id": 0})
        assert response0.status_code == 200
        assert len(response0.json()) == 2

        # List for user 1
        response1 = test_client.get("/api/campaign/r", params={"proto_user_id": 1})
        assert response1.status_code == 200
        assert len(response1.json()) == 1

        # List for user 2 (has nothing)
        response2 = test_client.get("/api/campaign/r", params={"proto_user_id": 2})
        assert response2.status_code == 200
        assert len(response2.json()) == 0


class TestCampaignPlanNestedOperations:
    """Tests specific to CampaignPlan with nested collections."""

    def test_create_campaign_with_empty_collections(
        self,
        test_client: TestClient,
    ):
        """Creating a CampaignPlan with empty collections should work."""
        campaign_data = {
            "title": "Empty Campaign",
            "version": "1.0",
            "setting": "Generic",
            "summary": "A campaign with no content yet",
            "storypoints": [],
            "storyline": [],
            "characters": [],
            "locations": [],
            "items": [],
            "rules": [],
            "objectives": [],
        }

        response = test_client.post("/api/campaign/campplan", json=campaign_data)
        assert response.status_code == 200

        result = response.json()
        assert result["title"] == "Empty Campaign"
        assert result["storypoints"] == []
        assert result["storyline"] == []

    def test_update_campaign_scalar_fields_only(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """Updating only scalar fields of a CampaignPlan should work."""
        campaign = create_test_resource("campaign_plan")
        numeric = campaign["obj_id"]["numeric"]

        update_data = {
            "obj_id": campaign["obj_id"],
            "title": "Updated Title",
            "version": "2.0",
            "setting": "New Setting",
            "summary": "Updated summary",
            "storypoints": [],
            "storyline": [],
            "characters": [],
            "locations": [],
            "items": [],
            "rules": [],
            "objectives": [],
        }

        response = test_client.put(f"/api/campaign/campplan/{numeric}", json=update_data)
        assert response.status_code == 200

        result = response.json()
        assert result["title"] == "Updated Title"
        assert result["version"] == "2.0"
