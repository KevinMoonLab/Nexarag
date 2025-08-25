# Overview
This is the backend stack consisting of four primary services that communicate asynchronously over RabbitMQ:
- `api`: FastAPI that services frontend queries and integrates with backend services
- `kg`: Primary service for creating embeddings, interacting with LLMs, and building visualizations.
- `rabbit`: Defines the messaging layer between services.
- `scholar`: Semantic Scholar integration.
- `mcp`: Provides MCP access to the API and context generation for external LLM hosts.

# Build & Run
Development for the backend project can be done inside a devcontainer. The container will be automatically provisioned with a `neo4j` database, a `rabbitmq` instance, and the official Ollama container image. 

1. Copy the `.env.example` file into `Nexarag/.devcontainer/.env`, modifying the values for your system
2. Open `Nexarag` in VS Code
3. Press `Ctrl+Shift+P` and type `Open Folder in Container`

Jupyter Lab will be run automatically inside `nexarag.dev`. Use the `python 3.11.11` kernel to run Jupyter notebooks.
