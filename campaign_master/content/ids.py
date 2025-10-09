import sys
import re
from collections import Counter
from .locking import ReaderWriterSuite

if sys.version_info < (3, 12):
    from typing_extensions import Annotated, NewType, TypedDict, TypeVar, TypeAlias
else:
    from typing import Annotated, NewType, TypedDict, TypeVar, TypeAlias

from pydantic import StringConstraints

ID = NewType("ID", str)

GenericIDPattern = re.compile(r'([A-z]+)-(\d{4})')
"""
Group 1: Prefix (e.g., "R", "O", etc.)
Group 2: Numeric part (e.g., "0001", "0002", etc.)
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

IDS_ANNOTATED = {type[ID], type[RuleID], type[ObjectiveID], type[PointID], type[SegmentID], type[ArcID], type[ItemID], type[CharacterID], type[LocationID], type[PlanID]}


_CURRENT_IDS: Counter = Counter()
"""
Global counter to keep track of the current highest ID number for each prefix.
Keyed by prefix (e.g., "R", "O", etc.) to the highest number used.
"""
_RELEASED_IDS: dict[str, set[ID]] = {}
"""
A set to keep track of released IDs for reuse.
Keyed by prefix (e.g., "R", "O", etc.) to sets of IDs.
"""
_CURRENT_IDS_LOCK = ReaderWriterSuite()
"""
A lock to manage concurrent access to _CURRENT_IDS and _RELEASED_IDS.
"""


IDType = TypeVar("IDType", bound=ID)
"""
Generic type variable for ID types.
"""
IDTypeUnion: TypeAlias = type[ID] | type[RuleID] | type[ObjectiveID] | type[PointID] | type[SegmentID] | type[ArcID] | type[ItemID] | type[CharacterID] | type[LocationID] | type[PlanID]
"""
Union of all ID types.
"""
# FIXME: Due to IDTypeUnion being a union of types, while what will be passed are one of the above types, mypy is not happy.
# The reasons are complex, and outside the scope of this comment. Go study category theory.
def _prefix_from_type(id_type: IDTypeUnion) -> str:
    """
    Get the prefix string for a given ID type.

    Args:
        id_type (type[ID]): The ID type (e.g., RuleID, ObjectiveID).
    Returns:
        str: The prefix string (e.g., "R" for RuleID).
    """
    if id_type not in IDS_ANNOTATED:
        raise ValueError(f"Unknown ID type: {id_type}")
    return id_type.__metadata__[0]['pattern'].split('-')[0]

def generate_id_from_type(id_type: type[IDType]) -> IDType:
    """
    Generate a new ID based on the given ID type.

    Args:
        id_type (type[ID]): The ID type (e.g., RuleID, ObjectiveID).

    Returns:
        ID: A new unique ID of the specified type.
    """
    return id_type(generate_id(_prefix_from_type(id_type)))

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
        id = ID(f"{prefix}{_CURRENT_IDS[prefix]:04d}")
    return id


def release_id(id: ID):
    """
    Release an ID back to the factory for reuse.
    """
    match = GenericIDPattern.match(id)
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



# TYPE_TO_ID_GENERATOR = {
#     "rule": generate_rule_id,
#     "objective": generate_objective_id,
#     "point": generate_point_id,
#     "segment": generate_segment_id,
#     "arc": generate_arc_id,
#     "item": generate_item_id,
#     "plan": generate_plan_id,
# }



