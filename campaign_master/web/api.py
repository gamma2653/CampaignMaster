import fastapi
from sqlalchemy.engine import Engine
from ..content import api as content_api

router = fastapi.APIRouter()
DB_SERVICE: content_api.DBService | None = None

@router.get("/id_service")
def id_service(id_type: str = "misc", service: str | None = None):
    """
    Simple ID service endpoint that returns a new unique ID.
    """
    if not service:
        service = "planning"
    
    # Determine prefix based on id_type

def create_db_and_tables(engine: Engine):
    global DB_SERVICE
    if DB_SERVICE is None:
        DB_SERVICE = content_api.DBService(engine=engine)
    DB_SERVICE.create_db_and_tables()