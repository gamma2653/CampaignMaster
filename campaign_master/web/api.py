from typing import cast

import fastapi
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.engine import Engine

from ..content import api as content_api_functions
from ..content import database as content_api
from ..content import planning
from ..content.database import transaction
from ..content.models import AuthUser
from .auth import get_authenticated_user

router = fastapi.APIRouter()


# Pydantic models for API request/response
class PointCreate(BaseModel):
    name: str
    description: str
    objective: dict | None = None  # {prefix: str, numeric: int}


class PointUpdate(BaseModel):
    obj_id: dict  # {prefix: str, numeric: int}
    name: str
    description: str
    objective: dict | None = None


class PointResponse(BaseModel):
    obj_id: dict
    name: str
    description: str
    objective: dict | None


# Point CRUD endpoints
@router.get("/campaign/p", response_model=list[PointResponse])
def list_points(user: AuthUser = Depends(get_authenticated_user)):
    """List all points for a user."""
    proto_user_id = user.proto_user_id
    try:
        points = content_api_functions.retrieve_objects(obj_type=planning.Point, proto_user_id=proto_user_id)
        points = cast(list[planning.Point], points)
        return [
            {
                "obj_id": {"prefix": p.obj_id.prefix, "numeric": p.obj_id.numeric},
                "name": p.name,
                "description": p.description,
                "objective": ({"prefix": p.objective.prefix, "numeric": p.objective.numeric} if p.objective else None),
            }
            for p in points
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/p/{numeric}", response_model=PointResponse)
def get_point(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Get a specific point by ID."""
    proto_user_id = user.proto_user_id
    try:
        point_id = planning.ID(prefix="P", numeric=numeric)
        point = content_api_functions.retrieve_object(obj_id=point_id, proto_user_id=proto_user_id)
        point = cast(planning.Point | None, point)
        if not point:
            raise HTTPException(status_code=404, detail="Point not found")

        return {
            "obj_id": {"prefix": point.obj_id.prefix, "numeric": point.obj_id.numeric},
            "name": point.name,
            "description": point.description,
            "objective": (
                {"prefix": point.objective.prefix, "numeric": point.objective.numeric} if point.objective else None
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/p", response_model=PointResponse)
def create_point(point_data: PointCreate, user: AuthUser = Depends(get_authenticated_user)):
    """Create a new point."""
    proto_user_id = user.proto_user_id
    try:
        # Use single transaction for ID generation and object save
        with transaction() as session:
            # Generate new ID
            new_id = content_api_functions.generate_id(
                prefix="P", proto_user_id=proto_user_id, session=session, auto_commit=False
            )

            # Create objective ID if provided
            objective_id = None
            if point_data.objective:
                objective_id = planning.ID(
                    prefix=point_data.objective["prefix"],
                    numeric=point_data.objective["numeric"],
                )

            # Create Point object
            new_point = planning.Point(
                obj_id=new_id,  # type: ignore[arg-type]
                name=point_data.name,
                description=point_data.description,
                objective=objective_id,
            )

            # Save to database (in same transaction)
            created_point = content_api_functions.save_object(
                obj=new_point, proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            created_point = cast(planning.Point, created_point)

        return {
            "obj_id": {
                "prefix": created_point.obj_id.prefix,
                "numeric": created_point.obj_id.numeric,
            },
            "name": created_point.name,
            "description": created_point.description,
            "objective": (
                {
                    "prefix": created_point.objective.prefix,
                    "numeric": created_point.objective.numeric,
                }
                if created_point.objective
                else None
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaign/p/{numeric}", response_model=PointResponse)
def update_point(numeric: int, point_data: PointUpdate, user: AuthUser = Depends(get_authenticated_user)):
    """Update an existing point."""
    proto_user_id = user.proto_user_id
    try:
        # Verify point exists
        point_id = planning.ID(prefix="P", numeric=numeric)
        existing_point = content_api_functions.retrieve_object(obj_id=point_id, proto_user_id=proto_user_id)
        if not existing_point:
            raise HTTPException(status_code=404, detail="Point not found")

        # Create objective ID if provided
        objective_id = None
        if point_data.objective:
            objective_id = planning.ID(
                prefix=point_data.objective["prefix"],
                numeric=point_data.objective["numeric"],
            )

        # Create updated Point object
        updated_point = planning.Point(
            obj_id=point_id,  # type: ignore[arg-type]
            name=point_data.name,
            description=point_data.description,
            objective=objective_id,
        )

        # Update in database
        result = content_api_functions.update_object(obj=updated_point, proto_user_id=proto_user_id)
        result = cast(planning.Point, result)

        return {
            "obj_id": {
                "prefix": result.obj_id.prefix,
                "numeric": result.obj_id.numeric,
            },
            "name": result.name,
            "description": result.description,
            "objective": (
                {"prefix": result.objective.prefix, "numeric": result.objective.numeric} if result.objective else None
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaign/p/{numeric}")
def delete_point(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Delete a point."""
    proto_user_id = user.proto_user_id
    try:
        point_id = planning.ID(prefix="P", numeric=numeric)
        success = content_api_functions.delete_object(obj_id=point_id, proto_user_id=proto_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Point not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Objective list endpoint for dropdown
@router.get("/campaign/o")
def list_objectives(user: AuthUser = Depends(get_authenticated_user)):
    """List all objectives for a user."""
    proto_user_id = user.proto_user_id
    try:
        objectives = content_api_functions.retrieve_objects(obj_type=planning.Objective, proto_user_id=proto_user_id)
        objectives = cast(list[planning.Objective], objectives)
        return [
            {
                "obj_id": {"prefix": o.obj_id.prefix, "numeric": o.obj_id.numeric},
                "description": o.description,
                "components": o.components,
                "prerequisites": [{"prefix": p.prefix, "numeric": p.numeric} for p in o.prerequisites],
            }
            for o in objectives
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/id_service")
def id_service(id_type: str = "misc", service: str | None = None):
    """
    Simple ID service endpoint that returns a new unique ID.
    """
    if not service:
        service = "planning"

    # Determine prefix based on id_type
    # Implementation pending


# ============== Rule CRUD ==============
class RuleCreate(BaseModel):
    description: str = ""
    effect: str = ""
    components: list[str] = []


class RuleUpdate(BaseModel):
    obj_id: dict
    description: str = ""
    effect: str = ""
    components: list[str] = []


class RuleResponse(BaseModel):
    obj_id: dict
    description: str
    effect: str
    components: list[str]


@router.get("/campaign/r", response_model=list[RuleResponse])
def list_rules(user: AuthUser = Depends(get_authenticated_user)):
    """List all rules for a user."""
    proto_user_id = user.proto_user_id
    try:
        rules = content_api_functions.retrieve_objects(obj_type=planning.Rule, proto_user_id=proto_user_id)
        rules = cast(list[planning.Rule], rules)
        return [
            {
                "obj_id": {"prefix": r.obj_id.prefix, "numeric": r.obj_id.numeric},
                "description": r.description,
                "effect": r.effect,
                "components": r.components,
            }
            for r in rules
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/r/{numeric}", response_model=RuleResponse)
def get_rule(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Get a specific rule by ID."""
    proto_user_id = user.proto_user_id
    try:
        rule_id = planning.ID(prefix="R", numeric=numeric)
        rule = content_api_functions.retrieve_object(obj_id=rule_id, proto_user_id=proto_user_id)
        rule = cast(planning.Rule | None, rule)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        return {
            "obj_id": {"prefix": rule.obj_id.prefix, "numeric": rule.obj_id.numeric},
            "description": rule.description,
            "effect": rule.effect,
            "components": rule.components,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/r", response_model=RuleResponse)
def create_rule(rule_data: RuleCreate, user: AuthUser = Depends(get_authenticated_user)):
    """Create a new rule."""
    proto_user_id = user.proto_user_id
    try:
        with transaction() as session:
            new_id = content_api_functions.generate_id(
                prefix="R", proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            new_rule = planning.Rule(
                obj_id=new_id,  # type: ignore[arg-type]
                description=rule_data.description,
                effect=rule_data.effect,
                components=rule_data.components,
            )
            created_rule = content_api_functions.save_object(
                obj=new_rule, proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            created_rule = cast(planning.Rule, created_rule)
        return {
            "obj_id": {"prefix": created_rule.obj_id.prefix, "numeric": created_rule.obj_id.numeric},
            "description": created_rule.description,
            "effect": created_rule.effect,
            "components": created_rule.components,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaign/r/{numeric}", response_model=RuleResponse)
def update_rule(numeric: int, rule_data: RuleUpdate, user: AuthUser = Depends(get_authenticated_user)):
    """Update an existing rule."""
    proto_user_id = user.proto_user_id
    try:
        rule_id = planning.ID(prefix="R", numeric=numeric)
        existing_rule = content_api_functions.retrieve_object(obj_id=rule_id, proto_user_id=proto_user_id)
        if not existing_rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        updated_rule = planning.Rule(
            obj_id=rule_id,  # type: ignore[arg-type]
            description=rule_data.description,
            effect=rule_data.effect,
            components=rule_data.components,
        )
        result = content_api_functions.update_object(obj=updated_rule, proto_user_id=proto_user_id)
        result = cast(planning.Rule, result)
        return {
            "obj_id": {"prefix": result.obj_id.prefix, "numeric": result.obj_id.numeric},
            "description": result.description,
            "effect": result.effect,
            "components": result.components,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaign/r/{numeric}")
def delete_rule(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Delete a rule."""
    proto_user_id = user.proto_user_id
    try:
        rule_id = planning.ID(prefix="R", numeric=numeric)
        success = content_api_functions.delete_object(obj_id=rule_id, proto_user_id=proto_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Rule not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Objective CRUD (extending existing list) ==============
class ObjectiveCreate(BaseModel):
    description: str = ""
    components: list[str] = []
    prerequisites: list[dict] = []  # list of {prefix, numeric}


class ObjectiveUpdate(BaseModel):
    obj_id: dict
    description: str = ""
    components: list[str] = []
    prerequisites: list[dict] = []


class ObjectiveResponse(BaseModel):
    obj_id: dict
    description: str
    components: list[str]
    prerequisites: list[dict]


@router.get("/campaign/o/{numeric}", response_model=ObjectiveResponse)
def get_objective(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Get a specific objective by ID."""
    proto_user_id = user.proto_user_id
    try:
        obj_id = planning.ID(prefix="O", numeric=numeric)
        objective = content_api_functions.retrieve_object(obj_id=obj_id, proto_user_id=proto_user_id)
        objective = cast(planning.Objective | None, objective)
        if not objective:
            raise HTTPException(status_code=404, detail="Objective not found")
        return {
            "obj_id": {"prefix": objective.obj_id.prefix, "numeric": objective.obj_id.numeric},
            "description": objective.description,
            "components": objective.components,
            "prerequisites": [{"prefix": p.prefix, "numeric": p.numeric} for p in objective.prerequisites],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/o", response_model=ObjectiveResponse)
def create_objective(obj_data: ObjectiveCreate, user: AuthUser = Depends(get_authenticated_user)):
    """Create a new objective."""
    proto_user_id = user.proto_user_id
    try:
        with transaction() as session:
            new_id = content_api_functions.generate_id(
                prefix="O", proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            prereqs = [planning.ID(prefix=p["prefix"], numeric=p["numeric"]) for p in obj_data.prerequisites]
            new_obj = planning.Objective(
                obj_id=new_id,  # type: ignore[arg-type]
                description=obj_data.description,
                components=obj_data.components,
                prerequisites=prereqs,
            )
            created = content_api_functions.save_object(
                obj=new_obj, proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            created = cast(planning.Objective, created)
        return {
            "obj_id": {"prefix": created.obj_id.prefix, "numeric": created.obj_id.numeric},
            "description": created.description,
            "components": created.components,
            "prerequisites": [{"prefix": p.prefix, "numeric": p.numeric} for p in created.prerequisites],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaign/o/{numeric}", response_model=ObjectiveResponse)
def update_objective(numeric: int, obj_data: ObjectiveUpdate, user: AuthUser = Depends(get_authenticated_user)):
    """Update an existing objective."""
    proto_user_id = user.proto_user_id
    try:
        obj_id = planning.ID(prefix="O", numeric=numeric)
        existing = content_api_functions.retrieve_object(obj_id=obj_id, proto_user_id=proto_user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Objective not found")
        prereqs = [planning.ID(prefix=p["prefix"], numeric=p["numeric"]) for p in obj_data.prerequisites]
        updated = planning.Objective(
            obj_id=obj_id,  # type: ignore[arg-type]
            description=obj_data.description,
            components=obj_data.components,
            prerequisites=prereqs,
        )
        result = content_api_functions.update_object(obj=updated, proto_user_id=proto_user_id)
        result = cast(planning.Objective, result)
        return {
            "obj_id": {"prefix": result.obj_id.prefix, "numeric": result.obj_id.numeric},
            "description": result.description,
            "components": result.components,
            "prerequisites": [{"prefix": p.prefix, "numeric": p.numeric} for p in result.prerequisites],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaign/o/{numeric}")
def delete_objective(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Delete an objective."""
    proto_user_id = user.proto_user_id
    try:
        obj_id = planning.ID(prefix="O", numeric=numeric)
        success = content_api_functions.delete_object(obj_id=obj_id, proto_user_id=proto_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Objective not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Segment CRUD ==============
class SegmentCreate(BaseModel):
    name: str = ""
    description: str = ""
    start: dict  # {prefix, numeric}
    end: dict  # {prefix, numeric}


class SegmentUpdate(BaseModel):
    obj_id: dict
    name: str = ""
    description: str = ""
    start: dict
    end: dict


class SegmentResponse(BaseModel):
    obj_id: dict
    name: str
    description: str
    start: dict
    end: dict


@router.get("/campaign/s", response_model=list[SegmentResponse])
def list_segments(user: AuthUser = Depends(get_authenticated_user)):
    """List all segments for a user."""
    proto_user_id = user.proto_user_id
    try:
        segments = content_api_functions.retrieve_objects(obj_type=planning.Segment, proto_user_id=proto_user_id)
        segments = cast(list[planning.Segment], segments)
        return [
            {
                "obj_id": {"prefix": s.obj_id.prefix, "numeric": s.obj_id.numeric},
                "name": s.name,
                "description": s.description,
                "start": {"prefix": s.start.prefix, "numeric": s.start.numeric},
                "end": {"prefix": s.end.prefix, "numeric": s.end.numeric},
            }
            for s in segments
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/s/{numeric}", response_model=SegmentResponse)
def get_segment(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Get a specific segment by ID."""
    proto_user_id = user.proto_user_id
    try:
        seg_id = planning.ID(prefix="S", numeric=numeric)
        segment = content_api_functions.retrieve_object(obj_id=seg_id, proto_user_id=proto_user_id)
        segment = cast(planning.Segment | None, segment)
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        return {
            "obj_id": {"prefix": segment.obj_id.prefix, "numeric": segment.obj_id.numeric},
            "name": segment.name,
            "description": segment.description,
            "start": {"prefix": segment.start.prefix, "numeric": segment.start.numeric},
            "end": {"prefix": segment.end.prefix, "numeric": segment.end.numeric},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/s", response_model=SegmentResponse)
def create_segment(seg_data: SegmentCreate, user: AuthUser = Depends(get_authenticated_user)):
    """Create a new segment."""
    proto_user_id = user.proto_user_id
    try:
        with transaction() as session:
            new_id = content_api_functions.generate_id(
                prefix="S", proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            start_id = planning.ID(prefix=seg_data.start["prefix"], numeric=seg_data.start["numeric"])
            end_id = planning.ID(prefix=seg_data.end["prefix"], numeric=seg_data.end["numeric"])
            new_seg = planning.Segment(
                obj_id=new_id,  # type: ignore[arg-type]
                name=seg_data.name,
                description=seg_data.description,
                start=start_id,
                end=end_id,
            )
            created = content_api_functions.save_object(
                obj=new_seg, proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            created = cast(planning.Segment, created)
        return {
            "obj_id": {"prefix": created.obj_id.prefix, "numeric": created.obj_id.numeric},
            "name": created.name,
            "description": created.description,
            "start": {"prefix": created.start.prefix, "numeric": created.start.numeric},
            "end": {"prefix": created.end.prefix, "numeric": created.end.numeric},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaign/s/{numeric}", response_model=SegmentResponse)
def update_segment(numeric: int, seg_data: SegmentUpdate, user: AuthUser = Depends(get_authenticated_user)):
    """Update an existing segment."""
    proto_user_id = user.proto_user_id
    try:
        seg_id = planning.ID(prefix="S", numeric=numeric)
        existing = content_api_functions.retrieve_object(obj_id=seg_id, proto_user_id=proto_user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Segment not found")
        start_id = planning.ID(prefix=seg_data.start["prefix"], numeric=seg_data.start["numeric"])
        end_id = planning.ID(prefix=seg_data.end["prefix"], numeric=seg_data.end["numeric"])
        updated = planning.Segment(
            obj_id=seg_id,  # type: ignore[arg-type]
            name=seg_data.name,
            description=seg_data.description,
            start=start_id,
            end=end_id,
        )
        result = content_api_functions.update_object(obj=updated, proto_user_id=proto_user_id)
        result = cast(planning.Segment, result)
        return {
            "obj_id": {"prefix": result.obj_id.prefix, "numeric": result.obj_id.numeric},
            "name": result.name,
            "description": result.description,
            "start": {"prefix": result.start.prefix, "numeric": result.start.numeric},
            "end": {"prefix": result.end.prefix, "numeric": result.end.numeric},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaign/s/{numeric}")
def delete_segment(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Delete a segment."""
    proto_user_id = user.proto_user_id
    try:
        seg_id = planning.ID(prefix="S", numeric=numeric)
        success = content_api_functions.delete_object(obj_id=seg_id, proto_user_id=proto_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Segment not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Arc CRUD ==============
class ArcCreate(BaseModel):
    name: str = ""
    description: str = ""
    segments: list[dict] = []  # list of segment objects


class ArcUpdate(BaseModel):
    obj_id: dict
    name: str = ""
    description: str = ""
    segments: list[dict] = []


class ArcResponse(BaseModel):
    obj_id: dict
    name: str
    description: str
    segments: list[dict]


@router.get("/campaign/a", response_model=list[ArcResponse])
def list_arcs(user: AuthUser = Depends(get_authenticated_user)):
    """List all arcs for a user."""
    proto_user_id = user.proto_user_id
    try:
        arcs = content_api_functions.retrieve_objects(obj_type=planning.Arc, proto_user_id=proto_user_id)
        arcs = cast(list[planning.Arc], arcs)
        return [
            {
                "obj_id": {"prefix": a.obj_id.prefix, "numeric": a.obj_id.numeric},
                "name": a.name,
                "description": a.description,
                "segments": [
                    {
                        "obj_id": {"prefix": s.obj_id.prefix, "numeric": s.obj_id.numeric},
                        "name": s.name,
                        "description": s.description,
                        "start": {"prefix": s.start.prefix, "numeric": s.start.numeric},
                        "end": {"prefix": s.end.prefix, "numeric": s.end.numeric},
                    }
                    for s in a.segments
                ],
            }
            for a in arcs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/a/{numeric}", response_model=ArcResponse)
def get_arc(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Get a specific arc by ID."""
    proto_user_id = user.proto_user_id
    try:
        arc_id = planning.ID(prefix="A", numeric=numeric)
        arc = content_api_functions.retrieve_object(obj_id=arc_id, proto_user_id=proto_user_id)
        arc = cast(planning.Arc | None, arc)
        if not arc:
            raise HTTPException(status_code=404, detail="Arc not found")
        return {
            "obj_id": {"prefix": arc.obj_id.prefix, "numeric": arc.obj_id.numeric},
            "name": arc.name,
            "description": arc.description,
            "segments": [
                {
                    "obj_id": {"prefix": s.obj_id.prefix, "numeric": s.obj_id.numeric},
                    "name": s.name,
                    "description": s.description,
                    "start": {"prefix": s.start.prefix, "numeric": s.start.numeric},
                    "end": {"prefix": s.end.prefix, "numeric": s.end.numeric},
                }
                for s in arc.segments
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/a", response_model=ArcResponse)
def create_arc(arc_data: ArcCreate, user: AuthUser = Depends(get_authenticated_user)):
    """Create a new arc."""
    proto_user_id = user.proto_user_id
    try:
        with transaction() as session:
            new_id = content_api_functions.generate_id(
                prefix="A", proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            # Convert segment dicts to Segment objects
            segments = []
            for seg_dict in arc_data.segments:
                seg_id = planning.ID(prefix=seg_dict["obj_id"]["prefix"], numeric=seg_dict["obj_id"]["numeric"])
                start_id = planning.ID(prefix=seg_dict["start"]["prefix"], numeric=seg_dict["start"]["numeric"])
                end_id = planning.ID(prefix=seg_dict["end"]["prefix"], numeric=seg_dict["end"]["numeric"])
                segments.append(
                    planning.Segment(
                        obj_id=seg_id,  # type: ignore[arg-type]
                        name=seg_dict.get("name", ""),
                        description=seg_dict.get("description", ""),
                        start=start_id,
                        end=end_id,
                    )
                )
            new_arc = planning.Arc(
                obj_id=new_id,  # type: ignore[arg-type]
                name=arc_data.name,
                description=arc_data.description,
                segments=segments,
            )
            created = content_api_functions.save_object(
                obj=new_arc, proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            created = cast(planning.Arc, created)
        return {
            "obj_id": {"prefix": created.obj_id.prefix, "numeric": created.obj_id.numeric},
            "name": created.name,
            "description": created.description,
            "segments": [
                {
                    "obj_id": {"prefix": s.obj_id.prefix, "numeric": s.obj_id.numeric},
                    "name": s.name,
                    "description": s.description,
                    "start": {"prefix": s.start.prefix, "numeric": s.start.numeric},
                    "end": {"prefix": s.end.prefix, "numeric": s.end.numeric},
                }
                for s in created.segments
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaign/a/{numeric}", response_model=ArcResponse)
def update_arc(numeric: int, arc_data: ArcUpdate, user: AuthUser = Depends(get_authenticated_user)):
    """Update an existing arc."""
    proto_user_id = user.proto_user_id
    try:
        arc_id = planning.ID(prefix="A", numeric=numeric)
        existing = content_api_functions.retrieve_object(obj_id=arc_id, proto_user_id=proto_user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Arc not found")
        segments = []
        for seg_dict in arc_data.segments:
            seg_id = planning.ID(prefix=seg_dict["obj_id"]["prefix"], numeric=seg_dict["obj_id"]["numeric"])
            start_id = planning.ID(prefix=seg_dict["start"]["prefix"], numeric=seg_dict["start"]["numeric"])
            end_id = planning.ID(prefix=seg_dict["end"]["prefix"], numeric=seg_dict["end"]["numeric"])
            segments.append(
                planning.Segment(
                    obj_id=seg_id,  # type: ignore[arg-type]
                    name=seg_dict.get("name", ""),
                    description=seg_dict.get("description", ""),
                    start=start_id,
                    end=end_id,
                )
            )
        updated = planning.Arc(
            obj_id=arc_id,  # type: ignore[arg-type]
            name=arc_data.name,
            description=arc_data.description,
            segments=segments,
        )
        result = content_api_functions.update_object(obj=updated, proto_user_id=proto_user_id)
        result = cast(planning.Arc, result)
        return {
            "obj_id": {"prefix": result.obj_id.prefix, "numeric": result.obj_id.numeric},
            "name": result.name,
            "description": result.description,
            "segments": [
                {
                    "obj_id": {"prefix": s.obj_id.prefix, "numeric": s.obj_id.numeric},
                    "name": s.name,
                    "description": s.description,
                    "start": {"prefix": s.start.prefix, "numeric": s.start.numeric},
                    "end": {"prefix": s.end.prefix, "numeric": s.end.numeric},
                }
                for s in result.segments
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaign/a/{numeric}")
def delete_arc(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Delete an arc."""
    proto_user_id = user.proto_user_id
    try:
        arc_id = planning.ID(prefix="A", numeric=numeric)
        success = content_api_functions.delete_object(obj_id=arc_id, proto_user_id=proto_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Arc not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Item CRUD ==============
class ItemCreate(BaseModel):
    name: str = ""
    type_: str = ""
    description: str = ""
    properties: dict[str, str] = {}


class ItemUpdate(BaseModel):
    obj_id: dict
    name: str = ""
    type_: str = ""
    description: str = ""
    properties: dict[str, str] = {}


class ItemResponse(BaseModel):
    obj_id: dict
    name: str
    type_: str
    description: str
    properties: dict[str, str]


@router.get("/campaign/i", response_model=list[ItemResponse])
def list_items(user: AuthUser = Depends(get_authenticated_user)):
    """List all items for a user."""
    proto_user_id = user.proto_user_id
    try:
        items = content_api_functions.retrieve_objects(obj_type=planning.Item, proto_user_id=proto_user_id)
        items = cast(list[planning.Item], items)
        return [
            {
                "obj_id": {"prefix": i.obj_id.prefix, "numeric": i.obj_id.numeric},
                "name": i.name,
                "type_": i.type_,
                "description": i.description,
                "properties": i.properties,
            }
            for i in items
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/i/{numeric}", response_model=ItemResponse)
def get_item(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Get a specific item by ID."""
    proto_user_id = user.proto_user_id
    try:
        item_id = planning.ID(prefix="I", numeric=numeric)
        item = content_api_functions.retrieve_object(obj_id=item_id, proto_user_id=proto_user_id)
        item = cast(planning.Item | None, item)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return {
            "obj_id": {"prefix": item.obj_id.prefix, "numeric": item.obj_id.numeric},
            "name": item.name,
            "type_": item.type_,
            "description": item.description,
            "properties": item.properties,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/i", response_model=ItemResponse)
def create_item(item_data: ItemCreate, user: AuthUser = Depends(get_authenticated_user)):
    """Create a new item."""
    proto_user_id = user.proto_user_id
    try:
        with transaction() as session:
            new_id = content_api_functions.generate_id(
                prefix="I", proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            new_item = planning.Item(
                obj_id=new_id,  # type: ignore[arg-type]
                name=item_data.name,
                type_=item_data.type_,
                description=item_data.description,
                properties=item_data.properties,
            )
            created = content_api_functions.save_object(
                obj=new_item, proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            created = cast(planning.Item, created)
        return {
            "obj_id": {"prefix": created.obj_id.prefix, "numeric": created.obj_id.numeric},
            "name": created.name,
            "type_": created.type_,
            "description": created.description,
            "properties": created.properties,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaign/i/{numeric}", response_model=ItemResponse)
def update_item(numeric: int, item_data: ItemUpdate, user: AuthUser = Depends(get_authenticated_user)):
    """Update an existing item."""
    proto_user_id = user.proto_user_id
    try:
        item_id = planning.ID(prefix="I", numeric=numeric)
        existing = content_api_functions.retrieve_object(obj_id=item_id, proto_user_id=proto_user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Item not found")
        updated = planning.Item(
            obj_id=item_id,  # type: ignore[arg-type]
            name=item_data.name,
            type_=item_data.type_,
            description=item_data.description,
            properties=item_data.properties,
        )
        result = content_api_functions.update_object(obj=updated, proto_user_id=proto_user_id)
        result = cast(planning.Item, result)
        return {
            "obj_id": {"prefix": result.obj_id.prefix, "numeric": result.obj_id.numeric},
            "name": result.name,
            "type_": result.type_,
            "description": result.description,
            "properties": result.properties,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaign/i/{numeric}")
def delete_item(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Delete an item."""
    proto_user_id = user.proto_user_id
    try:
        item_id = planning.ID(prefix="I", numeric=numeric)
        success = content_api_functions.delete_object(obj_id=item_id, proto_user_id=proto_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Character CRUD ==============
class CharacterCreate(BaseModel):
    name: str = ""
    role: str = ""
    backstory: str = ""
    attributes: dict[str, int] = {}
    skills: dict[str, int] = {}
    storylines: list[dict] = []  # list of {prefix, numeric}
    inventory: list[dict] = []  # list of {prefix, numeric}


class CharacterUpdate(BaseModel):
    obj_id: dict
    name: str = ""
    role: str = ""
    backstory: str = ""
    attributes: dict[str, int] = {}
    skills: dict[str, int] = {}
    storylines: list[dict] = []
    inventory: list[dict] = []


class CharacterResponse(BaseModel):
    obj_id: dict
    name: str
    role: str
    backstory: str
    attributes: dict[str, int]
    skills: dict[str, int]
    storylines: list[dict]
    inventory: list[dict]


@router.get("/campaign/c", response_model=list[CharacterResponse])
def list_characters(user: AuthUser = Depends(get_authenticated_user)):
    """List all characters for a user."""
    proto_user_id = user.proto_user_id
    try:
        characters = content_api_functions.retrieve_objects(obj_type=planning.Character, proto_user_id=proto_user_id)
        characters = cast(list[planning.Character], characters)
        return [
            {
                "obj_id": {"prefix": c.obj_id.prefix, "numeric": c.obj_id.numeric},
                "name": c.name,
                "role": c.role,
                "backstory": c.backstory,
                "attributes": c.attributes,
                "skills": c.skills,
                "storylines": [{"prefix": s.prefix, "numeric": s.numeric} for s in c.storylines],
                "inventory": [{"prefix": i.prefix, "numeric": i.numeric} for i in c.inventory],
            }
            for c in characters
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/c/{numeric}", response_model=CharacterResponse)
def get_character(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Get a specific character by ID."""
    proto_user_id = user.proto_user_id
    try:
        char_id = planning.ID(prefix="C", numeric=numeric)
        character = content_api_functions.retrieve_object(obj_id=char_id, proto_user_id=proto_user_id)
        character = cast(planning.Character | None, character)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        return {
            "obj_id": {"prefix": character.obj_id.prefix, "numeric": character.obj_id.numeric},
            "name": character.name,
            "role": character.role,
            "backstory": character.backstory,
            "attributes": character.attributes,
            "skills": character.skills,
            "storylines": [{"prefix": s.prefix, "numeric": s.numeric} for s in character.storylines],
            "inventory": [{"prefix": i.prefix, "numeric": i.numeric} for i in character.inventory],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/c", response_model=CharacterResponse)
def create_character(char_data: CharacterCreate, user: AuthUser = Depends(get_authenticated_user)):
    """Create a new character."""
    proto_user_id = user.proto_user_id
    try:
        with transaction() as session:
            new_id = content_api_functions.generate_id(
                prefix="C", proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            storylines = [planning.ID(prefix=s["prefix"], numeric=s["numeric"]) for s in char_data.storylines]
            inventory = [planning.ID(prefix=i["prefix"], numeric=i["numeric"]) for i in char_data.inventory]
            new_char = planning.Character(
                obj_id=new_id,  # type: ignore[arg-type]
                name=char_data.name,
                role=char_data.role,
                backstory=char_data.backstory,
                attributes=char_data.attributes,
                skills=char_data.skills,
                storylines=storylines,
                inventory=inventory,
            )
            created = content_api_functions.save_object(
                obj=new_char, proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            created = cast(planning.Character, created)
        return {
            "obj_id": {"prefix": created.obj_id.prefix, "numeric": created.obj_id.numeric},
            "name": created.name,
            "role": created.role,
            "backstory": created.backstory,
            "attributes": created.attributes,
            "skills": created.skills,
            "storylines": [{"prefix": s.prefix, "numeric": s.numeric} for s in created.storylines],
            "inventory": [{"prefix": i.prefix, "numeric": i.numeric} for i in created.inventory],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaign/c/{numeric}", response_model=CharacterResponse)
def update_character(numeric: int, char_data: CharacterUpdate, user: AuthUser = Depends(get_authenticated_user)):
    """Update an existing character."""
    proto_user_id = user.proto_user_id
    try:
        char_id = planning.ID(prefix="C", numeric=numeric)
        existing = content_api_functions.retrieve_object(obj_id=char_id, proto_user_id=proto_user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Character not found")
        storylines = [planning.ID(prefix=s["prefix"], numeric=s["numeric"]) for s in char_data.storylines]
        inventory = [planning.ID(prefix=i["prefix"], numeric=i["numeric"]) for i in char_data.inventory]
        updated = planning.Character(
            obj_id=char_id,  # type: ignore[arg-type]
            name=char_data.name,
            role=char_data.role,
            backstory=char_data.backstory,
            attributes=char_data.attributes,
            skills=char_data.skills,
            storylines=storylines,
            inventory=inventory,
        )
        result = content_api_functions.update_object(obj=updated, proto_user_id=proto_user_id)
        result = cast(planning.Character, result)
        return {
            "obj_id": {"prefix": result.obj_id.prefix, "numeric": result.obj_id.numeric},
            "name": result.name,
            "role": result.role,
            "backstory": result.backstory,
            "attributes": result.attributes,
            "skills": result.skills,
            "storylines": [{"prefix": s.prefix, "numeric": s.numeric} for s in result.storylines],
            "inventory": [{"prefix": i.prefix, "numeric": i.numeric} for i in result.inventory],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaign/c/{numeric}")
def delete_character(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Delete a character."""
    proto_user_id = user.proto_user_id
    try:
        char_id = planning.ID(prefix="C", numeric=numeric)
        success = content_api_functions.delete_object(obj_id=char_id, proto_user_id=proto_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Character not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Location CRUD ==============
class LocationCreate(BaseModel):
    name: str = ""
    description: str = ""
    neighboring_locations: list[dict] = []  # list of {prefix, numeric}
    coords: tuple[float, float] | tuple[float, float, float] | None = None


class LocationUpdate(BaseModel):
    obj_id: dict
    name: str = ""
    description: str = ""
    neighboring_locations: list[dict] = []
    coords: tuple[float, float] | tuple[float, float, float] | None = None


class LocationResponse(BaseModel):
    obj_id: dict
    name: str
    description: str
    neighboring_locations: list[dict]
    coords: tuple[float, float] | tuple[float, float, float] | None


@router.get("/campaign/l", response_model=list[LocationResponse])
def list_locations(user: AuthUser = Depends(get_authenticated_user)):
    """List all locations for a user."""
    proto_user_id = user.proto_user_id
    try:
        locations = content_api_functions.retrieve_objects(obj_type=planning.Location, proto_user_id=proto_user_id)
        locations = cast(list[planning.Location], locations)
        return [
            {
                "obj_id": {"prefix": loc.obj_id.prefix, "numeric": loc.obj_id.numeric},
                "name": loc.name,
                "description": loc.description,
                "neighboring_locations": [
                    {"prefix": n.prefix, "numeric": n.numeric} for n in loc.neighboring_locations
                ],
                "coords": loc.coords,
            }
            for loc in locations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/l/{numeric}", response_model=LocationResponse)
def get_location(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Get a specific location by ID."""
    proto_user_id = user.proto_user_id
    try:
        loc_id = planning.ID(prefix="L", numeric=numeric)
        location = content_api_functions.retrieve_object(obj_id=loc_id, proto_user_id=proto_user_id)
        location = cast(planning.Location | None, location)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        return {
            "obj_id": {"prefix": location.obj_id.prefix, "numeric": location.obj_id.numeric},
            "name": location.name,
            "description": location.description,
            "neighboring_locations": [
                {"prefix": n.prefix, "numeric": n.numeric} for n in location.neighboring_locations
            ],
            "coords": location.coords,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/l", response_model=LocationResponse)
def create_location(loc_data: LocationCreate, user: AuthUser = Depends(get_authenticated_user)):
    """Create a new location."""
    proto_user_id = user.proto_user_id
    try:
        with transaction() as session:
            new_id = content_api_functions.generate_id(
                prefix="L", proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            neighbors = [planning.ID(prefix=n["prefix"], numeric=n["numeric"]) for n in loc_data.neighboring_locations]
            new_loc = planning.Location(
                obj_id=new_id,  # type: ignore[arg-type]
                name=loc_data.name,
                description=loc_data.description,
                neighboring_locations=neighbors,
                coords=loc_data.coords,
            )
            created = content_api_functions.save_object(
                obj=new_loc, proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            created = cast(planning.Location, created)
        return {
            "obj_id": {"prefix": created.obj_id.prefix, "numeric": created.obj_id.numeric},
            "name": created.name,
            "description": created.description,
            "neighboring_locations": [
                {"prefix": n.prefix, "numeric": n.numeric} for n in created.neighboring_locations
            ],
            "coords": created.coords,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaign/l/{numeric}", response_model=LocationResponse)
def update_location(numeric: int, loc_data: LocationUpdate, user: AuthUser = Depends(get_authenticated_user)):
    """Update an existing location."""
    proto_user_id = user.proto_user_id
    try:
        loc_id = planning.ID(prefix="L", numeric=numeric)
        existing = content_api_functions.retrieve_object(obj_id=loc_id, proto_user_id=proto_user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Location not found")
        neighbors = [planning.ID(prefix=n["prefix"], numeric=n["numeric"]) for n in loc_data.neighboring_locations]
        updated = planning.Location(
            obj_id=loc_id,  # type: ignore[arg-type]
            name=loc_data.name,
            description=loc_data.description,
            neighboring_locations=neighbors,
            coords=loc_data.coords,
        )
        result = content_api_functions.update_object(obj=updated, proto_user_id=proto_user_id)
        result = cast(planning.Location, result)
        return {
            "obj_id": {"prefix": result.obj_id.prefix, "numeric": result.obj_id.numeric},
            "name": result.name,
            "description": result.description,
            "neighboring_locations": [{"prefix": n.prefix, "numeric": n.numeric} for n in result.neighboring_locations],
            "coords": result.coords,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaign/l/{numeric}")
def delete_location(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Delete a location."""
    proto_user_id = user.proto_user_id
    try:
        loc_id = planning.ID(prefix="L", numeric=numeric)
        success = content_api_functions.delete_object(obj_id=loc_id, proto_user_id=proto_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Location not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== CampaignPlan CRUD ==============
class CampaignPlanCreate(BaseModel):
    title: str = ""
    version: str = ""
    setting: str = ""
    summary: str = ""
    storypoints: list[dict] = []
    storyline: list[dict] = []
    characters: list[dict] = []
    locations: list[dict] = []
    items: list[dict] = []
    rules: list[dict] = []
    objectives: list[dict] = []


class CampaignPlanUpdate(BaseModel):
    obj_id: dict
    title: str = ""
    version: str = ""
    setting: str = ""
    summary: str = ""
    storypoints: list[dict] = []
    storyline: list[dict] = []
    characters: list[dict] = []
    locations: list[dict] = []
    items: list[dict] = []
    rules: list[dict] = []
    objectives: list[dict] = []


class CampaignPlanResponse(BaseModel):
    obj_id: dict
    title: str
    version: str
    setting: str
    summary: str
    storypoints: list[dict]
    storyline: list[dict]
    characters: list[dict]
    locations: list[dict]
    items: list[dict]
    rules: list[dict]
    objectives: list[dict]


def _serialize_campaign(campaign: planning.CampaignPlan) -> dict:
    """Helper to serialize a CampaignPlan to a response dict."""
    return {
        "obj_id": {"prefix": campaign.obj_id.prefix, "numeric": campaign.obj_id.numeric},
        "title": campaign.title,
        "version": campaign.version,
        "setting": campaign.setting,
        "summary": campaign.summary,
        "storypoints": [
            {
                "obj_id": {"prefix": p.obj_id.prefix, "numeric": p.obj_id.numeric},
                "name": p.name,
                "description": p.description,
                "objective": {"prefix": p.objective.prefix, "numeric": p.objective.numeric} if p.objective else None,
            }
            for p in campaign.storypoints
        ],
        "storyline": [
            {
                "obj_id": {"prefix": a.obj_id.prefix, "numeric": a.obj_id.numeric},
                "name": a.name,
                "description": a.description,
                "segments": [
                    {
                        "obj_id": {"prefix": s.obj_id.prefix, "numeric": s.obj_id.numeric},
                        "name": s.name,
                        "description": s.description,
                        "start": {"prefix": s.start.prefix, "numeric": s.start.numeric},
                        "end": {"prefix": s.end.prefix, "numeric": s.end.numeric},
                    }
                    for s in a.segments
                ],
            }
            for a in campaign.storyline
        ],
        "characters": [
            {
                "obj_id": {"prefix": c.obj_id.prefix, "numeric": c.obj_id.numeric},
                "name": c.name,
                "role": c.role,
                "backstory": c.backstory,
                "attributes": c.attributes,
                "skills": c.skills,
                "storylines": [{"prefix": s.prefix, "numeric": s.numeric} for s in c.storylines],
                "inventory": [{"prefix": i.prefix, "numeric": i.numeric} for i in c.inventory],
            }
            for c in campaign.characters
        ],
        "locations": [
            {
                "obj_id": {"prefix": loc.obj_id.prefix, "numeric": loc.obj_id.numeric},
                "name": loc.name,
                "description": loc.description,
                "neighboring_locations": [
                    {"prefix": n.prefix, "numeric": n.numeric} for n in loc.neighboring_locations
                ],
                "coords": loc.coords,
            }
            for loc in campaign.locations
        ],
        "items": [
            {
                "obj_id": {"prefix": i.obj_id.prefix, "numeric": i.obj_id.numeric},
                "name": i.name,
                "type_": i.type_,
                "description": i.description,
                "properties": i.properties,
            }
            for i in campaign.items
        ],
        "rules": [
            {
                "obj_id": {"prefix": r.obj_id.prefix, "numeric": r.obj_id.numeric},
                "description": r.description,
                "effect": r.effect,
                "components": r.components,
            }
            for r in campaign.rules
        ],
        "objectives": [
            {
                "obj_id": {"prefix": o.obj_id.prefix, "numeric": o.obj_id.numeric},
                "description": o.description,
                "components": o.components,
                "prerequisites": [{"prefix": p.prefix, "numeric": p.numeric} for p in o.prerequisites],
            }
            for o in campaign.objectives
        ],
    }


@router.get("/campaign/campplan", response_model=list[CampaignPlanResponse])
def list_campaigns(user: AuthUser = Depends(get_authenticated_user)):
    """List all campaign plans for a user."""
    proto_user_id = user.proto_user_id
    try:
        campaigns = content_api_functions.retrieve_objects(obj_type=planning.CampaignPlan, proto_user_id=proto_user_id)
        campaigns = cast(list[planning.CampaignPlan], campaigns)
        return [_serialize_campaign(c) for c in campaigns]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/campplan/{numeric}", response_model=CampaignPlanResponse)
def get_campaign(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Get a specific campaign plan by ID."""
    proto_user_id = user.proto_user_id
    try:
        camp_id = planning.ID(prefix="CampPlan", numeric=numeric)
        campaign = content_api_functions.retrieve_object(obj_id=camp_id, proto_user_id=proto_user_id)
        campaign = cast(planning.CampaignPlan | None, campaign)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return _serialize_campaign(campaign)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/campplan", response_model=CampaignPlanResponse)
def create_campaign(camp_data: CampaignPlanCreate, user: AuthUser = Depends(get_authenticated_user)):
    """Create a new campaign plan."""
    proto_user_id = user.proto_user_id
    try:
        with transaction() as session:
            new_id = content_api_functions.generate_id(
                prefix="CampPlan", proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            # For simplicity, create with empty collections - nested objects can be added separately
            new_camp = planning.CampaignPlan(
                obj_id=new_id,  # type: ignore[arg-type]
                title=camp_data.title,
                version=camp_data.version,
                setting=camp_data.setting,
                summary=camp_data.summary,
                storypoints=[],
                storyline=[],
                characters=[],
                locations=[],
                items=[],
                rules=[],
                objectives=[],
            )
            created = content_api_functions.save_object(
                obj=new_camp, proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            created = cast(planning.CampaignPlan, created)
        return _serialize_campaign(created)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaign/campplan/{numeric}", response_model=CampaignPlanResponse)
def update_campaign(numeric: int, camp_data: CampaignPlanUpdate, user: AuthUser = Depends(get_authenticated_user)):
    """Update an existing campaign plan, including all nested objects."""
    proto_user_id = user.proto_user_id
    try:
        camp_id = planning.ID(prefix="CampPlan", numeric=numeric)
        existing = content_api_functions.retrieve_object(obj_id=camp_id, proto_user_id=proto_user_id)
        existing = cast(planning.CampaignPlan | None, existing)
        if not existing:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Parse nested objects from dicts to Pydantic models
        storypoints = [planning.Point.model_validate(p) for p in camp_data.storypoints]
        storyline = [planning.Arc.model_validate(a) for a in camp_data.storyline]
        characters = [planning.Character.model_validate(c) for c in camp_data.characters]
        locations = [planning.Location.model_validate(loc) for loc in camp_data.locations]
        items = [planning.Item.model_validate(i) for i in camp_data.items]
        rules = [planning.Rule.model_validate(r) for r in camp_data.rules]
        objectives = [planning.Objective.model_validate(o) for o in camp_data.objectives]

        updated = planning.CampaignPlan(
            obj_id=camp_id,  # type: ignore[arg-type]
            title=camp_data.title,
            version=camp_data.version,
            setting=camp_data.setting,
            summary=camp_data.summary,
            storypoints=storypoints,
            storyline=storyline,
            characters=characters,
            locations=locations,
            items=items,
            rules=rules,
            objectives=objectives,
        )
        result = content_api_functions.update_object(obj=updated, proto_user_id=proto_user_id)
        result = cast(planning.CampaignPlan, result)
        return _serialize_campaign(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaign/campplan/{numeric}")
def delete_campaign(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Delete a campaign plan."""
    proto_user_id = user.proto_user_id
    try:
        camp_id = planning.ID(prefix="CampPlan", numeric=numeric)
        success = content_api_functions.delete_object(obj_id=camp_id, proto_user_id=proto_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== AgentConfig CRUD ==============
class AgentConfigCreate(BaseModel):
    name: str = ""
    provider_type: str = ""
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    max_tokens: int = 500
    temperature: float = 0.7
    is_default: bool = False
    is_enabled: bool = True
    system_prompt: str = ""


class AgentConfigUpdate(BaseModel):
    obj_id: dict
    name: str = ""
    provider_type: str = ""
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    max_tokens: int = 500
    temperature: float = 0.7
    is_default: bool = False
    is_enabled: bool = True
    system_prompt: str = ""


class AgentConfigResponse(BaseModel):
    obj_id: dict
    name: str
    provider_type: str
    api_key: str
    base_url: str
    model: str
    max_tokens: int
    temperature: float
    is_default: bool
    is_enabled: bool
    system_prompt: str


@router.get("/campaign/ag", response_model=list[AgentConfigResponse])
def list_agent_configs(user: AuthUser = Depends(get_authenticated_user)):
    """List all agent configs for a user."""
    proto_user_id = user.proto_user_id
    try:
        configs = content_api_functions.retrieve_objects(obj_type=planning.AgentConfig, proto_user_id=proto_user_id)
        configs = cast(list[planning.AgentConfig], configs)
        return [
            {
                "obj_id": {"prefix": c.obj_id.prefix, "numeric": c.obj_id.numeric},
                "name": c.name,
                "provider_type": c.provider_type,
                "api_key": c.api_key,
                "base_url": c.base_url,
                "model": c.model,
                "max_tokens": c.max_tokens,
                "temperature": c.temperature,
                "is_default": c.is_default,
                "is_enabled": c.is_enabled,
                "system_prompt": c.system_prompt,
            }
            for c in configs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/ag/{numeric}", response_model=AgentConfigResponse)
def get_agent_config(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Get a specific agent config by ID."""
    proto_user_id = user.proto_user_id
    try:
        config_id = planning.ID(prefix="AG", numeric=numeric)
        config = content_api_functions.retrieve_object(obj_id=config_id, proto_user_id=proto_user_id)
        config = cast(planning.AgentConfig | None, config)
        if not config:
            raise HTTPException(status_code=404, detail="AgentConfig not found")
        return {
            "obj_id": {"prefix": config.obj_id.prefix, "numeric": config.obj_id.numeric},
            "name": config.name,
            "provider_type": config.provider_type,
            "api_key": config.api_key,
            "base_url": config.base_url,
            "model": config.model,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "is_default": config.is_default,
            "is_enabled": config.is_enabled,
            "system_prompt": config.system_prompt,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/ag", response_model=AgentConfigResponse)
def create_agent_config(config_data: AgentConfigCreate, user: AuthUser = Depends(get_authenticated_user)):
    """Create a new agent config."""
    proto_user_id = user.proto_user_id
    try:
        with transaction() as session:
            new_id = content_api_functions.generate_id(
                prefix="AG", proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            new_config = planning.AgentConfig(
                obj_id=new_id,  # type: ignore[arg-type]
                name=config_data.name,
                provider_type=config_data.provider_type,
                api_key=config_data.api_key,
                base_url=config_data.base_url,
                model=config_data.model,
                max_tokens=config_data.max_tokens,
                temperature=config_data.temperature,
                is_default=config_data.is_default,
                is_enabled=config_data.is_enabled,
                system_prompt=config_data.system_prompt,
            )
            created = content_api_functions.save_object(
                obj=new_config, proto_user_id=proto_user_id, session=session, auto_commit=False
            )
            created = cast(planning.AgentConfig, created)
        return {
            "obj_id": {"prefix": created.obj_id.prefix, "numeric": created.obj_id.numeric},
            "name": created.name,
            "provider_type": created.provider_type,
            "api_key": created.api_key,
            "base_url": created.base_url,
            "model": created.model,
            "max_tokens": created.max_tokens,
            "temperature": created.temperature,
            "is_default": created.is_default,
            "is_enabled": created.is_enabled,
            "system_prompt": created.system_prompt,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/campaign/ag/{numeric}", response_model=AgentConfigResponse)
def update_agent_config(numeric: int, config_data: AgentConfigUpdate, user: AuthUser = Depends(get_authenticated_user)):
    """Update an existing agent config."""
    proto_user_id = user.proto_user_id
    try:
        config_id = planning.ID(prefix="AG", numeric=numeric)
        existing = content_api_functions.retrieve_object(obj_id=config_id, proto_user_id=proto_user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="AgentConfig not found")
        updated = planning.AgentConfig(
            obj_id=config_id,  # type: ignore[arg-type]
            name=config_data.name,
            provider_type=config_data.provider_type,
            api_key=config_data.api_key,
            base_url=config_data.base_url,
            model=config_data.model,
            max_tokens=config_data.max_tokens,
            temperature=config_data.temperature,
            is_default=config_data.is_default,
            is_enabled=config_data.is_enabled,
            system_prompt=config_data.system_prompt,
        )
        result = content_api_functions.update_object(obj=updated, proto_user_id=proto_user_id)
        result = cast(planning.AgentConfig, result)
        return {
            "obj_id": {"prefix": result.obj_id.prefix, "numeric": result.obj_id.numeric},
            "name": result.name,
            "provider_type": result.provider_type,
            "api_key": result.api_key,
            "base_url": result.base_url,
            "model": result.model,
            "max_tokens": result.max_tokens,
            "temperature": result.temperature,
            "is_default": result.is_default,
            "is_enabled": result.is_enabled,
            "system_prompt": result.system_prompt,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaign/ag/{numeric}")
def delete_agent_config(numeric: int, user: AuthUser = Depends(get_authenticated_user)):
    """Delete an agent config."""
    proto_user_id = user.proto_user_id
    try:
        config_id = planning.ID(prefix="AG", numeric=numeric)
        success = content_api_functions.delete_object(obj_id=config_id, proto_user_id=proto_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="AgentConfig not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
