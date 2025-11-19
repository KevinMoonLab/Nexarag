# System Overview

**Nexarag** is a platform for exploring and interacting with research literature through dynamic knowledge graphs. It enables users to upload papers, generate semantic embeddings, and leverage these representations for intelligent querying and visual exploration.

## ✨ Key Features

- **Build Knowledge Graphs** from references, citations, authors, venues, BibTex files, etc.
- **Attach documents** (e.g., full paper text) to graph nodes to create rich semantic embeddings and relationships
- **Talk To Your Data (TTYD)** via LLM-powered Retrieval-Augmented Generation (RAG)
- **Semantic Visualizations** like PCA projections of the semantic graph to explore research trajectories, gaps, and growth

---

## 🧱 Architecture Overview

Nexarag consists of two primary layers: **Frontend** and **Backend**. All components are containerized using Docker and communicate asynchronously via **RabbitMQ**.

### 📦 Backend Architecture

The backend is composed of three core services:

#### 1. **FastAPI Service**
- **Purpose**: Exposes REST endpoints to handle frontend requests such as paper uploads, graph queries, and TTYD chat requests.
- **Why FastAPI?**: Chosen for its excellent performance, developer-friendly async support, and native support for OpenAPI documentation.
- **Role in System**: Acts as the interface layer, dispatching tasks to other backend services and coordinating responses to the frontend.

#### 2. **Database Service (Neo4j)**
- **Purpose**: Stores the core knowledge graph, including relationships like _cited by_, _authored by_, and _published in_, as well as semantic embeddings for node content and associated documents. Uses `neomodel` as the Object-Graph Mapper (OGM) to simplify the research literature domain-specific language (DSL). 
- **Why Neo4j?**: Graphs are the natural data model for this domain. Neo4j allows efficient traversal, querying, and expansion of literature networks.
- **Semantic Embedding Support**: Embeddings from the LLM are stored alongside graph nodes, enabling vector similarity search and semantic clustering.

#### 3. **Knowledge Graph Service**
- **Purpose**: Handles all knowledge-centric operations — from querying Semantic Scholar to constructing knowledge graphs, computing embeddings, and processing TTYD (Talk To Your Data) interactions.
- **Why a dedicated service?**: Separating this logic allows for scalability and easier integration with different data sources and models.
- **LLM Integration**: Uses transformer-based language models to generate embeddings and power TTYD features via Retrieval-Augmented Generation (RAG).

#### 🔁 Inter-Service Communication
- **Mechanism**: All backend services communicate asynchronously using **RabbitMQ**.
- **Why RabbitMQ?**: Enables decoupled, event-driven processing of tasks like embedding generation, document parsing, and graph updates. Improves scalability and reliability by preventing tight coupling between services with high message durability.

---

### 🌐 Frontend Architecture

- Built with **Angular**
- Visualizes knowledge graphs using **Cytoscape.js**
- Renders semantic plots using **D3.js**
- Connects to the backend via REST endpoints and web sockets provided by the FastAPI service

---

## 🧠 Technology Stack

| Layer         | Technology                            |
|--------------|----------------------------------------|
| Frontend     | Angular, Cytoscape.js, D3.js           |
| Backend API  | FastAPI (Python)                       |
| Graph DB     | Neo4j, neomodel                        |
| Messaging    | RabbitMQ                               |
| Orchestration| Docker + Docker Compose                |

