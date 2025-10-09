# Abstract content, such as the class definitions for Campaign, Character, Item, Location, etc.

from typing import Optional, TypeAlias

from pydantic import BaseModel

from .ids import ID, RuleID, ObjectiveID, PointID, SegmentID, ArcID, ItemID, CharacterID, LocationID, PlanID


class AbstractObject(BaseModel):
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
    objective: Optional[ObjectiveID]


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
    coords: Optional[
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


Object: TypeAlias = AbstractObject | Rule | Objective | Point | Segment | Arc | Item | Character | Location | CampaignPlan

IDTypeToObjectTypeMap = {
    ID: AbstractObject,
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


