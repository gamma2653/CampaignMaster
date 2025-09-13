# Rationale: https://stackoverflow.com/a/6738456
# - Bullet #3, centralization for consistency

from collections import Counter
from .planning import ID, RuleID, ObjectiveID, PointID, SegmentID, ArcID, ItemID, PlanID

# TODO: Fix arbitrary limits and error handling
# Could use UUIDs instead, but less human-friendly,
#  which won't be good for ListView elements


class _IDFactory(Counter):
    """
    A factory to generate unique IDs for different object types.
    """
    FIELD_NAME_TO_GENERATOR = {
        "rule": "generate_rule_id",
        "objective": "generate_objective_id",
        "point": "generate_point_id",
        "segment": "generate_segment_id",
        "arc": "generate_arc_id",
        "item": "generate_item_id",
        "campaignplan": "generate_plan_id",
    }

    def __init__(self):
        super().__init__()

    def from_field_name(self, field_name: str) -> ID:
        """
        Generate a new ID based on the field name.

        Args:
            field_name (str): The name of the field (e.g., "rule", "objective").

        Returns:
            ID: A new unique ID for the specified field type.

        Raises:
            ValueError: If the field name is not recognized.
        """
        generator_method_name = self.FIELD_NAME_TO_GENERATOR.get(field_name.lower())
        if not generator_method_name:
            raise ValueError(f"Unknown field name '{field_name}' for ID generation.")
        generator_method = getattr(self, generator_method_name)
        return generator_method()

    def generate_id(self, prefix: str) -> ID:
        """
        Generate a new unique ID with the given prefix.
        """
        self[prefix] += 1
        new_id = f"{prefix}-{self[prefix]:03d}"
        if self[prefix] > 999:
            raise ValueError(f"ID limit reached for prefix '{prefix}' (>999)")
        return ID(new_id)
    
    def generate_rule_id(self) -> RuleID:
        return ID(self.generate_id("R"))
    
    def generate_objective_id(self) -> ObjectiveID:
        return ID(self.generate_id("O"))
    
    def generate_point_id(self) -> PointID:
        return ID(self.generate_id("P"))
    
    def generate_segment_id(self) -> SegmentID:
        return ID(self.generate_id("S"))
    
    def generate_arc_id(self) -> ArcID:
        return ID(self.generate_id("A"))
    
    def generate_item_id(self) -> ItemID:
        return ID(self.generate_id("I"))
    
    def generate_plan_id(self) -> PlanID:
        return ID(self.generate_id("CamPlan"))
    
    
# Singleton instance of the IDFactory
ID_FACTORY = _IDFactory()

