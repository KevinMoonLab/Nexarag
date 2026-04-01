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


## Statement of need

Retrieval-augmented generation (RAG) has become a standard approach for knowledge-intensive NLP [@Lewis2020; @Guu2020; @gao2023retrieval], but systems built primarily on embedding-based similarity [@Lewis2020; @Guu2020; @reimers-2019-sentence-bert] can miss long-range semantic structure and cross-document relationships, especially in long-context and multi-document settings [@wang-etal-2024-leave; @gao2023retrieval]. For literature synthesis and related research workflows, this limits transparency, controllability, and reproducibility.

Knowledge graphs address part of this problem by representing entities and relations explicitly, enabling path-based queries and more interpretable reasoning over document collections [@reinanda2020knowledge; @sahlab2022knowledge; @Xu2024]. However, existing KG-based tooling is often either proprietary or too technically demanding for routine research use. Nexarag addresses this gap with a researcher-friendly, self-hostable platform for constructing and curating literature knowledge graphs and exposing them to language models through MCP [@anthropic2024mcp].

## State of the field

Open-source RAG frameworks such as LangChain, LlamaIndex, and Haystack provide reusable components for ingestion, indexing, and retrieve-then-generate pipelines [@langchain2026rag; @llamaindex2026rag; @haystack2026]. They are effective developer libraries, but they are mainly designed for assembling application-specific pipelines in code.

Graph-augmented retrieval tools extend this ecosystem. LlamaIndex includes a KnowledgeGraphIndex [@llamaindex2026kg], LangChain provides graph QA utilities such as GraphCypherQAChain [@langchain2026neo4j], and packages such as Microsoft GraphRAG and Neo4j GraphRAG support structured extraction and graph-aware retrieval [@microsoft2026graphrag; @neo4j2026graphrag]. These projects show the value of graph-based retrieval, but they are generally aimed at developers rather than at reproducible, literature-centered research workflows.

Literature discovery platforms such as Connected Papers, ResearchRabbit, and Litmaps support citation exploration and related-work discovery [@connectedpapers2026; @researchrabbit2026; @litmaps2026], but they do not provide a researcher-owned, versionable graph substrate for controlled LLM experiments. Nexarag sits between these tool families by packaging persistent Neo4j-based graph construction, interactive curation, and standardized model access through MCP into a self-hostable research application [@anthropic2024mcp; @mcp2024github]. It complements existing RAG and GraphRAG libraries by turning graph-based context construction into a reusable and shareable research workflow with user-friendly UI tools, visualization, and pluggable MCP integration.


# Software Design
Nexarag was designed around four principles: ease of use, flexibility, modularity, and privacy/security.

| Design choices in Nexarag | Tradeoffs |
| - | - |
|  **Ease of use**: Nexarag uses familiar frontend technologies, including Angular, D3.js, Cytoscape.js, and PrimeNg, to provide an intuitive interface for building knowledge graphs, finding papers, interacting with LLMs, and visualizing results. Nexarag is fully containerized and can be deployed with a single command. | Multiple component libraries increases frontend maintenance overhead and onboarding cost for new contributors. Container deployments add complexity and additional software dependencies (Docker). |
| **Flexibility**: Nexarag integrates with Ollama and supports any embedding model or LLM that the user’s hardware can run, making it easy to switch models across tasks or adopt new ones as they become available. Users can also connect their preferred LLM or coding agent through the built-in MCP server. | Users have more choices but also more responsibility for hardware configuration, model selection, and staying up-to-date on relevant tools and architectures. |
| **Modularity**: The system is organized as distinct services for the REST API, Neo4j knowledge graph, MCP server, and frontend application, connected through a RabbitMQ messaging backbone. This supports horizontal scaling and reduces the blast radius of changes made within any single service. | Service decomposition improves scalability and isolates changes, but increases deployment complexity, inter-service coordination, and operational overhead. |
| **Privacy and security**: Nexarag supports on-premises, air-gapped deployment, providing a level of privacy and security that cloud-based applications typically cannot offer. | Air-gapped deployments can offer heightened security and privacy, but place more burden on the user for hardware configuration, deployment, and maintenance. Local compute resources may also be limited compared to cloud services. |


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

