# Overview
Nexarag is an open‑source platform for ingesting research papers, building knowledge graphs, and querying them with agentic AI.

# Feedback
We are actively seeking feedback for Nexarag, including feature requests, issue reports, training material, etc. Please submit to `nexarag.ai@gmail.com`. 

# Pre-Requisites
- [Docker](https://docs.docker.com/engine/install/)
- **(Windows Only)** [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
- **(MacOS Only)** [Ollama Desktop](https://ollama.com/download/mac)

# Local Deployment
## 1. Docker Compose
### Linux/WSL
```
docker compose up -d --build
```

### MacOS
```
docker compose -f docker-compose.macos.yml up -d
```

## 2. Pull Ollama Models
Browse the full library of Ollama models [here](https://ollama.com/library). The following are required; pull any other models that your hardware supports for LLM integration.

### Linux/WSL
Models can be pulled through the command line in the `ollama` Docker container. 

```
docker exec -it nexarag.ollama /bin/bash
ollama pull nomic-embed-text:v1.5
ollama pull gemma3:1b
```

### MacOS
Pull models directly from your command line.

```
ollama pull nomic-embed-text:v1.5
ollama pull gemma3:1b
```

## 3. Launch Application
The Nexarag frontend application will be served at `http://localhost:5000`.

# Semantic Scholar
Please note that we are rate-limited by the Semantic Scholar API, so enriching BibTex uploads with data and updating the graph after adding papers from a Semantic Scholar search may take several minutes to complete.
