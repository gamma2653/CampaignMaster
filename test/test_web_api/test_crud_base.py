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

    def test_list_with_user_isolation(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
        register_user: Callable,
    ):
        """Resources created by different users should be isolated."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]

        # Create resource for default user (test_client)
        create_test_resource(resource_name)

        # Create resource for a different user
        client2, _ = register_user("user2", "user2@example.com")
        config = resource_config
        response2 = client2.post(endpoint, json=config["create_data"])
        assert response2.status_code == 200

        # List for default user - should only see 1 resource
        response0 = test_client.get(endpoint)
        assert response0.status_code == 200
        results0 = response0.json()
        assert len(results0) == 1, f"Default user should see 1 resource, got {len(results0)}"

        # List for user 2 - should only see 1 resource
        response1 = client2.get(endpoint)
        assert response1.status_code == 200
        results1 = response1.json()
        assert len(results1) == 1, f"User 2 should see 1 resource, got {len(results1)}"

        # Unauthenticated request should get 401
        from fastapi.testclient import TestClient as TC

        unauth_response = test_client.get(endpoint, headers={"Authorization": ""})
        assert unauth_response.status_code == 401


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

    def test_get_with_wrong_user_returns_404(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
        register_user: Callable,
    ):
        """Getting a resource created by another user should return 404."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]

        # Create resource for default user
        created = create_test_resource(resource_name)
        numeric = created["obj_id"]["numeric"]

        # Try to get it as a different user
        client2, _ = register_user("user_get_wrong", "user_get_wrong@example.com")
        response = client2.get(f"{endpoint}/{numeric}")
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

    def test_create_requires_auth(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
    ):
        """Creating a resource without auth should return 401."""
        endpoint = resource_config["endpoint"]
        create_data = resource_config["create_data"]

        response = test_client.post(endpoint, json=create_data, headers={"Authorization": ""})
        assert response.status_code == 401


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

    def test_update_with_wrong_user_returns_404(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
        register_user: Callable,
    ):
        """Updating a resource created by another user should return 404."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]
        update_data = resource_config["update_data"].copy()

        # Create resource for default user
        created = create_test_resource(resource_name)
        numeric = created["obj_id"]["numeric"]
        prefix = created["obj_id"]["prefix"]

        update_data["obj_id"] = {"prefix": prefix, "numeric": numeric}

        # Try to update as a different user
        client2, _ = register_user("user_update_wrong", "user_update_wrong@example.com")
        response = client2.put(f"{endpoint}/{numeric}", json=update_data)
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

    def test_delete_with_wrong_user_returns_404(
        self,
        test_client: TestClient,
        resource_config: dict[str, Any],
        create_test_resource: Callable,
        register_user: Callable,
    ):
        """Deleting a resource created by another user should return 404."""
        resource_name = resource_config["resource_name"]
        endpoint = resource_config["endpoint"]

        # Create resource for default user
        created = create_test_resource(resource_name)
        numeric = created["obj_id"]["numeric"]

        # Try to delete as a different user
        client2, _ = register_user("user_del_wrong", "user_del_wrong@example.com")
        response = client2.delete(f"{endpoint}/{numeric}")
        assert response.status_code == 404

        # Verify it still exists for original user
        get_response = test_client.get(f"{endpoint}/{numeric}")
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
