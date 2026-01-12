"""Tests for the content API."""

import pytest

from campaign_master.content import api as content_api
from campaign_master.content import planning
from campaign_master.content.database import transaction


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
            assert prefix not in taken_prefixes, (
                f"Duplicate prefix '{prefix}' found in {ObjectType.__name__}"
            )
            taken_prefixes.add(prefix)


class TestDatabaseOperations:
    """Tests that require database access."""

    def test_transaction_rollback(self, db_session):
        """Test that failed transactions roll back properly."""
        with pytest.raises(ValueError):
            with transaction() as session:
                obj = content_api.create_object(
                    planning.Rule, session=session, auto_commit=False
                )
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
            rule1 = content_api.create_object(
                planning.Rule, session=session, auto_commit=False
            )
            rule2 = content_api.create_object(
                planning.Rule, session=session, auto_commit=False
            )
            assert rule1.obj_id != rule2.obj_id

        all_rules = content_api.retrieve_objects(planning.Rule)
        assert len(all_rules) == 2

    def test_error_handling_in_update(self, db_session):
        """Test that database errors in update are properly handled."""
        invalid_rule = planning.Rule(
            obj_id=planning.ID(prefix="R", numeric=99999)
        )
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
