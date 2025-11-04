---
title: "Nexarag: Democratizing Reproducible Knowledge Graph Contexts for LLM Research"
tags:
  - knowledge-graphs
  - RAG
  - LLM
  - Neo4j
  - MCP
authors:
  - name: TODO: First Author
    affiliation: 1
  - name: TODO: Second Author
    affiliation: 1
affiliations:
  - name: TODO: Your Institution, City, Country
    index: 1
date: 2025-11-04
bibliography: paper.bib
---

# Summary

Large language models (LLMs) are widely used in research workflows but struggle with hallucinations, short context windows, and weak reproducibility in literature reviews. Nexarag is a modular, open‑source platform that lets researchers curate, visualize, and share custom knowledge graphs (KGs) from academic sources stored in Neo4j. Through native support for the Model Context Protocol (MCP), any MCP‑compatible LLM can access these curated KGs for controllable, reproducible context injection—including fully private, air‑gapped deployments—so teams can explore literature more deeply and transparently.

# Statement of need

Traditional retrieval‑augmented generation (RAG) systems rely primarily on embedding similarity, which often misses long‑range semantic structure and relationships across documents. This weakens controllability, auditability, and reproducibility for complex research tasks. Knowledge graphs provide a structured and interpretable alternative by modeling entities and relations explicitly. However, existing KG‑powered tooling is either proprietary and expensive or technically demanding to deploy and maintain. Nexarag fills this gap with a researcher‑friendly platform that automates KG creation from academic inputs, supports semantic exploration, and standardizes LLM access via MCP, enabling reproducible literature synthesis across local and cloud settings.

# State of the field (brief)

RAG improves access to external knowledge but struggles with long contexts and multi‑step reasoning when similarity search is the only primitive. KGs address this by enabling path‑based queries and explicit relation reasoning while preserving transparency and updatability. Nexarag’s contribution is to operationalize these advantages in a package that researchers can run locally, share with collaborators, and connect to a wide range of LLM hosts through MCP.

# Software overview

**Core capabilities.** Nexarag provides: (i) automated KG construction from BibTeX, paper lists, search queries, and citation expansion (Semantic Scholar integration); (ii) Neo4j‑backed storage and Cypher querying; (iii) interactive graph and semantic visualizations (Cytoscape.js and D3.js); and (iv) an AI “Talk To Your Data” interface that supports both simple retrieve‑and‑generate and ReAct‑style agentic workflows.

**Architecture.** The system uses a containerized, microservices design orchestrated with Docker Compose. Primary services include: a FastAPI service for HTTP coordination, a Neo4j database for graph storage, and a Knowledge Graph service for document processing/embeddings/AI tasks. Services communicate asynchronously via RabbitMQ, enabling horizontal scaling.

**MCP integration.** Nexarag ships an MCP‑compatible server that exposes graph querying, semantic search over embedded content, and external search via Semantic Scholar to any MCP‑enabled LLM (local via Ollama or remote via hosted providers). This standardizes context delivery and promotes reproducible prompt‑driven research workflows.

**Install & minimal run.** (see repository docs for full instructions)

```bash
# CPU example
docker compose -f docker-compose.cpu.yml up -d
# or on macOS
docker compose -f docker-compose.macos.yml up -d
```

Optionally pull local models for embedding/LLM integration with Ollama:

```bash
# inside the Ollama container or on macOS host
ollama pull nomic-embed-text:v1.5
ollama pull gemma3:1b
```

**Repository:** <https://github.com/REPLACE-WITH-YOUR-ORG/nexarag>  
**License:** OSI‑approved license (e.g., MIT/Apache‑2.0/BSD‑3‑Clause).

# Quality control

Nexarag emphasizes verifiable operation through containerized deployment and a guided quick start. Reviewers can launch the full stack with Docker Compose, query/persist KGs in Neo4j, and exercise end‑to‑end flows (semantic search, citation expansion, MCP tools). A worked MCP chat transcript and an automatically generated literature review illustrate that the system’s graph building, retrieval, and reporting features execute as described. The repository should include example datasets/notebooks and scripts for running tests where applicable.

# Use cases (optional)

- **Reproducible literature reviews.** Build a KG from a seed set (e.g., via BibTeX), expand by citations, and generate a structured review through the MCP interface.  
- **Private research contexts.** Run entirely offline (air‑gapped) with local LLMs for sensitive domains (e.g., healthcare, legal, proprietary research).  
- **Collaborative curation.** Share/export/import graphs across teams to support longitudinal projects.

# Acknowledgements

We acknowledge the open‑source ecosystems behind Neo4j, Cytoscape.js, D3.js, RabbitMQ, FastAPI, Ollama, and the Model Context Protocol, as well as contributors and users who provided feedback during development.

# References

Please place bibliographic entries for works discussed in a `paper.bib` file and cite them inline (e.g., `@key`). For submission, ensure all citation keys resolve and that venues are written out in full.
