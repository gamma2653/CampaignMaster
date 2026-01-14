import pathlib
from contextlib import asynccontextmanager

import fastapi
import uvicorn
from fastapi.staticfiles import StaticFiles

from ..content import database as content_api
from ..util import get_uvicorn_log_config
from .settings import Settings

# from .auth import router as auth_router, create_db_and_tables as create_auth_db_and_tables
# from .api import router as api_router, create_db_and_tables as create_api_db_and_tables


# Mount auth router


@asynccontextmanager
async def setter_and_cleaner(app: fastapi.FastAPI):
    # Initialize tables
    # create_api_db_and_tables(engine)
    # create_auth_db_and_tables(engine)
    yield
    # Cleanup resources here


settings: Settings = Settings()
engine = content_api.engine
app = fastapi.FastAPI(lifespan=setter_and_cleaner)
# app


def initialize_app(settings_: Settings):
    """
    Initialize the FastAPI application with necessary configurations.
    """
    global app, engine, settings
    settings = settings_
    engine = content_api.engine

    # Import and register API router
    from .api import router as api_router

    app.include_router(api_router, prefix="/api")
    # app.include_router(auth_router, prefix="/auth")
    app.mount("/static", StaticFiles(directory=pathlib.Path("dist/static")), name="static")
    app.add_api_route("/", index, methods=["GET"])
    app.add_api_route("/{full_path:path}", spa_router, methods=["GET"])


def run_dev(host: str | None = None, port: int | None = None, debug: bool | None = None):
    """
    Runs the development server.

    When debug=True, logs are written to both console and a log file
    (default: logs/fastapi_debug.log). Configure via CM_log_dir and CM_log_filename.
    """
    host = host or settings.web_host
    port = port or settings.web_port
    debug = debug if debug is not None else settings.debug_mode
    initialize_app(settings)

    uvicorn_kwargs = {
        "host": host,
        "port": port,
        "log_level": "debug" if debug else "info",
    }

    if debug:
        log_file_path = settings.log_dir / settings.log_filename
        uvicorn_kwargs["log_config"] = get_uvicorn_log_config(str(log_file_path))
        print(f"Debug mode enabled. Logging to: {log_file_path.resolve()}")

    try:
        uvicorn.run(app, **uvicorn_kwargs)
    except Exception as e:
        print(f"Error starting development server: {e}")


# Base case, first serve. Rest is handled by the frontend router.
# To conceptualize, this establishes the applet session, while endpoints and static files are requested as needed.
# In production, serve built files from 'dist' directory using Nginx or some other CDN.
# @app.get("/")
async def index():
    try:
        return fastapi.responses.FileResponse(pathlib.Path("dist/index.html"))
    except Exception as e:
        return fastapi.responses.PlainTextResponse(str(e), status_code=500)


# Any case that does not match an API route should return the index.html for SPA routing.
# @app.get("/{full_path:path}")
async def spa_router(full_path: str):
    try:
        return fastapi.responses.FileResponse(pathlib.Path("dist/index.html"))
    except Exception as e:
        return fastapi.responses.PlainTextResponse(str(e), status_code=500)
