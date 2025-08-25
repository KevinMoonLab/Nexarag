# Overview

Nexarag is an open-source platform for ingesting research papers, building knowledge graphs, and querying them with agentic AI.

# Feedback

We are actively seeking feedback for Nexarag, including feature requests, issue reports, training material, etc. Please submit to `nexarag.ai@gmail.com`.

# Pre-Requisites
- [Docker](https://docs.docker.com/engine/install/)
- **(Windows Only)** [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
- **(MacOS Only)** [Ollama Desktop](https://ollama.com/download/mac)
- **(Optional)** [Claude Desktop (for MCP)](https://claude.ai/download)

# Local Deployment

## 0. Clone the Repository

```
git clone https://github.com/KevinMoonLab/Nexarag.git
cd Nexarag
```

## 1. Docker Compose

### Linux/WSL

Use the appropriate file for your hardware:

* **CPU:**

  ```
  docker compose -f docker-compose.cpu.yml up -d
  ```
* **GPU:**

  ```
  docker compose -f docker-compose.gpu.yml up -d
  ```

### MacOS

```
docker compose -f docker-compose.macos.yml up -d
```

## 2. Pull Ollama Models

Browse the full library of Ollama models [here](https://ollama.com/library). The `nomic-embed-text:v1.5` model is required. A language model is also required for LLM integration, and we recommend `gemma3:1b` as a default option. However, this can be easily replaced with another supported language model depending on your hardware and preferences.

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

## 4. (Optional) MCP Integration
Add the following to your Claude Desktop Config:
```
{
    "mcpServers": {
        "nexarag": {
            "command": "npx",
            "args": [
            "-y",
            "mcp-remote",
            "http://localhost:9000/mcp"
            ],
            "env": {
            "MCP_TRANSPORT_STRATEGY": "http-only"
            }
        }
    }
}
```

# Semantic Scholar
Please note that we are rate-limited by the Semantic Scholar API, so enriching BibTex uploads with data and updating the graph after adding papers from a Semantic Scholar search may take several minutes to complete.
