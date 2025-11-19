# Advanced Configuration
A number of advanced settings can be applied using environment variables. Copy [.env.example](https://github.com/KevinMoonLab/Nexarag/blob/bnf/make-docs/docker/.env.example) into the same folder as your docker compose file, and modify the values as needed.


## Environment Variables
| Name                      | Default                 | Description                                                                                                   |
| ------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------- |
| `COMPOSE_PROJECT_NAME`    | `nexarag`               | Overrides the default Docker Compose project name to group containers under a unified prefix.                 |
| `NEO4J_USERNAME`          | `neo4j`                 | Username for authenticating with the Neo4j database.                                                          |
| `NEO4J_PASSWORD`          | `password`              | Password for the Neo4j user.                                                                                  |
| `RABBITMQ_USERNAME`       | `guest`                 | Username for connecting to RabbitMQ.                                                                          |
| `RABBITMQ_PASSWORD`       | `guest`                 | Password for the RabbitMQ user.                                                                               |
| `API_PORT`                | `8000`                  | Port exposed by the API service.                                                                              |
| `FRONTEND_PORT`           | `5000`                  | Port for serving the frontend application.                                                                    |
| `OLLAMA_PORT`             | `11434`                 | Port used by the Ollama server for model inference.                                                           |
| `MCP_PORT`                | `9000`                  | Port for the MCP service.                                                                                     |
| `EMBEDDING_CHUNK_SIZE`    | `500`                   | Size of text chunks (in characters or tokens, depending on implementation) used before generating embeddings. |
| `EMBEDDING_CHUNK_OVERLAP` | `100`                   | Number of overlapping characters/tokens between embedding chunks to preserve context.                         |
| `EMBEDDING_MODEL`         | `nomic-embed-text:v1.5` | Model identifier used for generating vector embeddings.                                                       |
