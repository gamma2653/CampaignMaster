# Abstract content, such as the class definitions for Campaign, Character, Item, Location, etc.
import sys
import json

if sys.version_info < (3, 12):
    from typing_extensions import TypedDict, NotRequired, NewType, TypeVar, Annotated
else:
    from typing import TypedDict, NotRequired, NewType, TypeVar, Annotated


from pydantic import TypeAdapter, StringConstraints

from .ids import ID, RuleID, ObjectiveID, PointID, SegmentID, ArcID, ItemID, CharacterID, LocationID, PlanID


class AbstractObject(TypedDict):
    id: ID

class Rule(AbstractObject):
    """
    A class to represent a single rule in a tabletop RPG campaign.
    """
    id: RuleID
    description: str
    effect: str
    components: list[str]

class Objective(AbstractObject):
    """
    A class to represent a single objective in a campaign plan.
    """
    id: ObjectiveID
    description: str
    components: list[str]
    prerequisites: list[str]

class Point(AbstractObject):
    id: PointID
    name: str
    description: str
    objective: NotRequired[ObjectiveID]


class Segment(AbstractObject):
    id: SegmentID
    name: str
    description: str
    points: list[Point]


class Arc(AbstractObject):
    id: ArcID
    name: str
    description: str
    segments: list[Segment]


class Item(AbstractObject):
    id: ItemID
    name: str
    type_: str
    description: str
    properties: dict[str, str]


class Character(AbstractObject):
    id: CharacterID
    name: str
    role: str
    backstory: str
    attributes: dict[str, int]
    skills: dict[str, int]
    storylines: list[ArcID | SegmentID | PointID]
    inventory: list[ItemID]


class Location(AbstractObject):
    id: LocationID
    name: str
    description: str
    neighboring_locations: list[LocationID]
    coords: NotRequired[
        tuple[float, float] | tuple[float, float, float]
    ]  # (latitude, longitude, [altitude])


class CampaignPlan(AbstractObject):
    """
    A class to represent a campaign plan, loaded from a JSON file.
    """
    id: PlanID
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

IDTypeToObjectTypeMap = {
    ID: AbstractObject,  # Does this case make sense?
    RuleID: Rule,
    ObjectiveID: Objective,
    PointID: Point,
    SegmentID: Segment,
    ArcID: Arc,
    ItemID: Item,
    CharacterID: Character,
    LocationID: Location,
    PlanID: CampaignPlan,
}

# _Rule = TypeAdapter(Rule)
# _Objective = TypeAdapter(Objective)
# _Point = TypeAdapter(Point)
# _Segment = TypeAdapter(Segment)
# _Arc = TypeAdapter(Arc)
# _Item = TypeAdapter(Item)
# _Character = TypeAdapter(Character)
# _Location = TypeAdapter(Location)
_CampaignPlan: TypeAdapter[CampaignPlan] = TypeAdapter(CampaignPlan) # type: ignore[arg-type]


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
