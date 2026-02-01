# Campaign execution models for tracking what happens during gameplay sessions.
from enum import Enum
from typing import ClassVar

from pydantic import BaseModel

from . import planning


class ExecutionStatus(str, Enum):
    NOT_ENCOUNTERED = "not_encountered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class RefinementMode(str, Enum):
    NARRATIVE = "narrative"
    STRUCTURED = "structured"


class ExecutionEntry(BaseModel):
    entity_id: planning.ID
    entity_type: str = ""
    status: ExecutionStatus = ExecutionStatus.NOT_ENCOUNTERED
    raw_notes: str = ""
    refined_notes: str = ""


class CampaignExecution(planning.Object):
    _default_prefix: ClassVar[str] = "EX"
    campaign_plan_id: planning.ID = planning.ID(prefix="CampPlan", numeric=0)
    title: str = ""
    session_date: str = ""
    raw_session_notes: str = ""
    refined_session_notes: str = ""
    refinement_mode: RefinementMode = RefinementMode.NARRATIVE
    entries: list[ExecutionEntry] = []
