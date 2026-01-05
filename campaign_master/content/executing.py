# Abstract content, such as the class definitions for Campaign, Character, Item, Location, etc.
from pydantic import BaseModel

from . import planning


class Campaign(BaseModel):
    plan: planning.CampaignPlan
