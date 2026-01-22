"""Parametrized CRUD tests for all resource types."""

from typing import Any, Callable

import pytest
from fastapi.testclient import TestClient


class TestListEndpoints:
    """Tests for LIST (GET all) endpoints."""

    def test_list_empty_returns_empty_array(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
    ):
        """Listing resources when none exist should return an empty array."""
        endpoint = resource_config["endpoint"]
        response = test_client.get(endpoint)

        assert response.status_code == 200
        assert response.json() == []

    def test_list_returns_created_resources(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
    ):
        """Listing resources should return all created resources."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]

        # Create two resources
        created1 = create_test_resource(resource_name)
        created2 = create_test_resource(resource_name)

        response = test_client.get(endpoint)
        assert response.status_code == 200

        results = response.json()
        assert len(results) == 2

        # Verify both created resources are in the list
        numerics = [r["obj_id"]["numeric"] for r in results]
        assert created1["obj_id"]["numeric"] in numerics
        assert created2["obj_id"]["numeric"] in numerics

    def test_list_with_proto_user_id_isolation(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
    ):
        """Resources created by different proto_user_ids should be isolated."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]

        # Create resources for user 0
        create_test_resource(resource_name, proto_user_id=0)

        # Create resources for user 1
        create_test_resource(resource_name, proto_user_id=1)

        # List for user 0 - should only see 1 resource
        response0 = test_client.get(endpoint, params={"proto_user_id": 0})
        assert response0.status_code == 200
        results0 = response0.json()
        assert len(results0) == 1, f"User 0 should see 1 resource, got {len(results0)}"

        # List for user 1 - should only see 1 resource
        response1 = test_client.get(endpoint, params={"proto_user_id": 1})
        assert response1.status_code == 200
        results1 = response1.json()
        assert len(results1) == 1, f"User 1 should see 1 resource, got {len(results1)}"

        # List for user 2 (no resources) - should see 0 resources
        response2 = test_client.get(endpoint, params={"proto_user_id": 2})
        assert response2.status_code == 200
        results2 = response2.json()
        assert len(results2) == 0, f"User 2 should see 0 resources, got {len(results2)}"


class TestGetSingleEndpoints:
    """Tests for GET single resource endpoints."""

    def test_get_existing_resource(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
    ):
        """Getting an existing resource should return its data."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]
        response_fields = resource_config["response_fields"]

        created = create_test_resource(resource_name)
        numeric = created["obj_id"]["numeric"]

        response = test_client.get(f"{endpoint}/{numeric}")
        assert response.status_code == 200

        result = response.json()
        # Verify all expected fields are present
        for field in response_fields:
            assert field in result, f"Missing field: {field}"

        # Verify the obj_id matches
        assert result["obj_id"]["numeric"] == numeric

    def test_get_nonexistent_resource_returns_404(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
    ):
        """Getting a non-existent resource should return 404."""
        endpoint = resource_config["endpoint"]

        response = test_client.get(f"{endpoint}/99999")
        assert response.status_code == 404

    def test_get_with_wrong_proto_user_id_returns_404(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
    ):
        """Getting a resource with wrong proto_user_id should return 404."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]

        # Create resource for user 0
        created = create_test_resource(resource_name, proto_user_id=0)
        numeric = created["obj_id"]["numeric"]

        # Try to get it as user 1
        response = test_client.get(f"{endpoint}/{numeric}", params={"proto_user_id": 1})
        assert response.status_code == 404


class TestCreateEndpoints:
    """Tests for POST (create) endpoints."""

    def test_create_returns_created_resource(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
    ):
        """Creating a resource should return the created resource with an ID."""
        endpoint = resource_config["endpoint"]
        create_data = resource_config["create_data"]
        response_fields = resource_config["response_fields"]

        response = test_client.post(endpoint, json=create_data)
        assert response.status_code == 200

        result = response.json()
        # Verify all expected fields are present
        for field in response_fields:
            assert field in result, f"Missing field: {field}"

        # Verify obj_id was assigned
        assert "obj_id" in result
        assert "prefix" in result["obj_id"]
        assert "numeric" in result["obj_id"]
        assert result["obj_id"]["prefix"] == resource_config["prefix"]
        assert result["obj_id"]["numeric"] > 0

    def test_create_assigns_sequential_ids(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
    ):
        """Creating multiple resources should assign sequential IDs."""
        endpoint = resource_config["endpoint"]
        create_data = resource_config["create_data"]

        response1 = test_client.post(endpoint, json=create_data)
        assert response1.status_code == 200
        numeric1 = response1.json()["obj_id"]["numeric"]

        response2 = test_client.post(endpoint, json=create_data)
        assert response2.status_code == 200
        numeric2 = response2.json()["obj_id"]["numeric"]

        assert numeric2 == numeric1 + 1

    def test_create_with_custom_proto_user_id(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
    ):
        """Creating a resource with a custom proto_user_id should work."""
        endpoint = resource_config["endpoint"]
        create_data = resource_config["create_data"]

        response = test_client.post(endpoint, json=create_data, params={"proto_user_id": 42})
        assert response.status_code == 200

        result = response.json()
        assert "obj_id" in result
        assert result["obj_id"]["numeric"] > 0


