import subprocess
from pydantic_core import PydanticUndefined  # HACK: Used to check for undefined defaults
from ..content import planning

def get_required_fields(model: type[planning.Object]) -> list[str]:
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
    # subprocess.run(['npm', 'run', 'css'], check=True, shell=True)
    print("Web app built successfully.")
