import os

config = {
    "llm": {
        "provider": "ollama",    # options: "ollama", "openai", "huggingface", etc.
        'model_id': 'llama3.3',
        "num_ctx": 32768,
        "num_predict": 4096,
        "temperature": 0.5,
        "api_key": "YOUR_API_KEY_IF_NEEDED"  # only used for some providers
    },
    'database': {
        'uri': os.getenv("NEO4J_URI"),
        'username': os.getenv("NEO4J_USERNAME"),
        'password': os.getenv("NEO4J_PASSWORD"),
        'database': os.getenv("NEO4J_DATABASE")
    },
    "embedding": {
        "provider": "nomic",  # e.g., "nomic", "openai"
        "model_id": "nomic-embed-text",
        'size': 768,
        'similarity': 'cosine',
        # For some embedder providers (like nomic) you may need to prepend a prefix:
        "query_prefix": "search_query: "
    },
    'rag': {
        'index_name': 'paper_chunks',
        'embedding_node_property': 'textEmbedding',
        'text_node_property': 'text'
    }
}