from unittest import TestCase

from campaign_master.content import api as content_api
from campaign_master.content import database, planning


def get_all_object_types() -> list[type[planning.Object]]:
    """Retrieve all subclasses of planning.Object."""
    object_types = []

    def recurse_subclasses(cls):
        for subclass in cls.__subclasses__():
            object_types.append(subclass)
            recurse_subclasses(subclass)

    recurse_subclasses(planning.Object)
    return [planning.Object] + object_types


class ContentTestCase(TestCase):

    def test_unique_object_prefixes(self):
        all_objects: list[type[planning.Object]] = get_all_object_types()
        taken_prefixes = set()
        for ObjectType in all_objects:
            prefix = ObjectType._default_prefix
            self.assertNotIn(
                prefix,
                taken_prefixes,
                f"Duplicate prefix '{prefix}' found in {ObjectType.__name__}",
            )
            taken_prefixes.add(prefix)


class DBTestCase(TestCase):

    def setUp(self) -> None:
        # Drop all tables and recreate for test isolation
        from campaign_master.content.models import Base

        Base.metadata.drop_all(database.engine)
        database.create_db_and_tables()
        database.create_example_data()

    def test_transaction_rollback(self):
        """Test that failed transactions roll back properly."""
        from campaign_master.content.database import transaction

        with self.assertRaises(ValueError):
            with transaction() as session:
                # Create an object
                obj = content_api.create_object(
                    planning.Rule, session=session, auto_commit=False
                )
                # Verify it exists in session
                self.assertIsNotNone(obj)
                # Force an error
                raise ValueError("Simulated error")

        # Verify rollback - object should not exist in DB
        all_rules = content_api.retrieve_objects(planning.Rule)
        self.assertEqual(len(all_rules), 0)

    def test_nested_operations_atomic(self):
        """Test that multi-step operations are atomic."""
        # This should create both ID and object in one transaction
        rule = content_api.create_object(planning.Rule)

        # Verify object was created with valid ID
        self.assertTrue(rule.has_id())
        self.assertEqual(rule.obj_id.prefix, "R")
        self.assertGreater(rule.obj_id.numeric, 0)

        # Verify we can retrieve all rules and find our rule
        all_rules = content_api.retrieve_objects(planning.Rule)
        self.assertGreaterEqual(len(all_rules), 1)
        found = any(r.obj_id == rule.obj_id for r in all_rules)
        self.assertTrue(found, "Created rule should be retrievable")

    def test_manual_transaction_grouping(self):
        """Test manual transaction grouping."""
        from campaign_master.content.database import transaction

        with transaction() as session:
            # Create multiple objects in one transaction
            rule1 = content_api.create_object(
                planning.Rule, session=session, auto_commit=False
            )
            rule2 = content_api.create_object(
                planning.Rule, session=session, auto_commit=False
            )
            # Verify objects have different IDs
            self.assertNotEqual(rule1.obj_id, rule2.obj_id)
        # Commit happens at end of context manager

        # Verify both exist after transaction completes
        all_rules = content_api.retrieve_objects(planning.Rule)
        self.assertEqual(len(all_rules), 2)

    def test_error_handling_in_update(self):
        """Test that database errors in update are properly handled."""
        # Try to update with invalid ID - should raise error
        invalid_rule = planning.Rule(obj_id=planning.ID(prefix="R", numeric=99999)) # type: ignore[arg-type]
        with self.assertRaises(ValueError) as context:
            content_api.update_object(invalid_rule)
        self.assertIn("not found", str(context.exception))

    def test_error_handling_in_delete(self):
        """Test that delete handles non-existent objects correctly."""
        # Try to delete non-existent object
        invalid_id = planning.ID(prefix="R", numeric=99999)
        result = content_api.delete_object(invalid_id)
        self.assertFalse(result)

        # Create and delete an object
        rule = content_api.create_object(planning.Rule)
        self.assertTrue(rule.has_id())
        result = content_api.delete_object(rule.obj_id)
        self.assertTrue(result)

        # Verify it's gone
        retrieved = content_api.retrieve_object(rule.obj_id)
        self.assertIsNone(retrieved)

    def test_create_object(self):
        for ObjectType in [
            ObjectType
            for ObjectType in get_all_object_types()
            if ObjectType is not planning.Object
        ]:
            with self.subTest(ObjectType=ObjectType.__name__):
                obj = content_api.create_object(ObjectType)
                self.assertIsInstance(obj, ObjectType)
                self.assertIsInstance(obj.obj_id, planning.ID)


if __name__ == "__main__":
    test_case = DBTestCase()
    try:
        test_case.setUp()
        test_case.test_create_object()
    finally:
        test_case.tearDown()
