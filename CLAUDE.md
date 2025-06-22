# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nexarag is an open-source platform for ingesting research papers, building knowledge graphs, and querying them with agentic AI. The system enables users to upload papers, generate semantic embeddings, and leverage these representations for intelligent querying through a "Talk To Your Data" (TTYD) interface.

## Architecture

The system consists of containerized microservices communicating asynchronously via RabbitMQ:

### Backend Services
- **API Service** (`backend/src/api/`): FastAPI server exposing REST endpoints for frontend interactions
- **Database Service** (`backend/src/db/`): Manages Neo4j graph database operations using neomodel OGM
- **Knowledge Graph Service** (`backend/src/kg/`): Handles embeddings, LLM interactions, and knowledge graph construction
- **RabbitMQ Service** (`backend/src/rabbit/`): Message queue event handling
- **Scholar Service** (`backend/src/scholar/`): Semantic Scholar API integration

### Frontend
- **Angular Application** (`frontend/`): Web interface built with Angular 19, using Cytoscape.js for graph visualization and Plotly.js for semantic plots

### Infrastructure
- **Neo4j**: Graph database for storing research papers, citations, authors, and relationships
- **RabbitMQ**: Asynchronous message queue for inter-service communication
- **Ollama**: Local LLM inference (requires `nomic-embed-text:v1.5` embedding model)

## Development Commands

### Docker Deployment
```bash
# Linux/WSL
docker compose up -d

# MacOS
docker compose -f docker-compose.macos.yml up -d
```

### Backend Development
Backend development uses Poetry and can be done in a devcontainer:
```bash
# Install dependencies
cd backend && poetry install

# Run Jupyter Lab (available in devcontainer)
# Use python 3.11.11 kernel for notebooks
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Development server (with live reload)
npx nx serve
# Access at http://localhost:4200

# Build for production
nx build

# Run tests
nx test

# Lint code
nx lint
```

### Ollama Models
Required models for LLM functionality:
```bash
# Linux/WSL (inside container)
docker exec -it nexarag.ollama /bin/bash
ollama pull nomic-embed-text:v1.5
ollama pull gemma3:1b

# MacOS (local)
ollama pull nomic-embed-text:v1.5
ollama pull gemma3:1b
```

### Monitoring
```bash
# View all container logs
docker compose logs --follow

# View specific service logs
docker container logs nexarag.kg --follow

# Monitor resource usage
docker compose stats
```

## Key Technologies

### Backend Stack
- **Python 3.10+** with Poetry for dependency management
- **FastAPI** for REST API with async support
- **Neo4j** graph database with neomodel OGM
- **RabbitMQ** for message queuing (aio-pika)
- **LangChain** for LLM orchestration and RAG
- **PyMuPDF4LLM** for document processing
- **Transformers & Sentence-Transformers** for embeddings

### Frontend Stack
- **Angular 19** with TypeScript
- **Nx** monorepo tooling
- **Cytoscape.js** for interactive graph visualization
- **Plotly.js** for semantic plotting and PCA visualizations
- **PrimeNG** UI component library
- **Tailwind CSS** for styling
- **Jest** for unit testing

## Service Ports
- Frontend: http://localhost:5000 (production) / http://localhost:4200 (dev)
- API: http://localhost:8000
- Neo4j Browser: http://localhost:7474 (neo4j/password)
- RabbitMQ Management: http://localhost:15672 (guest/guest)
- Ollama: http://localhost:11434

## Database Configuration
- Neo4j URI: `bolt://localhost:7687` (or `bolt://nexarag.neo4j:7687` in containers)
- Username: `neo4j`
- Password: `password`
- Database: `neo4j`

## Development Workflow
1. Start infrastructure with Docker Compose
2. For backend: Use devcontainer or local Poetry environment
3. For frontend: Use `nx serve` for development server with live reload
4. Services communicate via RabbitMQ - check logs for debugging inter-service issues
5. Use Jupyter notebooks in `backend/notebooks/` for data exploration and prototyping