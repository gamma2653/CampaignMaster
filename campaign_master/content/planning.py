# Abstract content, such as the class definitions for Campaign, Character, Item, Location, etc.

import re
from typing import Optional, ClassVar, Annotated, Any
from collections import Counter
from pydantic import BaseModel, Field, model_validator, BeforeValidator

from .locking import ReaderWriterSuite

id_pattern = re.compile(r"^([a-zA-Z]+)-(\d+)$")

class ID(BaseModel):
    """
    Group 1: Prefix (e.g., "R", "O", etc.)
    Group 2: Numeric part (e.g., "1", "2", etc.)
    """
    numeric: int
    prefix: str = "MISC"

    _max_numeric_digits: ClassVar[int] = 6

    def __str__(self) -> str:
        return f"{self.prefix}-{self.numeric:0{self._max_numeric_digits}d}"
    
    def to_digits(self, max_digits: Optional[int] = None) -> int:
        """
        Get the numeric part of the ID, zero-padded to max_digits.
        """
        if max_digits is None:
            max_digits = self._max_numeric_digits
        return int(f"{self.numeric:0{max_digits}d}")

    @classmethod
    def from_str(cls, id_str: Any) -> Any:
        if not isinstance(id_str, str):
            return id_str
        match = id_pattern.match(id_str)
        if not match:
            raise ValueError(f"Invalid ID format: {id_str}")
        prefix, numeric_str = match.groups()
        numeric = int(numeric_str)
        return cls(prefix=prefix, numeric=numeric)

    @model_validator(mode="after")
    def valid_prefix(self) -> "ID":
        if not self.prefix.isalpha():
            raise ValueError(f"Invalid prefix: {self.prefix}. Must be letters only.")
        return self
    

    def __hash__(self) -> int:
        return hash((self.prefix, self.numeric))

ValidID = Annotated[ID, BeforeValidator(ID.from_str)]
# IDS_ANNOTATED: set[Annotated] = {GenericID, RuleID, ObjectiveID, PointID, SegmentID, ArcID, ItemID, CharacterID, LocationID, PlanID}


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
    obj_id: ValidID

    _default_prefix: ClassVar[str] = "MISC"

    
    # FIXME: This borked constructor type definition. See Segment class for example.
    # Bootstrap ID if not provided
    def __init__(self, **data):
        if "obj_id" not in data:
            data["obj_id"] = generate_id(self._default_prefix)
        super().__init__(**data)
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.obj_id})"

class Rule(AbstractObject):
    """
    A class to represent a single rule in a tabletop RPG campaign.
    """
    _default_prefix: ClassVar[str] = "R"
    description: str = ""
    """
    A textual description of the rule.
    """
    effect: str = ""
    """
    A description of the effect of the rule. This may include mechanical effects, narrative effects, or both.
    """
    components: list[str] = []
    """
    A list of components that make up the rule. This may include keywords, phrases, or other elements that define the rule.
    """

class Objective(AbstractObject):
    """
    A class to represent a single objective in a campaign plan.
    """
    _default_prefix: ClassVar[str] = "O"
    description: str = ""
    """
    A textual description of the objective.
    """
    components: list[str] = []
    """
    A list of components that make up the objective. This may include keywords, phrases, or other elements that define the objective.
    """

    prerequisites: list[str] = []
    """
    A list of prerequisites that must be met before the objective can be attempted.
    This may include other objectives, character levels, items, or other conditions.
    """

class Point(AbstractObject):
    _default_prefix: ClassVar[str] = "P"
    name: str = ""
    """
    The name of the story point.
    """
    description: str = ""
    """
    A textual description of the story point.
    """
    objective: Optional[ID] = None
    """
    An optional reference to an Objective ID associated with this point.
    """


class Segment(AbstractObject):
    _default_prefix: ClassVar[str] = "S"
    name: str = ""
    """
    The name of the story segment.
    """
    description: str = ""
    """
    A textual description of the story segment.
    """
    start: Point = Field(default_factory=Point)  # type: ignore[assignment]
    """
    The starting point of the segment.
    """
    end: Point = Field(default_factory=Point)  # type: ignore[assignment]
    """
    The ending point of the segment.
    """


