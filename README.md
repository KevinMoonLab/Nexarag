# Overview
Nexarag is a tool for interacting with research literature.

# Pre-Requisites
- [Docker](https://docs.docker.com/engine/install/)

# Run
First copy `Nexarag/.env.example` to `Nexarag/.env`, modifying the settings as needed to configure volumes.

```
docker compose up -d --build
```

# Pull Ollama Models
Models can be pulled through the command line and will be stored on the volume specified by the `OLLAMA_VOLUME` environment variable.

```
docker exec -it ollama /bin/bash
ollama pull nomic-embed-text:v1.5
ollama pull gemma3:1b
```

# Development
## Backend
Development for the backend project can be done inside a devcontainer. The container will be automatically provisioned with a `neo4j` database, a `rabbitmq` instance, and the official Ollama container image. 

1. Copy the `.env.example` file into `Nexarag/.devcontainer/.env`, modifying the values for your system
2. Open `Nexarag` in VS Code
3. Press `Ctrl+Shift+P` and type `Open Folder in Container`

Jupyter Lab will be run automatically inside `nexarag.dev`. Use the `python 3.11.11` kernel to run Jupyter notebooks.

## Frontend
### First Time Deployment
1. Install [NVM](https://github.com/nvm-sh/nvm) for your platform (Linux is much easier)
2. Install [NPM](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
3. In `Nexarag/frontend`, run `npm install`

### Running the Development Server
1. Run the application stack from the root using `docker compose`. The API will be served at `http://localhost:8000`
2. In `Nexarag/frontend`, run `npx nx s`. The application will be available (with live reloads) at `http://localhost:4200`

# Useful Commands
|Command|Description|
|-|-|
|`docker compose logs --follow` | Show all logs from all containers in the compose stack|
|`docker container logs litreview.kg --follow` | Show logs for a specific container|
|`docker compose stats` | Monitor research usage in compose stack |
