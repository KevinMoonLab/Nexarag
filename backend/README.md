# Overview
This is the backend stack consisting of three primary services that communicate asynchronously over RabbitMQ:
- `api`: FastAPI that services frontend queries and integrates with backend services
- `db`: Subscribes to frontend and system commands and events (for creating papers, authors, chat messages, etc.) and persists to the `neo4j` database.
- `kg`: Primary service for creating embeddings, interacting with LLMs, and building visualizations.

# Build & Run
Development for the backend project can be done inside a devcontainer. The container will be automatically provisioned with a `neo4j` database, a `rabbitmq` instance, and the official Ollama container image. 

1. Copy the `.env.example` file into `Nexarag/.devcontainer/.env`, modifying the values for your system
2. Open `Nexarag` in VS Code
3. Press `Ctrl+Shift+P` and type `Open Folder in Container`

Jupyter Lab will be run automatically inside `nexarag.dev`. Use the `python 3.11.11` kernel to run Jupyter notebooks.