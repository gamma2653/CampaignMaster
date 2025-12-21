import sys
from unittest import TestCase
from PySide6 import QtWidgets
from campaign_master.content import planning, api as content_api

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
            self.assertNotIn(prefix, taken_prefixes, f"Duplicate prefix '{prefix}' found in {ObjectType.__name__}")
            taken_prefixes.add(prefix)


class DBTestCase(TestCase):

    def setUp(self) -> None:
        content_api.create_db_and_tables()
        content_api.create_example_data()

    def test_generate_and_retrieve_ids(self):
        generated_ids: dict[str, planning.ID] = {}
        # Use prefixes from Object class (cls._default_prefix)
        prefixes = {obj_type._default_prefix for obj_type in get_all_object_types()}
        for prefix in prefixes:
            new_id = content_api.generate_id(prefix=prefix)
            self.assertEqual(new_id.prefix, prefix)
            generated_ids[prefix] = new_id
        # Retrieve and verify
        for prefix, gen_id in generated_ids.items():
            retrieved_ids = content_api.retrieve_ids(prefix=prefix)
            self.assertIn(gen_id, retrieved_ids)
    
    def test_generate_and_retrieve_ids_proto_user(self):
        proto_user_id = 42
        generated_ids: dict[str, planning.ID] = {}
        prefixes = {obj_type._default_prefix for obj_type in get_all_object_types()}
        for prefix in prefixes:
            new_id = content_api.generate_id(prefix=prefix, proto_user_id=proto_user_id)
            self.assertEqual(new_id.prefix, prefix)
            generated_ids[prefix] = new_id
        # Retrieve and verify
        for prefix, gen_id in generated_ids.items():
            retrieved_ids = content_api.retrieve_ids(prefix=prefix, proto_user_id=proto_user_id)
            self.assertIn(gen_id, retrieved_ids)
        for prefix, gen_id in generated_ids.items():
            retrieved_ids_global = content_api.retrieve_ids(prefix=prefix, proto_user_id=0)
            self.assertNotIn(gen_id, retrieved_ids_global)

    def test_create_object(self):
        for ObjectType in [ObjectType for ObjectType in get_all_object_types() if ObjectType is not planning.Object]:
            with self.subTest(ObjectType=ObjectType):
                print(f"Testing creation of object type: {ObjectType.__name__}")
                obj = content_api.create_object(ObjectType)
                self.assertIsInstance(obj, ObjectType)
                self.assertIsInstance(obj.obj_id, planning.ID)
            break  # Limit to one test per run for debugging


if __name__ == "__main__":
    test_case = DBTestCase()
    try:
        test_case.setUp()
        test_case.test_create_object()
    finally:
        test_case.tearDown()


