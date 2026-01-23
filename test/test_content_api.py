"""Tests for the content API."""

import pytest
from sqlalchemy import func, select

from campaign_master.content import api as content_api
from campaign_master.content import planning
from campaign_master.content.database import get_session_factory, transaction
from campaign_master.content.models import ObjectID


def get_all_object_types() -> list[type[planning.Object]]:
    """Retrieve all subclasses of planning.Object."""
    object_types = []

    def recurse_subclasses(cls):
        for subclass in cls.__subclasses__():
            object_types.append(subclass)
            recurse_subclasses(subclass)

    recurse_subclasses(planning.Object)
    return [planning.Object] + object_types


class TestContentValidation:
    """Tests that don't require a database."""

    def test_unique_object_prefixes(self):
        """Ensure all object types have unique prefixes."""
        all_objects: list[type[planning.Object]] = get_all_object_types()
        taken_prefixes = set()
        for ObjectType in all_objects:
            prefix = ObjectType._default_prefix
            assert prefix not in taken_prefixes, f"Duplicate prefix '{prefix}' found in {ObjectType.__name__}"
            taken_prefixes.add(prefix)


class TestDatabaseOperations:
    """Tests that require database access."""

    def test_transaction_rollback(self, db_session):
        """Test that failed transactions roll back properly."""
        with pytest.raises(ValueError):
            with transaction() as session:
                obj = content_api.create_object(planning.Rule, session=session, auto_commit=False)
                assert obj is not None
                raise ValueError("Simulated error")

        all_rules = content_api.retrieve_objects(planning.Rule)
        assert len(all_rules) == 0

    def test_nested_operations_atomic(self, db_session):
        """Test that multi-step operations are atomic."""
        rule = content_api.create_object(planning.Rule)

        assert rule.has_id()
        assert rule.obj_id.prefix == "R"
        assert rule.obj_id.numeric > 0

        all_rules = content_api.retrieve_objects(planning.Rule)
        assert len(all_rules) >= 1
        assert any(r.obj_id == rule.obj_id for r in all_rules)

    def test_manual_transaction_grouping(self, db_session):
        """Test manual transaction grouping."""
        with transaction() as session:
            rule1 = content_api.create_object(planning.Rule, session=session, auto_commit=False)
            rule2 = content_api.create_object(planning.Rule, session=session, auto_commit=False)
            assert rule1.obj_id != rule2.obj_id

        all_rules = content_api.retrieve_objects(planning.Rule)
        assert len(all_rules) == 2

    def test_error_handling_in_update(self, db_session):
        """Test that database errors in update are properly handled."""
        invalid_rule = planning.Rule(obj_id=planning.ID(prefix="R", numeric=99999))
        with pytest.raises(ValueError, match="not found"):
            content_api.update_object(invalid_rule)

    def test_error_handling_in_delete(self, db_session):
        """Test that delete handles non-existent objects correctly."""
        invalid_id = planning.ID(prefix="R", numeric=99999)
        result = content_api.delete_object(invalid_id)
        assert result is False

        rule = content_api.create_object(planning.Rule)
        assert rule.has_id()
        result = content_api.delete_object(rule.obj_id)
        assert result is True

        retrieved = content_api.retrieve_object(rule.obj_id)
        assert retrieved is None

    @pytest.mark.parametrize(
        "ObjectType",
        [ot for ot in get_all_object_types() if ot is not planning.Object],
    )
    def test_create_object(self, db_session, ObjectType):
        """Test creating each object type."""
        obj = content_api.create_object(ObjectType)
        assert isinstance(obj, ObjectType)
        assert isinstance(obj.obj_id, planning.ID)


