"""Tests for cross-resource relationships in the web API."""

from typing import Callable

import pytest
from fastapi.testclient import TestClient


class TestPointObjectiveRelationship:
    """Tests for Point-Objective relationships."""

    def test_create_point_with_objective_reference(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """A Point can reference an Objective."""
        # Create an objective first
        objective = create_test_resource("objective")
        objective_id = objective["obj_id"]

        # Create a point that references the objective
        point_data = {
            "name": "Point with Objective",
            "description": "This point references an objective",
            "objective": {"prefix": objective_id["prefix"], "numeric": objective_id["numeric"]},
        }

        response = test_client.post("/api/campaign/p", json=point_data)
        assert response.status_code == 200

        result = response.json()
        assert result["objective"] is not None
        assert result["objective"]["prefix"] == objective_id["prefix"]
        assert result["objective"]["numeric"] == objective_id["numeric"]

    def test_update_point_objective_reference(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """A Point's objective reference can be updated."""
        # Create two objectives
        objective1 = create_test_resource("objective")
        objective2 = create_test_resource("objective")

        # Create a point with first objective
        point_data = {
            "name": "Point",
            "description": "Test point",
            "objective": {
                "prefix": objective1["obj_id"]["prefix"],
                "numeric": objective1["obj_id"]["numeric"],
            },
        }
        response = test_client.post("/api/campaign/p", json=point_data)
        point = response.json()

        # Update to second objective
        update_data = {
            "obj_id": point["obj_id"],
            "name": "Updated Point",
            "description": "Updated description",
            "objective": {
                "prefix": objective2["obj_id"]["prefix"],
                "numeric": objective2["obj_id"]["numeric"],
            },
        }
        response = test_client.put(f"/api/campaign/p/{point['obj_id']['numeric']}", json=update_data)
        assert response.status_code == 200

        result = response.json()
        assert result["objective"]["numeric"] == objective2["obj_id"]["numeric"]


class TestSegmentPointRelationship:
    """Tests for Segment-Point relationships."""

    def test_create_segment_with_point_references(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """A Segment can reference start and end Points."""
        # Create two points
        point1 = create_test_resource("point")
        point2 = create_test_resource("point")

        # Create a segment with start and end points
        segment_data = {
            "name": "Test Segment",
            "description": "A segment with points",
            "start": {
                "prefix": point1["obj_id"]["prefix"],
                "numeric": point1["obj_id"]["numeric"],
            },
            "end": {
                "prefix": point2["obj_id"]["prefix"],
                "numeric": point2["obj_id"]["numeric"],
            },
        }

        response = test_client.post("/api/campaign/s", json=segment_data)
        assert response.status_code == 200

        result = response.json()
        assert result["start"]["numeric"] == point1["obj_id"]["numeric"]
        assert result["end"]["numeric"] == point2["obj_id"]["numeric"]

    def test_update_segment_point_references(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """A Segment's start and end points can be updated."""
        # Create three points
        point1 = create_test_resource("point")
        point2 = create_test_resource("point")
        point3 = create_test_resource("point")

        # Create segment with first two points
        segment_data = {
            "name": "Test Segment",
            "description": "A segment",
            "start": {"prefix": "P", "numeric": point1["obj_id"]["numeric"]},
            "end": {"prefix": "P", "numeric": point2["obj_id"]["numeric"]},
        }
        response = test_client.post("/api/campaign/s", json=segment_data)
        segment = response.json()

        # Update end point to third point
        update_data = {
            "obj_id": segment["obj_id"],
            "name": "Updated Segment",
            "description": "Updated segment",
            "start": {"prefix": "P", "numeric": point1["obj_id"]["numeric"]},
            "end": {"prefix": "P", "numeric": point3["obj_id"]["numeric"]},
        }
        response = test_client.put(f"/api/campaign/s/{segment['obj_id']['numeric']}", json=update_data)
        assert response.status_code == 200

        result = response.json()
        assert result["end"]["numeric"] == point3["obj_id"]["numeric"]


class TestArcSegmentRelationship:
    """Tests for Arc-Segment relationships."""

    def test_create_arc_with_embedded_segments(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """An Arc can contain embedded Segment objects."""
        # Create points for segments
        point1 = create_test_resource("point")
        point2 = create_test_resource("point")

        # Create a segment first to get a valid ID
        segment = create_test_resource(
            "segment",
            {
                "name": "Segment for Arc",
                "description": "Test segment",
                "start": {"prefix": "P", "numeric": point1["obj_id"]["numeric"]},
                "end": {"prefix": "P", "numeric": point2["obj_id"]["numeric"]},
            },
        )

        # Create an arc with embedded segment
        arc_data = {
            "name": "Test Arc",
            "description": "An arc with segments",
            "segments": [
                {
                    "obj_id": segment["obj_id"],
                    "name": segment["name"],
                    "description": segment["description"],
                    "start": segment["start"],
                    "end": segment["end"],
                }
            ],
        }

        response = test_client.post("/api/campaign/a", json=arc_data)
        assert response.status_code == 200

        result = response.json()
        assert len(result["segments"]) == 1
        assert result["segments"][0]["obj_id"]["numeric"] == segment["obj_id"]["numeric"]


class TestCharacterItemRelationship:
    """Tests for Character-Item (inventory) relationships."""

    def test_create_character_with_inventory(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """A Character can have items in inventory."""
        # Create items
        item1 = create_test_resource("item")
        item2 = create_test_resource("item")

        # Create character with inventory
        character_data = {
            "name": "Character with Items",
            "role": "Hero",
            "backstory": "A character with items",
            "attributes": {"strength": 10},
            "skills": {"combat": 5},
            "storylines": [],
            "inventory": [
                {"prefix": item1["obj_id"]["prefix"], "numeric": item1["obj_id"]["numeric"]},
                {"prefix": item2["obj_id"]["prefix"], "numeric": item2["obj_id"]["numeric"]},
            ],
        }

        response = test_client.post("/api/campaign/c", json=character_data)
        assert response.status_code == 200

        result = response.json()
        assert len(result["inventory"]) == 2
        inventory_numerics = [i["numeric"] for i in result["inventory"]]
        assert item1["obj_id"]["numeric"] in inventory_numerics
        assert item2["obj_id"]["numeric"] in inventory_numerics

    def test_update_character_inventory(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """A Character's inventory can be updated."""
        # Create items
        item1 = create_test_resource("item")
        item2 = create_test_resource("item")
        item3 = create_test_resource("item")

        # Create character with first two items
        character_data = {
            "name": "Character",
            "role": "Hero",
            "backstory": "Test",
            "attributes": {},
            "skills": {},
            "storylines": [],
            "inventory": [
                {"prefix": "I", "numeric": item1["obj_id"]["numeric"]},
                {"prefix": "I", "numeric": item2["obj_id"]["numeric"]},
            ],
        }
        response = test_client.post("/api/campaign/c", json=character_data)
        character = response.json()

        # Update inventory to only third item
        update_data = {
            "obj_id": character["obj_id"],
            "name": "Updated Character",
            "role": "Updated Hero",
            "backstory": "Updated",
            "attributes": {},
            "skills": {},
            "storylines": [],
            "inventory": [
                {"prefix": "I", "numeric": item3["obj_id"]["numeric"]},
            ],
        }
        response = test_client.put(f"/api/campaign/c/{character['obj_id']['numeric']}", json=update_data)
        assert response.status_code == 200

        result = response.json()
        assert len(result["inventory"]) == 1
        assert result["inventory"][0]["numeric"] == item3["obj_id"]["numeric"]


class TestCharacterStorylineRelationship:
    """Tests for Character-Arc (storyline) relationships."""

    def test_create_character_with_storylines(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """A Character can have storyline arcs."""
        # Create an arc
        arc = create_test_resource("arc")

        # Create character with storyline
        character_data = {
            "name": "Character with Storylines",
            "role": "Protagonist",
            "backstory": "Main character",
            "attributes": {},
            "skills": {},
            "storylines": [
                {"prefix": arc["obj_id"]["prefix"], "numeric": arc["obj_id"]["numeric"]},
            ],
            "inventory": [],
        }

        response = test_client.post("/api/campaign/c", json=character_data)
        assert response.status_code == 200

        result = response.json()
        assert len(result["storylines"]) == 1
        assert result["storylines"][0]["numeric"] == arc["obj_id"]["numeric"]


class TestObjectivePrerequisiteRelationship:
    """Tests for Objective-Objective (prerequisite) relationships."""

    def test_create_objective_with_prerequisites(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """An Objective can have prerequisite Objectives."""
        # Create prerequisite objectives
        prereq1 = create_test_resource("objective")
        prereq2 = create_test_resource("objective")

        # Create objective with prerequisites
        objective_data = {
            "description": "Objective with Prerequisites",
            "components": ["component1"],
            "prerequisites": [
                {"prefix": prereq1["obj_id"]["prefix"], "numeric": prereq1["obj_id"]["numeric"]},
                {"prefix": prereq2["obj_id"]["prefix"], "numeric": prereq2["obj_id"]["numeric"]},
            ],
        }

        response = test_client.post("/api/campaign/o", json=objective_data)
        assert response.status_code == 200

        result = response.json()
        assert len(result["prerequisites"]) == 2
        prereq_numerics = [p["numeric"] for p in result["prerequisites"]]
        assert prereq1["obj_id"]["numeric"] in prereq_numerics
        assert prereq2["obj_id"]["numeric"] in prereq_numerics

    def test_objective_prerequisite_chain(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """Objectives can form prerequisite chains."""
        # Create chain: obj3 requires obj2, obj2 requires obj1
        obj1 = create_test_resource(
            "objective",
            {"description": "First Objective", "components": [], "prerequisites": []},
        )

        obj2_data = {
            "description": "Second Objective",
            "components": [],
            "prerequisites": [{"prefix": "O", "numeric": obj1["obj_id"]["numeric"]}],
        }
        response = test_client.post("/api/campaign/o", json=obj2_data)
        obj2 = response.json()

        obj3_data = {
            "description": "Third Objective",
            "components": [],
            "prerequisites": [{"prefix": "O", "numeric": obj2["obj_id"]["numeric"]}],
        }
        response = test_client.post("/api/campaign/o", json=obj3_data)
        obj3 = response.json()

        # Verify chain
        assert len(obj3["prerequisites"]) == 1
        assert obj3["prerequisites"][0]["numeric"] == obj2["obj_id"]["numeric"]


class TestLocationNeighborRelationship:
    """Tests for Location-Location (neighbor) relationships."""

    def test_create_location_with_neighbors(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """A Location can have neighboring Locations."""
        # Create neighbor locations
        neighbor1 = create_test_resource("location")
        neighbor2 = create_test_resource("location")

        # Create location with neighbors
        location_data = {
            "name": "Central Location",
            "description": "A location with neighbors",
            "neighboring_locations": [
                {
                    "prefix": neighbor1["obj_id"]["prefix"],
                    "numeric": neighbor1["obj_id"]["numeric"],
                },
                {
                    "prefix": neighbor2["obj_id"]["prefix"],
                    "numeric": neighbor2["obj_id"]["numeric"],
                },
            ],
            "coords": (0.0, 0.0),
        }

        response = test_client.post("/api/campaign/l", json=location_data)
        assert response.status_code == 200

        result = response.json()
        assert len(result["neighboring_locations"]) == 2
        neighbor_numerics = [n["numeric"] for n in result["neighboring_locations"]]
        assert neighbor1["obj_id"]["numeric"] in neighbor_numerics
        assert neighbor2["obj_id"]["numeric"] in neighbor_numerics

    def test_bidirectional_neighbor_relationship(
        self,
        test_client: TestClient,
        create_test_resource: Callable,
    ):
        """Neighbor relationships can be set up bidirectionally."""
        # Create two locations
        loc1 = create_test_resource(
            "location",
            {
                "name": "Location 1",
                "description": "First location",
                "neighboring_locations": [],
                "coords": None,
            },
        )
        loc2_data = {
            "name": "Location 2",
            "description": "Second location",
            "neighboring_locations": [
                {"prefix": "L", "numeric": loc1["obj_id"]["numeric"]},
            ],
            "coords": None,
        }
        response = test_client.post("/api/campaign/l", json=loc2_data)
        loc2 = response.json()

        # Update loc1 to reference loc2
        update_data = {
            "obj_id": loc1["obj_id"],
            "name": "Location 1 Updated",
            "description": "First location updated",
            "neighboring_locations": [
                {"prefix": "L", "numeric": loc2["obj_id"]["numeric"]},
            ],
            "coords": None,
        }
        response = test_client.put(f"/api/campaign/l/{loc1['obj_id']['numeric']}", json=update_data)
        assert response.status_code == 200

        # Verify bidirectional relationship
        response1 = test_client.get(f"/api/campaign/l/{loc1['obj_id']['numeric']}")
        response2 = test_client.get(f"/api/campaign/l/{loc2['obj_id']['numeric']}")

        loc1_result = response1.json()
        loc2_result = response2.json()

        assert loc2["obj_id"]["numeric"] in [n["numeric"] for n in loc1_result["neighboring_locations"]]
        assert loc1["obj_id"]["numeric"] in [n["numeric"] for n in loc2_result["neighboring_locations"]]
