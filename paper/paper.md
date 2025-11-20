---
title: "Nexarag: Democratizing Reproducible Knowledge Graph Contexts for LLM Research"
tags:
  - knowledge-graphs
  - RAG
  - LLM
  - Neo4j
  - MCP
authors:
  - name: Thomas J. Kerby
    affiliation: 1
  - name: Benjamin N. Fuller
    affiliation: 3
  - name: Kevin R. Moon
    affiliation: 2
affiliations:
  - name: Brigham Young University, Provo, UT
    index: 1
  - name: Utah State University, Logan, UT
    index: 2
  - name: Independent Researcher
    index: 3
date: 2025-11-04
bibliography: paper.bib
---

# Summary

Large language models (LLMs) are widely used in research workflows but struggle with hallucinations, short context windows, and weak reproducibility in literature reviews [@Ji2023; @Huang2025]. Nexarag is a modular, open‑source platform that lets researchers curate, visualize, and share custom knowledge graphs (KGs) from academic sources stored in Neo4j [@neo4j2024database]. Through native support for the Model Context Protocol (MCP), any MCP‑compatible LLM can access these curated KGs for controllable, reproducible context injection [@anthropic2024mcp; @mcp2024github]—including fully private, air‑gapped deployments via containers [@boettiger2015docker]—so teams can explore literature more deeply and transparently. Nexarag provides interactive graph/semantic visualizations using Cytoscape.js and D3 [@franz2023cytoscape; @bostock2011d3].

# Statement of need

Traditional retrieval‑augmented generation (RAG) systems rely primarily on embedding‑based similarity [@Lewis2020; @Guu2020; @reimers-2019-sentence-bert], which often misses long‑range semantic structure and relationships across documents, especially in long‑context, multi‑document settings [@wang-etal-2024-leave; @gao2023retrieval]. This weakens controllability, auditability, and reproducibility for complex research tasks. Knowledge graphs provide a structured and interpretable alternative by modeling entities and relations explicitly [@reinanda2020knowledge]. However, existing KG‑powered tooling is either proprietary and expensive or technically demanding to deploy and maintain. Nexarag fills this gap with a researcher‑friendly platform that automates KG creation from academic inputs, supports semantic exploration, and standardizes LLM access via MCP [@anthropic2024mcp], enabling reproducible literature synthesis across local and cloud settings.

# State of the field

RAG improves access to external knowledge and has become a standard strategy for knowledge‑intensive NLP [@Lewis2020; @Guu2020; @gao2023retrieval], yet it struggles with long contexts and multi‑step reasoning when similarity search is the only primitive [@wang-etal-2024-leave]. KGs address this by enabling path‑based queries and explicit relation reasoning while preserving transparency and updatability [@reinanda2020knowledge; @sahlab2022knowledge; @Xu2024]. Nexarag’s contribution is to operationalize these advantages in a package that researchers can run locally, share with collaborators, and connect to a wide range of LLM hosts through MCP [@anthropic2024mcp].

# Software overview

**Core capabilities.** Nexarag provides: (i) automated KG construction from BibTeX, paper lists, search queries, and citation expansion (Semantic Scholar integration) [@Kinney2023TheSS; @semanticscholar2024api]; (ii) Neo4j‑backed storage and Cypher querying [@neo4j2024database]; (iii) interactive graph and semantic visualizations (Cytoscape.js and D3.js) [@franz2023cytoscape; @bostock2011d3]; and (iv) an AI “Talk To Your Data” interface that supports both simple retrieve‑and‑generate and ReAct‑style agentic workflows [@yao2022react].

**Architecture.** The system uses a containerized, microservices design orchestrated with Docker Compose [@merkel2014docker; @docker2024]. Primary services include: a FastAPI service for HTTP coordination [@fastapi2024], a Neo4j database for graph storage [@neo4j2024database], and a Knowledge Graph service for document processing/embeddings/AI tasks. Services communicate asynchronously via RabbitMQ, enabling horizontal scaling [@rabbitmq2024].

**MCP integration.** Nexarag ships an MCP‑compatible server that exposes graph querying, semantic search over embedded content, and external search via Semantic Scholar to any MCP‑enabled LLM (local via Ollama or remote via hosted providers) [@anthropic2024mcp; @mcp2024github; @ollama2024; @openai2023api]. This standardizes context delivery and promotes reproducible prompt‑driven research workflows.

**Install & minimal run.** (see repository docs for full instructions)

```bash
# CPU example
docker compose -f docker-compose.cpu.yml up -d
# or on macOS
docker compose -f docker-compose.macos.yml up -d
```

Optionally pull local models for embedding/LLM integration with Ollama [@ollama2024]; for example, a long‑context text embedder like Nomic Embed [@nussbaum2025nomic]:

```bash
# inside the Ollama container or on macOS host
ollama pull nomic-embed-text:v1.5
ollama pull gemma3:1b
```

**Repository:** [https://github.com/REPLACE-WITH-YOUR-ORG/nexarag](https://github.com/KevinMoonLab/Nexarag)

**License:** GNU General Public License v3.0.

# Quality control

Nexarag emphasizes verifiable operation through containerized deployment and a guided quick start [@boettiger2015docker]. Reviewers can launch the full stack with Docker Compose, query/persist KGs in Neo4j, and exercise end‑to‑end flows (semantic search, citation expansion, MCP tools). A worked MCP chat transcript and an automatically generated literature review illustrate that the system’s graph building, retrieval, and reporting features execute as described. The repository includes example datasets/notebooks and scripts for running tests where applicable, supporting broader reproducibility goals in research practice [@rothacher2023eleven].

# Use cases

- **Reproducible literature reviews.** Build a KG from a seed set (e.g., via BibTeX), expand by citations, and generate a structured review through the MCP interface [@sahlab2022knowledge]. 
- **Private research contexts.** Run entirely offline (air‑gapped) with local LLMs for sensitive domains (e.g., healthcare, legal, proprietary research) [@boettiger2015docker].
- **Collaborative curation.** Share/export/import graphs across teams to support longitudinal projects.

# Acknowledgements

We acknowledge the open‑source ecosystems behind Neo4j, Cytoscape.js, D3.js, RabbitMQ, FastAPI, Ollama, and the Model Context Protocol, as well as contributors and users who provided feedback during development. This research was supported in part by the NSF under Grant 221235.

# References
