import subprocess
import fastapi
import pathlib

app = fastapi.FastAPI()


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


# Base case, first serve. Rest is handled by the frontend router.
# To conceptualize, this establishes the applet session, while endpoints and static files are requested as needed.
@app.get("/")
async def index():
    try:
        print(pathlib.Path("dist/index.html").resolve(strict=True))
        return fastapi.responses.FileResponse(pathlib.Path("dist/index.html"))
    except Exception as e:
        print(e)
        return fastapi.responses.PlainTextResponse(str(e), status_code=500)