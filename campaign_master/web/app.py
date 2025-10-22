import subprocess
import fastapi
import pathlib
from pydantic_core import PydanticUndefined  # HACK: Used to check for undefined defaults

from ..content import planning, executing

app = fastapi.FastAPI()

def get_required_fields(model: type[planning.AbstractObject]) -> list[str]:
    """
    Returns a list of names of required fields in a Pydantic model.
    """
    required_fields = []
    for field_name, field_info in model.model_fields.items():
        if field_info.default is PydanticUndefined:
            required_fields.append(field_name)
    return required_fields

ANNO_TO_JS_TYPE: dict[type, str] = {
    str: "text",
    int: "number",
    float: "number",
    bool: "checkbox",
    list: "array",
    dict: "object",
    tuple: "array",
}


def build():
    """
    Builds the web app by installing dependencies and running the build script.

    Raises
    ------
    subprocess.CalledProcessError
        If any of the subprocess commands fail.
    """
    print("Building web app...")

    subprocess.run(['npm', 'install'], check=True, shell=True)
    subprocess.run(['npm', 'run', 'build'], check=True, shell=True)
    print("Web app built successfully.")


def run_dev():
    """
    Runs the development server.
    """
    try:
        subprocess.run(['npm', 'run', 'dev'], check=True, shell=True)
    except KeyboardInterrupt:
        print("Development server interrupted by user.")
    else:
        print("Development server closed.")

# Base case, first serve. Rest is handled by the frontend router.
# To conceptualize, this establishes the applet session, while endpoints and static files are requested as needed.
@app.get("/")
async def index():
    try:
        return fastapi.responses.FileResponse(pathlib.Path("dist/index.html"))
    except Exception as e:
        return fastapi.responses.PlainTextResponse(str(e), status_code=500)


@app.get("/api/app/planning")
async def get_app_fields():
    """
    API endpoint to retrieve planning object fields.

    Returns
    -------
    dict
        A dictionary containing the fields for planning objects.
    """
    required_fields = get_required_fields(planning.CampaignPlan)
    obj = {"fields": [
        {
            "name": field_name,
            "label": field_name.replace("_", " ").title(),
            "type": ANNO_TO_JS_TYPE.get(field_info.annotation or str, "text"),
            "required": field_name in required_fields
        }
        for field_name, field_info in planning.CampaignPlan.model_fields.items()
    ]}
    print(obj)
    return obj
