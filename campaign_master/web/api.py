import fastapi
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.engine import Engine

from ..content import api as content_api_functions
from ..content import database as content_api
from ..content import planning

router = fastapi.APIRouter()
DB_SERVICE: content_api.DBService | None = None


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
def list_points(proto_user_id: int = 0):
    """List all points for a user."""
    try:
        points = content_api_functions.retrieve_objects(
            obj_type=planning.Point, proto_user_id=proto_user_id
        )
        return [
            {
                "obj_id": {"prefix": p.obj_id.prefix, "numeric": p.obj_id.numeric},
                "name": p.name,
                "description": p.description,
                "objective": (
                    {"prefix": p.objective.prefix, "numeric": p.objective.numeric}
                    if p.objective
                    else None
                ),
            }
            for p in points
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/p/{numeric}", response_model=PointResponse)
def get_point(numeric: int, proto_user_id: int = 0):
    """Get a specific point by ID."""
    try:
        point_id = planning.PointID(prefix="P", numeric=numeric)
        point = content_api_functions.retrieve_object(
            obj_id=point_id, proto_user_id=proto_user_id
        )
        if not point:
            raise HTTPException(status_code=404, detail="Point not found")

        return {
            "obj_id": {"prefix": point.obj_id.prefix, "numeric": point.obj_id.numeric},
            "name": point.name,
            "description": point.description,
            "objective": (
                {"prefix": point.objective.prefix, "numeric": point.objective.numeric}
                if point.objective
                else None
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/p", response_model=PointResponse)
def create_point(point_data: PointCreate, proto_user_id: int = 0):
    """Create a new point."""
    try:
        # Generate new ID
        new_id = content_api_functions.generate_id(
            prefix="P", proto_user_id=proto_user_id
        )

        # Create objective ID if provided
        objective_id = None
        if point_data.objective:
            objective_id = planning.ObjectiveID(
                prefix=point_data.objective["prefix"],
                numeric=point_data.objective["numeric"],
            )

        # Create Point object
        new_point = planning.Point(
            _obj_id=new_id,
            name=point_data.name,
            description=point_data.description,
            objective=objective_id,
        )

        # Save to database
        created_point = content_api_functions._create_object(
            obj=new_point, proto_user_id=proto_user_id
        ).to_pydantic()

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
def update_point(numeric: int, point_data: PointUpdate, proto_user_id: int = 0):
    """Update an existing point."""
    try:
        # Verify point exists
        point_id = planning.PointID(prefix="P", numeric=numeric)
        existing_point = content_api_functions.retrieve_object(
            obj_id=point_id, proto_user_id=proto_user_id
        )
        if not existing_point:
            raise HTTPException(status_code=404, detail="Point not found")

        # Create objective ID if provided
        objective_id = None
        if point_data.objective:
            objective_id = planning.ObjectiveID(
                prefix=point_data.objective["prefix"],
                numeric=point_data.objective["numeric"],
            )

        # Create updated Point object
        updated_point = planning.Point(
            _obj_id=point_id,
            name=point_data.name,
            description=point_data.description,
            objective=objective_id,
        )

        # Update in database
        result = content_api_functions.update_object(
            obj=updated_point, proto_user_id=proto_user_id
        )

        return {
            "obj_id": {
                "prefix": result.obj_id.prefix,
                "numeric": result.obj_id.numeric,
            },
            "name": result.name,
            "description": result.description,
            "objective": (
                {"prefix": result.objective.prefix, "numeric": result.objective.numeric}
                if result.objective
                else None
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/campaign/p/{numeric}")
def delete_point(numeric: int, proto_user_id: int = 0):
    """Delete a point."""
    try:
        point_id = planning.PointID(prefix="P", numeric=numeric)
        success = content_api_functions.delete_object(
            obj_id=point_id, proto_user_id=proto_user_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Point not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Objective list endpoint for dropdown
@router.get("/campaign/o")
def list_objectives(proto_user_id: int = 0):
    """List all objectives for a user."""
    try:
        objectives = content_api_functions.retrieve_objects(
            obj_type=planning.Objective, proto_user_id=proto_user_id
        )
        return [
            {
                "obj_id": {"prefix": o.obj_id.prefix, "numeric": o.obj_id.numeric},
                "description": o.description,
                "components": o.components,
                "prerequisites": [
                    {"prefix": p.prefix, "numeric": p.numeric} for p in o.prerequisites
                ],
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
