# Overview 
Frontend Angular application that provides [Cytoscape.js](https://js.cytoscape.org/) and [D3.js](https://d3js.org/) visualizations of Nexarag knowledge graphs. Also provides graph-building features, [Semantic Scholar](https://www.semanticscholar.org/) integration, and LLM talk-to-your-data (TTYD) chat capabilities. The `frontend` service in the compose stack serves the static Angular files and routes API requests via `nginx`.

# Local Development
## First Deployment
1. Install [NVM](https://github.com/nvm-sh/nvm) for your platform (Linux is recommended for local development)
2. Install [NPM](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
3. In `Nexarag/frontend`, run `npm install`

## Running the Development Server
1. Run the application stack from the root using `docker compose`. The API will be served at `http://localhost:8000`
2. In `Nexarag/frontend`, run `npx nx s`. The application will be available (with live reloads) at `http://localhost:4200`
