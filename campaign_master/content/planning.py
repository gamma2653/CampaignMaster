# Abstract content, such as the class definitions for Campaign, Character, Item, Location, etc.

import re
from typing import Annotated, Any, NewType, Optional, TypeVar, ClassVar, cast
from collections import Counter
from pydantic import BaseModel, StringConstraints

from .locking import ReaderWriterSuite

ID = NewType("ID", tuple[str, int])
"""
Group 1: Prefix (e.g., "R", "O", etc.)
Group 2: Numeric part (e.g., "001", "002", etc.)
"""

RuleID = Annotated[ID, StringConstraints(min_length=3, pattern=r"R-\d+")]
ObjectiveID = Annotated[ID, StringConstraints(min_length=3, pattern=r"O-\d+")]
PointID = Annotated[ID, StringConstraints(min_length=3, pattern=r"P-\d+")]
SegmentID = Annotated[ID, StringConstraints(min_length=3, pattern=r"S-\d+")]
ArcID = Annotated[ID, StringConstraints(min_length=3, pattern=r"A-\d+")]
ItemID = Annotated[ID, StringConstraints(min_length=3, pattern=r"I-\d+")]
CharacterID = Annotated[ID, StringConstraints(min_length=3, pattern=r"C-\d+")]
LocationID = Annotated[ID, StringConstraints(min_length=3, pattern=r"L-\d+")]
PlanID = Annotated[ID, StringConstraints(min_length=9, pattern=r"CamPlan-\d+")]
# Devolved ID, for generic use (e.g., temporary objects, misc objects, etc.)
GenericID = Annotated[ID, StringConstraints(min_length=3, pattern=r"[A-z]+-\d+")]

IDS_ANNOTATED: set[Annotated] = {GenericID, RuleID, ObjectiveID, PointID, SegmentID, ArcID, ItemID, CharacterID, LocationID, PlanID}


_CURRENT_IDS: Counter = Counter()
"""
Global counter to keep track of the current highest ID number for each prefix.
Keyed by prefix (e.g., "P", "R", "O", etc.) to the highest number used.
"""
_RELEASED_IDS: dict[str, set[ID]] = {}
"""
A set to keep track of released IDs for reuse.
Keyed by prefix (e.g., "P", "R", "O", etc.) to sets of IDs.
"""
_CURRENT_IDS_LOCK = ReaderWriterSuite()
"""
A lock to manage concurrent access to _CURRENT_IDS and _RELEASED_IDS.
"""

class AbstractObject(BaseModel):
    """
    Base class for all objects in the campaign planning system.
    """
    obj_id: GenericID

    @classmethod
    def id_type(cls) -> Annotated:
        obj_id_annotation = cls.model_fields.get("obj_id")
        if obj_id_annotation is None:
            return GenericID
        return obj_id_annotation.annotation

    # Bootstrap ID if not provided
    def __init__(self, **data):
        if "obj_id" not in data:
            data["obj_id"] = generate_id_from_type(self.__class__.id_type())
        super().__init__(**data)

class Rule(AbstractObject):
    """
    A class to represent a single rule in a tabletop RPG campaign.
    """
    _id_type = RuleID
    obj_id: RuleID
    description: str
    effect: str
    components: list[str]

class Objective(AbstractObject):
    """
    A class to represent a single objective in a campaign plan.
    """
    _id_type = ObjectiveID
    obj_id: ObjectiveID
    description: str
    components: list[str]
    prerequisites: list[str]

class Point(AbstractObject):
    _id_type = PointID
    obj_id: PointID
    name: str
    description: str
    objective: Optional[ObjectiveID]


class Segment(AbstractObject):
    _id_type = SegmentID
    obj_id: SegmentID
    name: str
    description: str
    points: list[Point]


class Arc(AbstractObject):
    _id_type = ArcID
    obj_id: ArcID
    name: str
    description: str
    segments: list[Segment]