**Repository:** [https://github.com/KevinMoonLab/Nexarag](https://github.com/KevinMoonLab/Nexarag)

**License:** GNU General Public License v3.0.

## Use cases

- **Reproducible literature reviews.** Build a KG from a seed set (e.g., via BibTeX), expand by citations, and generate a structured review through the MCP interface [@sahlab2022knowledge]. 
- **Private research contexts.** Run entirely offline (air‑gapped) with local LLMs for sensitive domains (e.g., healthcare, legal, proprietary research) [@boettiger2015docker].
- **Collaborative curation.** Share/export/import graphs across teams to support longitudinal projects.

## Quality control

Nexarag emphasizes verifiable operation through containerized deployment and a guided quick start [@boettiger2015docker]. Reviewers can launch the full stack with Docker Compose, query/persist KGs in Neo4j, and exercise end‑to‑end flows (semantic search, citation expansion, MCP tools). A worked MCP chat transcript and an automatically generated literature review illustrate that the system’s graph building, retrieval, and reporting features execute as described. The repository includes example datasets/notebooks and scripts for running tests where applicable, supporting broader reproducibility goals in research practice [@rothacher2023eleven].

# Research impact statement

Nexarag addresses a growing need in LLM-assisted research for transparent, reproducible, and inspectable context construction beyond embedding-only retrieval. While many RAG systems remain opaque and difficult to reproduce, Nexarag operationalizes knowledge-graph–based context building in a form that researchers can deploy locally, inspect visually, and share across projects. By combining Neo4j-backed knowledge graphs with standardized access through the Model Context Protocol (MCP), the software provides a reproducible bridge between structured scholarly knowledge and LLM-driven analysis.

Although Nexarag is a relatively new project and has not yet accumulated extensive downstream citations, it demonstrates credible near-term research impact through its design, documentation, and reproducible reference materials. The repository includes end-to-end examples that reproduce literature expansion, graph construction, semantic querying, and LLM-mediated synthesis from fixed inputs, allowing independent researchers to verify behavior and compare results across models and deployment environments. Containerized deployment and air-gapped operation further support use in domains where reproducibility, auditability, or data sensitivity are critical.

Nexarag is positioned to serve as shared research infrastructure for studies on retrieval-augmented generation, knowledge-graph–augmented reasoning, and AI-assisted literature review workflows. Its model-agnostic design, enabled by MCP, allows researchers to interchange local or API-hosted LLMs while holding the underlying knowledge graph and retrieval logic fixed. This supports a direct comparison of LLM behavior under identical, graph-derived contexts, facilitating methodological research on controllability, hallucination reduction, and long-context reasoning. By lowering the technical barrier to building, inspecting, and sharing reproducible knowledge graph contexts, Nexarag enables researchers to move beyond ad hoc, model-coupled RAG pipelines toward more transparent and portable AI-assisted research practices.

# AI usage disclosure
Generative AI tools were used in the development of the software, supporting code reviews, providing minor features in the frontend, and identifying and fixing bugs. Generative AI tools were also used to generate some of the documentation, and assisted with paper authoring. We primarily used:

* ChatGPT with the GPT-4o model for writing tasks
* Claude Code with the Sonnet 4 model for coding tasks

All AI-generated material was explicitly reviewed by at least one author, and all major design decisions were formalized by multiple authors. 

# Acknowledgements

We acknowledge the open‑source ecosystems behind Neo4j, Cytoscape.js, D3.js, RabbitMQ, FastAPI, Ollama, and the Model Context Protocol, as well as contributors and users who provided feedback during development. This research was supported in part by the NSF under Grant 221235.

# References
