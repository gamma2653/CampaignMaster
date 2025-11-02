# Camp-Plan

A companion application for game masters of various TTRPG formats. This application allows a game master to plan, and then subsequently execute a game plan for player sessions. As development continues, support for additional game mechanics will be added, via a "Rules" framework, more to come later.

As far as game masters are concerned, running a TTRPG campaign is associated with two primary actitivies: preparation (planning), and execution (running the campaign with players).

This application breaks down this process into two clean steps. First, the user is able to plan out their campaign, or at least some overarching critical storypoints. Notably, the plan will be able to be modified on the fly, with new branches able to be spun off, and a notion of "executed" storypoints.

To fit this theme, the "installation" and "usage" instructions are outlined below, as "Preparation" and "Execution."

## Preperation

### Python
<sub>This installation section is required.</sub>

#### Requirements

1. Ensure poetry is installed on your system as per their websites [instructions](https://python-poetry.org/docs/#installing-with-the-official-installer).
    - Configure your preferred virtualenv defaults before proceeding.

2. Run `poetry install`

3. Activate your poetry environment. [Poetry's instructions](https://python-poetry.org/docs/managing-environments#powershell)


### React/NodeJS
<sub>Note: First complete the above [Python setup](#python)</sub>
<sub>This section is optional; it is only required if you intend to use the `web` functionality.</sub>

1. Ensure NodeJS is installed on your system, giving access to the `npm` command.
    - On Windows, you can use the `winget install --id OpenJS.NodeJS --source winget` command (assuming the ID has not changed as of 10/09/25) to install the appropriate build.



## Execution

- Run `python -m campaign_master -h` to see more exhaustive usage information.

<p>This module can first and foremost be run in two different ways, as a local applet (a Qt application), or as a web server.</p>
<sub>The switch from serving via FastAPI to serving via Qt is considered trivial thanks to the build step. If a hybrid mode is desired, just serve the static files via Qt.</sub>

### App Mode
<sub>For this mode of operation, NodeJS is not required.</sub>

Simply run `python -m campaign_master --gui [--debug]`

This will launch a Qt Application where you can interface with your local file system to load relevant configuration files.

The debug flag can be used for more verbose logging.

### Web Mode

Simply run `python -m campaign_master --web [--debug]`

The debug flag can be used for more verbose logging.
**NOTE:** in this use case, it also launches the development server using `uvicorn`. See the `host` (default: `127.0.0.1` aka `localhost`) and `port` (default: `8000`) arguments.


### Technologies Used
##### General
  - **[nginx](https://nginx.org/)** (production server, wip)
  - None more anticipated.
##### Python
  - **[Pydantic](https://docs.pydantic.dev/latest/)** (Business logic)
  - **[FastAPI](https://fastapi.tiangolo.com/)** (Serving business logic)
  - **[uvicorn](https://uvicorn.dev/)** (local development server)
  - **[PySide6](https://doc.qt.io/qtforpython-6/)** (Qt framework for client-side interface app)
  - More to be added as developed.
##### React
  - **[RSBuild](https://rsbuild.rs/)** (Pre-compilation of app before serving)
  - **[TypeScript](https://www.typescriptlang.org/docs/handbook/react.html)** (TypeScript flavored React, see their [documentation](https://react.dev/learn/typescript))
  - **[Tanstack](https://tanstack.com)**
  - More to be added as developed.