class Item(AbstractObject):
    _id_type = ItemID
    obj_id: ItemID
    name: str
    type_: str
    description: str
    properties: dict[str, str]


class Character(AbstractObject):
    _id_type = CharacterID
    obj_id: CharacterID
    name: str
    role: str
    backstory: str
    attributes: dict[str, int]
    skills: dict[str, int]
    storylines: list[ArcID | SegmentID | PointID]
    inventory: list[ItemID]


class Location(AbstractObject):
    _id_type = LocationID
    obj_id: LocationID
    name: str
    description: str
    neighboring_locations: list[LocationID]
    coords: Optional[
        tuple[float, float] | tuple[float, float, float]
    ]  # (latitude, longitude[, altitude])


class CampaignPlan(AbstractObject):
    """
    A class to represent a campaign plan, loaded from a JSON file.
    """
    _id_type = PlanID
    obj_id: PlanID
    title: str
    version: str
    setting: str
    summary: str
    storypoints: list[Arc]
    npcs: list[Character]
    locations: list[Location]
    items: list[Item]
    rules: list[Rule]



def pattern_from_annotated(id_type) -> re.Pattern:
    try:
        return re.compile(id_type.__metadata__[0].pattern)
    except (AttributeError, IndexError):
        raise ValueError(f"Type {id_type} is not an Annotated ID type with StringConstraints")

"""
Generic type variable for ID types.
"""
def _prefix_from_type(id_type) -> str:
    """
    Get the prefix string for a given ID type.

    Args:
        id_type (type[ID]): The ID type (e.g., RuleID, ObjectiveID).
    Returns:
        str: The prefix string (e.g., "R" for RuleID).
    """
    if id_type not in IDS_ANNOTATED:
        raise ValueError(f"Unknown ID type: {id_type}")
    try:
        return id_type.__metadata__[0].pattern.split('-')[0]
    except (AttributeError, IndexError):
        # Not an Annotated type, or StringConstraints is not the first element, assume it's the base ID type
        return "MISC"  # Unknown prefix, aka category

IDType = TypeVar("IDType")
def generate_id_from_type(id_type: Annotated[IDType, Any]) -> IDType:
    """
    Generate a new ID based on the given ID type.

    Args:
        id_type (type[ID]): The ID type (e.g., RuleID, ObjectiveID).

    Returns:
        ID: A new unique ID of the specified type.
    """
    # Retrieve prefix from type, then generate ID, then cast to type
    return cast(IDType, generate_id(_prefix_from_type(id_type)))

def generate_id(prefix: str) -> ID:
    """
    Generate a new ID with the given prefix.

    Args:
        prefix (str): The prefix for the ID (e.g., "R" for Rule).

    Returns:
        ID: A new unique ID with the specified prefix.
    """
    with _CURRENT_IDS_LOCK.writer():
        if prefix not in _RELEASED_IDS:
            _RELEASED_IDS[prefix] = set()
        if _RELEASED_IDS[prefix]:
            new_id = _RELEASED_IDS[prefix].pop()
            return new_id
        _CURRENT_IDS[prefix] += 1
        id = ID((prefix, _CURRENT_IDS[prefix]))  # NOTE: Unbounded integer IDs
    return id


def release_id(id: ID):
    """
    Release an ID back to the factory for reuse.
    """
    match = pattern_from_annotated(id).match(id)
    if not match:
        raise ValueError(f"Invalid ID format: {id}")
    prefix = match.group(1)
    with _CURRENT_IDS_LOCK.writer():
        if prefix not in _RELEASED_IDS:
            _RELEASED_IDS[prefix] = set()
        _RELEASED_IDS[prefix].add(id)

def get_released_ids(prefix: str) -> set[ID]:
    """
    Get the set of released IDs for a given prefix.
    """
    with _CURRENT_IDS_LOCK.reader():
        return _RELEASED_IDS.get(prefix, set())