class Arc(AbstractObject):
    _default_prefix: ClassVar[str] = "A"
    name: str = ""
    """
    The name of the story arc.
    """
    description: str = ""
    """
    A textual description of the story arc.
    """
    segments: list[Segment] = []
    """
    A list of segments that make up the story arc.
    """


class Item(AbstractObject):
    _default_prefix: ClassVar[str] = "I"
    name: str = ""
    """
    The name of the item.
    """
    type_: str = ""
    """
    The type of the item (e.g., weapon, armor, potion).
    """
    description: str = ""
    """
    A textual description of the item.
    """
    properties: dict[str, str] = {}
    """
    A dictionary of properties that define the item's attributes and miscellaneous properties.
    """


class Character(AbstractObject):
    _default_prefix: ClassVar[str] = "C"
    name: str = ""
    """
    The name of the character.
    """
    role: str = ""
    """
    The role of the character (e.g., hero, villain, NPC).
    """
    backstory: str = ""
    """
    A brief backstory for the character.
    """
    attributes: dict[str, int] = {}
    """
    A dictionary of attributes that define the character's capabilities (e.g., strength, intelligence).
    """
    skills: dict[str, int] = {}
    """
    A dictionary of skills that the character possesses (e.g., stealth, persuasion).
    """
    storylines: list[ID] = []
    """
    A list of storylines that the character is involved in.
    """
    inventory: list[ID] = []
    """
    A list of item IDs that the character possesses.
    """


class Location(AbstractObject):
    _default_prefix: ClassVar[str] = "L"
    name: str = ""
    """
    The name of the location.
    """
    description: str = ""
    """
    A textual description of the location.
    """
    neighboring_locations: list[ID] = []
    """
    A list of IDs of neighboring locations.
    """
    coords: Optional[
        tuple[float, float] | tuple[float, float, float]
    ]  # (latitude, longitude[, altitude])
    """
    The geographical coordinates of the location in-universe.
    NOTE: It is up to the CampaignPlan to define the coordinate system, via a Rule.
    """


class CampaignPlan(AbstractObject):
    """
    A class to represent a campaign plan, loaded from a JSON file.
    """
    _default_prefix: ClassVar[str] = "CampPlan"
    title: str = ""
    version: str = ""
    setting: str = ""
    summary: str = ""
    storypoints: list[Arc] = []
    npcs: list[Character] = []
    locations: list[Location] = []
    items: list[Item] = []
    rules: list[Rule] = []


def get_next_id_numeric(prefix: str) -> int:
    with _CURRENT_IDS_LOCK.writer():
        if prefix not in _RELEASED_IDS:
            _RELEASED_IDS[prefix] = set()
        if _RELEASED_IDS[prefix]:
            new_id = _RELEASED_IDS[prefix].pop()
            return new_id.numeric
        _CURRENT_IDS[prefix] += 1
        return _CURRENT_IDS[prefix]


def generate_id(prefix: str) -> ID:
    """
    Generate a new ID with the given prefix.

    Args:
        prefix (str): The prefix for the ID (e.g., "R" for Rule).

    Returns:
        ID: A new unique ID with the specified prefix.
    """
    return ID(prefix=prefix, numeric=get_next_id_numeric(prefix))

def release_id(id: ID):
    """
    Release an ID back to the factory for reuse.
    """
    with _CURRENT_IDS_LOCK.writer():
        if id.prefix not in _RELEASED_IDS:
            _RELEASED_IDS[id.prefix] = set()
        _RELEASED_IDS[id.prefix].add(id)

def get_released_ids(prefix: str) -> set[ID]:
    """
    Get the set of released IDs for a given prefix.
    """
    with _CURRENT_IDS_LOCK.reader():
        return _RELEASED_IDS.get(prefix, set())
