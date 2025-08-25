# Overview 
This is the Angular frontend web application for Nexarag.

## First Time Deployment
1. Install [NVM](https://github.com/nvm-sh/nvm) for your platform (Linux is recommended for local development)
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
