# Abstract content, such as the class definitions for Campaign, Character, Item, Location, etc.
import sys
import json

if sys.version_info < (3, 12):
    from typing_extensions import TypedDict, NotRequired, NewType, TypeVar
else:
    from typing import TypedDict, NotRequired, NewType, TypeVar


from pydantic import TypeAdapter


from . import planning



class Campaign(TypedDict):
    plan: planning.CampaignPlan

_Campaign = TypeAdapter(Campaign)
