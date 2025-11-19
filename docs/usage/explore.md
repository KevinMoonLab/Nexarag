# Exploring Knowledge Graphs
There are three ways to explore Nexarag knowledge graphs: 

* Built-in LLM chat feature
* Interactive visualization tools
* Filtering

## LLM Chat Feature
The Nexarag chat feature, available in the right sidebar, uses context from paper abstracts, documents, authors, and other data and relationships in the knowledge graph to respond to user queries. 

1. Click the chat menu item in the right sidebar. 
2. **[Optional]** Click the cog on the right sidebar and choose a different Ollama model or specify a different system prompt.
3. Ask a question about the knowledge graph!

## Interactive Visualizations
Nexarag allows users to generate two-dimensional visualizations of the abstracts and documents in their knowledge graph.

1. Click the chart icon on the left sidebar.
2. Select a color variable. (Currently only 'Labels' is supported).
3. Add a label for your prompt.
4. Add a prompt, e.g. "Papers about constrained optimization".
5. Repeat steps 3 and 4 for as many labels as is desired.
6. Click 'Submit'.
7. Your plot will be generated automatically. 

## Filtering
Users can filter the graph and change certain display settings. Click the sliders icon on the left sidebar.

| Filter         | Description                                                                    |
| -------------- | ------------------------------------------------------------------------------ |
| Search         | Enter a search term to filter by title.                                        |
| Visible Nodes  | Filter visible nodes: Paper, Author, Document, Journal, and Publication Venue. |
| Node Weighting | Nodes will be weighted by the number of edges they have.                       |
| Node Repulsion | Used by the Cytoscape COSE layout.                                             |