class TestUpdateEndpoints:
    """Tests for PUT (update) endpoints."""

    def test_update_existing_resource(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
    ):
        """Updating an existing resource should return the updated data."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]
        update_data = resource_config["update_data"].copy()

        # Create resource
        created = create_test_resource(resource_name)
        numeric = created["obj_id"]["numeric"]
        prefix = created["obj_id"]["prefix"]

        # Add obj_id to update data (required by API)
        update_data["obj_id"] = {"prefix": prefix, "numeric": numeric}

        response = test_client.put(f"{endpoint}/{numeric}", json=update_data)
        assert response.status_code == 200

        result = response.json()
        assert result["obj_id"]["numeric"] == numeric

    def test_update_nonexistent_returns_404(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
    ):
        """Updating a non-existent resource should return 404."""
        endpoint = resource_config["endpoint"]
        prefix = resource_config["prefix"]
        update_data = resource_config["update_data"].copy()
        update_data["obj_id"] = {"prefix": prefix, "numeric": 99999}

        response = test_client.put(f"{endpoint}/99999", json=update_data)
        assert response.status_code == 404

    def test_update_with_wrong_proto_user_id_returns_404(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
    ):
        """Updating a resource with wrong proto_user_id should return 404."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]
        update_data = resource_config["update_data"].copy()

        # Create resource for user 0
        created = create_test_resource(resource_name, proto_user_id=0)
        numeric = created["obj_id"]["numeric"]
        prefix = created["obj_id"]["prefix"]

        update_data["obj_id"] = {"prefix": prefix, "numeric": numeric}

        # Try to update as user 1
        response = test_client.put(
            f"{endpoint}/{numeric}", json=update_data, params={"proto_user_id": 1}
        )
        assert response.status_code == 404


class TestDeleteEndpoints:
    """Tests for DELETE endpoints."""

    def test_delete_existing_resource(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
    ):
        """Deleting an existing resource should succeed."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]

        # Create resource
        created = create_test_resource(resource_name)
        numeric = created["obj_id"]["numeric"]

        # Delete it
        response = test_client.delete(f"{endpoint}/{numeric}")
        assert response.status_code == 200
        assert response.json() == {"success": True}

        # Verify it's gone
        get_response = test_client.get(f"{endpoint}/{numeric}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_returns_404(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
    ):
        """Deleting a non-existent resource should return 404."""
        endpoint = resource_config["endpoint"]

        response = test_client.delete(f"{endpoint}/99999")
        assert response.status_code == 404

    def test_delete_with_wrong_proto_user_id_returns_404(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
    ):
        """Deleting a resource with wrong proto_user_id should return 404."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]

        # Create resource for user 0
        created = create_test_resource(resource_name, proto_user_id=0)
        numeric = created["obj_id"]["numeric"]

        # Try to delete as user 1
        response = test_client.delete(f"{endpoint}/{numeric}", params={"proto_user_id": 1})
        assert response.status_code == 404

        # Verify it still exists for user 0
        get_response = test_client.get(f"{endpoint}/{numeric}", params={"proto_user_id": 0})
        assert get_response.status_code == 200

    def test_delete_idempotent(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
    ):
        """Deleting a resource twice should return 404 on second attempt."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]

        # Create resource
        created = create_test_resource(resource_name)
        numeric = created["obj_id"]["numeric"]

        # Delete it
        response1 = test_client.delete(f"{endpoint}/{numeric}")
        assert response1.status_code == 200

        # Try to delete again
        response2 = test_client.delete(f"{endpoint}/{numeric}")
        assert response2.status_code == 404
