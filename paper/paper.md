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

RAG improves access to external knowledge and has become a standard strategy for knowledge‑intensive NLP [@Lewis2020; @Guu2020; @gao2023retrieval], yet it struggles with long contexts and multi‑step reasoning when similarity search is the only primitive [@wang-etal-2024-leave]. KGs address this by enabling path‑based queries and explicit relation reasoning while preserving transparency and updatability [@reinanda2020knowledge; @sahlab2022knowledge; @Xu2024]. Nexarag’s contribution is to operationalize these advantages in a package that researchers can run locally, share with collaborators, and connect to a wide range of LLM hosts through MCP [@anthropic2024mcp].

# State of the field

The open-source ecosystem around retrieval-augmented generation (RAG) has matured quickly, with widely used orchestration frameworks such as LangChain, LlamaIndex, and Haystack providing reusable components for ingesting documents, building indexes, and implementing retrieve-then-generate pipelines [@langchain2026rag; @llamaindex2026rag; @haystack2026]. These frameworks are well suited for building bespoke RAG applications, but they are primarily developer libraries: users typically assemble pipelines in code, and the resulting “context construction” logic is often tightly coupled to a specific project’s embeddings, chunking choices, runtime configuration, and LLM host.

Graph-augmented retrieval approaches have emerged to address limitations of similarity-only retrieval for multi-document reasoning. For example, LlamaIndex provides a KnowledgeGraphIndex that supports automated knowledge graph construction from unstructured text and entity-based querying [@llamaindex2026kg]. LangChain offers graph question-answering utilities, including GraphCypherQAChain for translating natural-language questions into Cypher queries over Neo4j [@langchain2026neo4j]. Dedicated GraphRAG toolkits such as Microsoft GraphRAG and the Neo4j GraphRAG package for Python provide pipelines for extracting structured representations from text and using graph-aware retrieval strategies during LLM inference [@microsoft2026graphrag; @neo4j2026graphrag]. These projects demonstrate that knowledge graphs can improve retrieval structure and interpretability, but they are generally positioned as building blocks for developers rather than as reproducible, end-to-end research applications for literature-centric workflows.

In parallel, literature discovery tools such as Connected Papers, ResearchRabbit, and Litmaps offer citation-network visualizations and recommendations to help researchers explore related work and track research areas over time [@connectedpapers2026; @researchrabbit2026; @litmaps2026]. While valuable for interactive discovery, these tools are not designed to serve as a researcher-owned, queryable knowledge graph substrate that can be versioned, shared, and integrated as a controllable context source for LLM experiments across local and secure environments.

Nexarag fills the gap between these two tool families by packaging knowledge-graph-based context construction as a reproducible, shareable research artifact and workflow. Instead of treating graph retrieval as a code-level feature, Nexarag provides a self-hostable platform centered on a persistent Neo4j knowledge graph, interactive graph curation and visualization, and standardized LLM access through the Model Context Protocol (MCP) [@anthropic2024mcp; @mcp2024github]. This design enables researchers to hold the underlying graph context and retrieval tools fixed while varying models, prompts, and deployment settings, supporting more transparent and reproducible LLM-assisted literature synthesis.

We chose to build Nexarag rather than contribute directly to an existing RAG or GraphRAG library because our core contribution requires application-level infrastructure that is outside the scope of most libraries’ design constraints: a literature-oriented ingestion workflow (BibTeX and paper lists, citation expansion, and persistent graph storage), a collaborative and visual curation interface, containerized offline deployment, and an MCP-first tool surface for model-agnostic experimentation. Nexarag therefore complements, rather than replaces, existing RAG frameworks by providing a researcher-facing system for producing and reusing reproducible knowledge graph contexts in LLM research.

# Software Design
In designing Nexarag we focused on four principles: (1) ease-of-use (in deployment and practical application), (2) flexibility (in model selection and configuration), (3) modularity (to promote scale and independent contribution), and (4) privacy and security. For ease-of-use, we chose popular frontend technologies such as Angular, D3.js, and Cytoscape.js and leveraged existing component libraries to provide a simple and familiar frontend user interface with intuitive tools for building knowledge graphs, searching for relevant papers, conversing with LLMs, and visualizing data. Nexarag is also fully containerized, with release artifacts produced by automated build pipelines readily available for local deployment through Docker. For flexibility, we integrate with Ollama and support any embedding model and LLM that is also supported by the user's hardware, making it simple to switch between models for different tasks and as new models are released. Users can also plug in their preferred LLM or coding agent of choice using the built-in MCP server. Additionally, Nexarag features a highly modular design, with distinct services for the REST API, the neo4j knowledge graph, the MCP server, and the frontend application, all bound together with a RabbitMQ messaging backbone. This allows components to scale horizontally, and to minimize the blast radius of contributions in a single service. Finally, Nexarag supports on-premises, air-gapped deployments, offering privacy and security that is not available in cloud-based applications.

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
