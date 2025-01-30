# Overview
Nexarag is a tool for interacting with research literature.

# Pre-Requisites
- [Docker](https://docs.docker.com/engine/install/)

# Run
First copy `Nexarag/.env.example` to `Nexarag/.env`, modifying the settings as needed.

```
docker compose up -d --build
```

# Development
## Backend
Development for the backend project can be done inside a devcontainer. The container will be automatically provisioned with a `neo4j` database and a `rabbitmq` instance. 

1. Copy the `.env.example` file into `Nexarag/.devcontainer/.env`, modifying the values for your system
2. Open `Nexarag` in VS Code
3. Press `Ctrl+Shift+P` and type `Open Folder in Container`

Jupyter Lab will be run automatically inside `litreview.devcontainer`. Use the `python 3.11.11` kernel to run Jupyter notebooks.

## Frontend
The frontend application can be deployed in two ways: as static HTML and JS files served by `nginx` in the `litreview.frontend` container, or in Angular development server mode.

### First Time Deployment
1. Install [NVM](https://github.com/nvm-sh/nvm) for your platform (Linux is much easier)
2. Install [NPM](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
3. In the `litreview` root, run `npm install`

### Running the Development Server
1. Run the application stack from the root using `docker compose`. The API will be served at `http://localhost:8000`
2. In `Nexarag/frontend`, run `npx nx s`. The application will be available (with live reloads) at `http://localhost:4200`

# Useful Commands
|Command|Description|
|-|-|
|`docker compose logs --follow` | Show all logs from all containers in the compose stack|
|`docker container logs litreview.kg --follow` | Show logs for a specific container|
|`docker compose stats` | Monitor research usage in compose stack |
