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

## Backend Architecture Details

### Service Communication Patterns
Services communicate asynchronously via RabbitMQ using fan-out exchanges with durable queues. Each service subscribes to relevant channels and publishes events/commands using Pydantic models:

```python
# Publishing pattern
await publish_message(ChannelType.ADD_PAPER, AddPapersById(paper_ids=papers))

# Subscription pattern  
await subscribe_to_queue(ChannelType.GRAPH_UPDATED, handle_update_result, GraphUpdated)
```

### Database Layer Architecture
The database service (`backend/src/db/`) was moved from `backend/src/kg/db/` and uses:
- **Neomodel OGM** with `AsyncStructuredNode` for all models
- **Vector embeddings** with 768-dimension cosine similarity indices  
- **Key models**: Paper (with embeddings), Author, PublicationVenue, Document, Chat entities, Tag
- **Connection management** using context managers for database operations

### Backend Development Commands
```bash
# Backend testing (when available)
cd backend && poetry run pytest

# Run specific service for debugging
cd backend/src && python -m api.main  # API service
cd backend/src && python -m kg.main   # Knowledge graph service

# Database operations
# Access Neo4j directly: http://localhost:7474 (neo4j/password)
# RabbitMQ management: http://localhost:15672 (guest/guest)
```

## Frontend Architecture Details

### Component Architecture
The Angular 19 application uses standalone components with signal-based state management:

- **Shell Structure**: AppComponent → ShellComponent → ViewportComponent
- **Main Components**: GraphComponent (Cytoscape.js), PlotComponent (Plotly.js), ChatComponent, MenuComponent
- **State Management**: GraphStore (signals), ChatService, EventService (WebSocket)

### Visualization Libraries Integration
- **Cytoscape.js**: Graph visualization with context menus, dynamic layouts, node selection syncing
- **Plotly.js**: PCA visualization of document embeddings with interactive scatter plots
- **Real-time updates**: WebSocket events drive UI updates (graph_updated, chat_response)

### Frontend Development Commands
```bash
cd frontend

# Specific testing commands
nx test --watch                    # Watch mode testing
nx test --coverage                 # Coverage reports
nx build --configuration=production  # Production build

# Linting and formatting
nx lint --fix                      # Auto-fix linting issues
```

## Development Environment Setup

### DevContainer Development
The project includes a devcontainer configuration for backend development:
```bash
# Start devcontainer services
cd .devcontainer && docker compose up -d

# Jupyter Lab will be available at http://localhost:8888
# Use Python 3.11.11 kernel for notebooks
```

### Database Service Location
**Important**: Database models and queries are located in `backend/src/db/` (not `backend/src/kg/db/`). This includes:
- `models.py`: Neomodel AsyncStructuredNode definitions
- `queries.py`: Database query operations  
- `builder.py`: Graph construction logic

## Common Development Issues
- **Tag Model**: Ensure Tag class exists in `backend/src/db/models.py` when adding tag relationships to Paper
- **Ollama Models**: Required models must be pulled before LLM functionality works
- **Rate Limiting**: Semantic Scholar API is rate-limited; graph updates may take several minutes
- **Service Dependencies**: Services depend on Neo4j and RabbitMQ health checks