class TestNoDuplicateObjectIDs:
    """
    Tests to verify that creating objects does not generate duplicate ObjectIDs.

    This was a bug where from_pydantic() methods called ObjectID.from_pydantic()
    multiple times, causing duplicate IDs to be created in the database.
    """

    def _count_object_ids_with_prefix(self, prefix: str, proto_user_id: int = 0) -> int:
        """Count ObjectID rows with a specific prefix."""
        session = get_session_factory()()
        try:
            count = session.execute(
                select(func.count(ObjectID.id)).where(
                    ObjectID.prefix == prefix,
                    ObjectID.proto_user_id == proto_user_id,
                )
            ).scalar()
            return count or 0
        finally:
            session.close()

    def _get_total_object_id_count(self) -> int:
        """Get total count of all ObjectID rows."""
        session = get_session_factory()()
        try:
            count = session.execute(select(func.count(ObjectID.id))).scalar()
            return count or 0
        finally:
            session.close()

    @pytest.mark.parametrize(
        "ObjectType",
        [ot for ot in get_all_object_types() if ot is not planning.Object],
    )
    def test_single_object_creates_single_id(self, db_session, ObjectType):
        """Test that creating one object creates exactly one ObjectID."""
        prefix = ObjectType._default_prefix

        # Verify no IDs exist before creation
        initial_count = self._count_object_ids_with_prefix(prefix)
        assert initial_count == 0, f"Expected 0 IDs with prefix {prefix}, got {initial_count}"

        # Create the object
        obj = content_api.create_object(ObjectType)
        assert obj.has_id()
        assert obj.obj_id.prefix == prefix

        # Verify exactly one ID was created
        final_count = self._count_object_ids_with_prefix(prefix)
        assert final_count == 1, (
            f"Expected exactly 1 ObjectID with prefix {prefix} after creating one {ObjectType.__name__}, "
            f"but found {final_count}. This indicates duplicate ID generation."
        )

    def test_point_creation_no_duplicate_ids(self, db_session):
        """Test Point creation specifically (the originally reported bug)."""
        # Create a Point
        point = content_api.create_object(planning.Point)
        assert point.has_id()
        assert point.obj_id.prefix == "P"
        assert point.obj_id.numeric == 1

        # Verify only one ObjectID with prefix "P" exists
        count = self._count_object_ids_with_prefix("P")
        assert count == 1, f"Expected 1 Point ID, found {count}"

        # Create another Point
        point2 = content_api.create_object(planning.Point)
        assert point2.obj_id.numeric == 2

        # Verify exactly 2 ObjectIDs with prefix "P" exist
        count = self._count_object_ids_with_prefix("P")
        assert count == 2, f"Expected 2 Point IDs, found {count}"

    def test_point_with_objective_reference_no_duplicate_ids(self, db_session):
        """Test Point with objective reference doesn't create duplicate IDs."""
        # Create an Objective first
        objective = content_api.create_object(planning.Objective)
        obj_count = self._count_object_ids_with_prefix("O")
        assert obj_count == 1, f"Expected 1 Objective ID, found {obj_count}"

        # Create a Point that references the Objective using save_object
        point_id = content_api.generate_id(prefix="P", proto_user_id=0)
        point = planning.Point(obj_id=point_id, name="Test Point", description="Test", objective=objective.obj_id)
        saved_point = content_api.save_object(point, proto_user_id=0)
        point_count = self._count_object_ids_with_prefix("P")
        assert point_count == 1, f"Expected 1 Point ID, found {point_count}"

        # Objective count should still be 1
        obj_count = self._count_object_ids_with_prefix("O")
        assert obj_count == 1, f"Expected 1 Objective ID after Point creation, found {obj_count}"

    def test_segment_with_point_references_no_duplicate_ids(self, db_session):
        """Test Segment with start/end point references doesn't create duplicate IDs."""
        # Create two Points
        start_point = content_api.create_object(planning.Point)
        end_point = content_api.create_object(planning.Point)
        point_count = self._count_object_ids_with_prefix("P")
        assert point_count == 2, f"Expected 2 Point IDs, found {point_count}"

        # Create a Segment referencing the Points using save_object
        segment_id = content_api.generate_id(prefix="S", proto_user_id=0)
        segment = planning.Segment(
            obj_id=segment_id,
            name="Test Segment",
            description="Test",
            start=start_point.obj_id,
            end=end_point.obj_id,
        )
        saved_segment = content_api.save_object(segment, proto_user_id=0)
        segment_count = self._count_object_ids_with_prefix("S")
        assert segment_count == 1, f"Expected 1 Segment ID, found {segment_count}"

        # Point count should still be 2
        point_count = self._count_object_ids_with_prefix("P")
        assert point_count == 2, f"Expected 2 Point IDs after Segment creation, found {point_count}"

    def test_character_with_inventory_no_duplicate_ids(self, db_session):
        """Test Character with inventory items doesn't create duplicate IDs."""
        # Create some Items
        item1 = content_api.create_object(planning.Item)
        item2 = content_api.create_object(planning.Item)
        item_count = self._count_object_ids_with_prefix("I")
        assert item_count == 2, f"Expected 2 Item IDs, found {item_count}"

        # Create a Character with inventory using save_object
        char_id = content_api.generate_id(prefix="C", proto_user_id=0)
        character = planning.Character(
            obj_id=char_id,
            name="Test Character",
            role="NPC",
            backstory="Test backstory",
            inventory=[item1.obj_id, item2.obj_id],
        )
        saved_char = content_api.save_object(character, proto_user_id=0)
        char_count = self._count_object_ids_with_prefix("C")
        assert char_count == 1, f"Expected 1 Character ID, found {char_count}"

        # Item count should still be 2
        item_count = self._count_object_ids_with_prefix("I")
        assert item_count == 2, f"Expected 2 Item IDs after Character creation, found {item_count}"

    def test_character_with_storylines_no_duplicate_ids(self, db_session):
        """Test Character with storyline arcs doesn't create duplicate IDs."""
        # Create an Arc
        arc = content_api.create_object(planning.Arc)
        arc_count = self._count_object_ids_with_prefix("A")
        assert arc_count == 1, f"Expected 1 Arc ID, found {arc_count}"

        # Create a Character with storylines using save_object
        char_id = content_api.generate_id(prefix="C", proto_user_id=0)
        character = planning.Character(
            obj_id=char_id,
            name="Test Character",
            role="NPC",
            backstory="Test backstory",
            storylines=[arc.obj_id],
        )
        saved_char = content_api.save_object(character, proto_user_id=0)
        char_count = self._count_object_ids_with_prefix("C")
        assert char_count == 1, f"Expected 1 Character ID, found {char_count}"

        # Arc count should still be 1
        arc_count = self._count_object_ids_with_prefix("A")
        assert arc_count == 1, f"Expected 1 Arc ID after Character creation, found {arc_count}"

    def test_objective_with_prerequisites_no_duplicate_ids(self, db_session):
        """Test Objective with prerequisites doesn't create duplicate IDs."""
        # Create prerequisite Objectives
        prereq1 = content_api.create_object(planning.Objective)
        prereq2 = content_api.create_object(planning.Objective)
        obj_count = self._count_object_ids_with_prefix("O")
        assert obj_count == 2, f"Expected 2 Objective IDs, found {obj_count}"

        # Create an Objective with prerequisites using save_object
        obj_id = content_api.generate_id(prefix="O", proto_user_id=0)
        objective = planning.Objective(
            obj_id=obj_id,
            description="Test Objective",
            prerequisites=[prereq1.obj_id, prereq2.obj_id],
        )
        saved_obj = content_api.save_object(objective, proto_user_id=0)
        obj_count = self._count_object_ids_with_prefix("O")
        assert obj_count == 3, f"Expected 3 Objective IDs, found {obj_count}"

    def test_location_with_neighbors_no_duplicate_ids(self, db_session):
        """Test Location with neighboring locations doesn't create duplicate IDs."""
        # Create neighbor Locations
        neighbor1 = content_api.create_object(planning.Location)
        neighbor2 = content_api.create_object(planning.Location)
        loc_count = self._count_object_ids_with_prefix("L")
        assert loc_count == 2, f"Expected 2 Location IDs, found {loc_count}"

        # Create a Location with neighbors using save_object
        loc_id = content_api.generate_id(prefix="L", proto_user_id=0)
        location = planning.Location(
            obj_id=loc_id,
            name="Test Location",
            description="Test",
            neighboring_locations=[neighbor1.obj_id, neighbor2.obj_id],
        )
        saved_loc = content_api.save_object(location, proto_user_id=0)
        loc_count = self._count_object_ids_with_prefix("L")
        assert loc_count == 3, f"Expected 3 Location IDs, found {loc_count}"

    def test_multiple_objects_sequential_ids_no_gaps(self, db_session):
        """Test that creating multiple objects produces sequential IDs without gaps."""
        # Create 5 Rules
        rules = [content_api.create_object(planning.Rule) for _ in range(5)]

        # Verify sequential numeric IDs
        for i, rule in enumerate(rules, start=1):
            assert rule.obj_id.numeric == i, f"Expected numeric ID {i}, got {rule.obj_id.numeric}"

        # Verify exactly 5 ObjectIDs with prefix "R"
        count = self._count_object_ids_with_prefix("R")
        assert count == 5, f"Expected 5 Rule IDs, found {count}"

    def test_save_object_no_duplicate_ids(self, db_session):
        """Test that save_object (used by web API) doesn't create duplicate IDs."""
        # This simulates what the web API does: generate ID then save object
        obj_id = content_api.generate_id(prefix="P", proto_user_id=0)
        point = planning.Point(obj_id=obj_id, name="Test Point", description="Test")

        # Save the object (this is what web API endpoints do)
        saved = content_api.save_object(point, proto_user_id=0)
        assert saved.obj_id == obj_id

        # Verify exactly one ObjectID with prefix "P" exists
        count = self._count_object_ids_with_prefix("P")
        assert count == 1, f"Expected 1 Point ID after save_object, found {count}"

    def test_save_multiple_objects_no_duplicate_ids(self, db_session):
        """Test saving multiple objects via save_object doesn't create duplicates."""
        # Simulate multiple web API create requests
        for i in range(3):
            obj_id = content_api.generate_id(prefix="P", proto_user_id=0)
            point = planning.Point(obj_id=obj_id, name=f"Point {i+1}", description="Test")
            content_api.save_object(point, proto_user_id=0)

        # Verify exactly 3 ObjectIDs with prefix "P"
        count = self._count_object_ids_with_prefix("P")
        assert count == 3, f"Expected 3 Point IDs, found {count}"

    def test_total_object_id_count_matches_created_objects(self, db_session):
        """Test that total ObjectID count matches the number of objects created."""
        initial_count = self._get_total_object_id_count()
        assert initial_count == 0

        # Create various objects
        content_api.create_object(planning.Rule)
        content_api.create_object(planning.Point)
        content_api.create_object(planning.Character)
        content_api.create_object(planning.Item)
        content_api.create_object(planning.Location)

        # Verify total count is exactly 5
        total_count = self._get_total_object_id_count()
        assert total_count == 5, f"Expected 5 total ObjectIDs, found {total_count}"
