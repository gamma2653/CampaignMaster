# Abstract content, such as the class definitions for Campaign, Character, Item, Location, etc.
import re
from typing import Optional, ClassVar, Any, TYPE_CHECKING
from pydantic import BaseModel, Field, field_validator, PrivateAttr, model_validator
from ..util import get_basic_logger

# To avoid circular imports
# if TYPE_CHECKING:
#     from ..content.api import IDService

logger = get_basic_logger(__name__)

id_pattern = re.compile(r"^([a-zA-Z]+)-(\d+)$")

DEFAULT_ID_PREFIX = "MISC"

IDDef = {
    "numeric": int,
    "prefix": DEFAULT_ID_PREFIX,
}


class ID(BaseModel):
    """
    Group 1: Prefix (e.g., "R", "O", etc.)
    Group 2: Numeric part (e.g., "1", "2", etc.)
    """

    numeric: int
    prefix: str = DEFAULT_ID_PREFIX

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
    def from_str(cls, id_str: str) -> "ID":
        if not isinstance(id_str, str):
            return id_str
        match = id_pattern.match(id_str)
        if not match:
            raise ValueError(f"Invalid ID format: {id_str}")
        prefix, numeric_str = match.groups()
        numeric = int(numeric_str)
        return cls(prefix=prefix, numeric=numeric)

    @model_validator(mode="before")
    @classmethod
    def validate_id(cls, values: Any) -> Any:
        if isinstance(values, str):
            return cls.from_str(values)
        return values

    @field_validator("prefix", mode="after")
    @classmethod
    def valid_prefix(cls, v: str) -> str:
        if not v.isalpha():
            raise ValueError(f"Invalid prefix: {v}. Must be letters only.")
        return v

    def __hash__(self) -> int:
        return hash((self.prefix, self.numeric))


class Object(BaseModel):
    """
    Base class for all objects in the campaign planning system.
    """

    obj_id: Optional[ID] = None

    _default_prefix: ClassVar[str] = DEFAULT_ID_PREFIX
    # _id_service: IDService = PrivateAttr()

    # @property
    # def id_service(self) -> IDService:
    #     if not self._id_service:
    #         # Warn and set default
    #         from ..content.api import IDService
    #         logger.error("IDService not set. Creating new instance for validation engine.")
    #         self._id_service = IDService()
    #     return self._id_service

    @model_validator(mode="before")
    @classmethod
    def try_coerce_id(cls, data: Any) -> Any:
        # Lazy load generate_id to avoid circular imports
        if isinstance(data, dict):
            if not data.get("obj_id"):
                from . import api as content_api
                id_ = content_api.ObjectID.generate_id(prefix=cls._default_prefix)
                return {**data, "obj_id": id_.to_pydantic()}
            if isinstance(data.get("obj_id"), str):
                return {**data, "obj_id": ID.from_str(data["obj_id"]).model_dump()}
        return data

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.obj_id})"


class Rule(Object):
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


class Objective(Object):
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

    prerequisites: list[ID] = []
    """
    A list of prerequisites that must be met before the objective can be attempted.
    This may include other objectives, character levels, items, or other conditions.
    """


class Point(Object):
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


class Segment(Object):
    _default_prefix: ClassVar[str] = "S"
    name: str = ""
    """
    The name of the story segment.
    """
    description: str = ""
    """
    A textual description of the story segment.
    """
    # Poetically, the start and end are always defined. (non-optional)
    start: Point = Field(default_factory=Point)
    """
    The starting point of the segment.
    """
    end: Point = Field(default_factory=Point)
    """
    The ending point of the segment.
    """


class Arc(Object):
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


class Item(Object):
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


class Character(Object):
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


class Location(Object):
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


class CampaignPlan(Object):
    """
    A class to represent a campaign plan, loaded from a JSON file.
    """

    _default_prefix: ClassVar[str] = "CampPlan"
    title: str = ""
    version: str = ""
    setting: str = ""
    summary: str = ""
    storypoints: list[Arc] = []
    characters: list[Character] = []
    locations: list[Location] = []
    items: list[Item] = []
    rules: list[Rule] = []
    objectives: list[Objective] = []
