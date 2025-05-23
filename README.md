# Overview
Nexarag is an open‑source platform to ingest research papers, build knowledge graphs, and query them with agentic AI.

# Pre-Requisites
- **(Windows Only)** [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Docker](https://docs.docker.com/engine/install/)
- **(MacOS Only)** [Ollama](https://ollama.com/download/mac)

# Run
## Linux/WSL
```
docker compose up -d --build
```

## MacOS
```
docker compose -f docker-compose.macos.yml up -d
```

# Pull Ollama Models
## Linux/WSL
Models can be pulled through the command line and will be stored on the volume specified by the `OLLAMA_VOLUME` environment variable.

```
docker exec -it ollama /bin/bash
ollama pull nomic-embed-text:v1.5
ollama pull gemma3:1b
```

## MacOS
Pull models from the command line:

```
ollama pull nomic-embed-text:v1.5
ollama pull gemma3:1b
```