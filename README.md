# Preperation

## Python
<sub>This section is required.</sub>

### Requirements

1. Ensure poetry is installed on your system as per their websites [instructions](https://python-poetry.org/docs/#installing-with-the-official-installer).
    - Configure your preferred virtualenv defaults before proceeding.

2. Run `poetry install`

3. Activate your poetry environment. [Poetry's instructions](https://python-poetry.org/docs/managing-environments#powershell)


## React/NodeJS
<sub>Note: First complete the above [Python setup](#python)</sub>
<sub>This section is optional; it is only required if you intend to use the `web` functionality.</sub>

1. Ensure NodeJS is installed on your system, giving access to the `npm` command.
  - On Windows, you can use the `winget install --id OpenJS.NodeJS --source winget` command (assuming the ID has not changed as of 10/09/25) to install the appropriate build.



# Execution

- Run `python -m campaign_master -h` to see more exhaustive usage information.

The best way to conceptualize this module is that it can first and foremost be run in two different ways, as a local applet (as a Qt application), or as a web server.The switch from serving the index via FastAPI to being served via Qt is considered trivial thanks to the precompilation step, if a hybrid mode is desired. Just serve the static files via Qt.

## App Mode
<sub>For this mode of operation, NodeJS is not required.</sub>

Simply run `python -m campaign_master --gui [--debug]`

This will launch a Qt Application where you can interface with your local file system to load relevant configuration files.

The debug flag can be used for more verbose logging.

## Web Mode

Simply run `python -m campaign_master --web [--debug]`

The debug flag can be used for more verbose logging.
**NOTE:** in this use case, it also launches the development server using `uvicorn`. See the `host` (default: `127.0.0.1` aka `localhost`) and `port` (default: `8000`) arguments.


## Technologies Used
#### General
  - **[nginx](https://nginx.org/)** (production server, wip)
  - None more anticipated.
#### Python
  - **[Pydantic](https://docs.pydantic.dev/latest/)** (Business logic)
  - **[FastAPI](https://fastapi.tiangolo.com/)** (Serving business logic)
  - **[uvicorn](https://uvicorn.dev/)** (local development server)
  - **[PySide6](https://doc.qt.io/qtforpython-6/)** (Qt framework for client-side interface app)
  - More to be added as developed.
#### React
  - **[RSBuild](https://rsbuild.rs/)** (Pre-compilation of app before serving)
  - **[TypeScript](https://www.typescriptlang.org/docs/handbook/react.html)** (TypeScript flavored React, see their [documentation](https://react.dev/learn/typescript))
  - More to be added as developed.

