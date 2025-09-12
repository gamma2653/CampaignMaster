# Abstract content, such as the class definitions for Campaign, Character, Item, Location, etc.
import sys
import json

if sys.version_info < (3, 12):
    from typing_extensions import TypedDict, NotRequired, NewType, TypeVar, Annotated
else:
    from typing import TypedDict, NotRequired, NewType, TypeVar, Annotated


from pydantic import TypeAdapter, StringConstraints

ID = NewType("ID", str)

class AbstractObject(TypedDict):
    id: NotRequired[ID]

RuleID = Annotated[ID, StringConstraints(min_length=3, pattern=r"R-\d+")]
class Rule(AbstractObject):
    """
    A class to represent a single rule in a tabletop RPG campaign.
    """
    id: NotRequired[RuleID]  # Auto-generated if not provided
    description: str
    effect: str
    components: list[str]

ObjectiveID = Annotated[ID, StringConstraints(min_length=3, pattern=r"O-\d+")]
class Objective(TypedDict):
    """
    A class to represent a single objective in a campaign plan.
    """
    id: NotRequired[ObjectiveID]  # Auto-generated if not provided
    description: str
    components: list[str]
    prerequisites: list[str]

PointID = Annotated[ID, StringConstraints(min_length=3, pattern=r"P-\d+")]
class Point(TypedDict):
    id: NotRequired[PointID]  # Auto-generated if not provided
    name: str
    description: str
    objective: NotRequired[ObjectiveID]


SegmentID = Annotated[ID, StringConstraints(min_length=3, pattern=r"S-\d+")]
class Segment(TypedDict):
    id: NotRequired[SegmentID]  # Auto-generated if not provided
    name: str
    description: str
    points: list[Point]


ArcID = Annotated[ID, StringConstraints(min_length=3, pattern=r"A-\d+")]
class Arc(TypedDict):
    id: NotRequired[ArcID]  # Auto-generated if not provided
    name: str
    description: str
    segments: list[Segment]


ItemID = Annotated[ID, StringConstraints(min_length=3, pattern=r"I-\d+")]
class Item(TypedDict):
    id: NotRequired[ItemID]  # Auto-generated if not provided
    name: str
    type_: str
    description: str
    properties: dict[str, str]


CharacterID = Annotated[ID, StringConstraints(min_length=3, pattern=r"C-\d+")]
class Character(TypedDict):
    id: NotRequired[CharacterID]  # Auto-generated if not provided
    name: str
    role: str
    backstory: str
    attributes: dict[str, int]
    skills: dict[str, int]
    storylines: list[ArcID | SegmentID | PointID]
    inventory: list[ItemID]


LocationID = Annotated[ID, StringConstraints(min_length=3, pattern=r"L-\d+")]
class Location(TypedDict):
    id: NotRequired[LocationID]  # Auto-generated if not provided
    name: str
    description: str
    neighboring_locations: list[LocationID]
    coords: NotRequired[
        tuple[float, float] | tuple[float, float, float]
    ]  # (latitude, longitude, [altitude])


class CampaignPlan(TypedDict):
    """
    A class to represent a campaign plan, loaded from a JSON file.
    """
    title: str
    version: str
    setting: str
    summary: str
    storypoints: list[Arc]
    npcs: list[Character]
    locations: list[Location]
    items: list[Item]
    rules: list[Rule]


ObjectType = AbstractObject | Rule | Objective | Point | Segment | Arc | Item | Character | Location | CampaignPlan

# _Rule = TypeAdapter(Rule)
# _Objective = TypeAdapter(Objective)
# _Point = TypeAdapter(Point)
# _Segment = TypeAdapter(Segment)
# _Arc = TypeAdapter(Arc)
# _Item = TypeAdapter(Item)
# _Character = TypeAdapter(Character)
# _Location = TypeAdapter(Location)
_CampaignPlan = TypeAdapter(CampaignPlan)


Object = TypeVar("Object", bound=ObjectType)
def load_obj(dict_type: TypeAdapter[Object], file_path: str) -> Object:
    """
    Load a TypedDict object from a JSON file and validate it using the provided TypeAdapter.

    Parameters
    ----------
    dict_type : TypeAdapter
        The TypeAdapter for the TypedDict to be loaded.
    file_path : str
        The path to the JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return dict_type.validate_json(file.read())
