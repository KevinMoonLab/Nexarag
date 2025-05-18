from langchain_ollama.llms import OllamaLLM
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk
from typing import Any, AsyncIterator, Iterator, List, Optional
from langchain_neo4j import Neo4jVector
from db.util import load_default_kg
from rabbit.events import ChatMessage

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

prompt_template = """
    Based on the following context, provide as much detail as possible in response to the question based primarily on the context, but also including any existing knowledge you have of the topic.
    If the context lacks the requested information, provide a reasonable response while acknowledging your limited knowledge of the topic.
    Always explicitly cite the title in the context you used to answer the question, if it is available.

    Context:
    {context}

    Question:
    {question}

    Answer:
"""

class BaseLLM:
    def stream(self, prompt: str):
        raise NotImplementedError("stream() must be implemented by subclasses.")

class LangChainWrapper(LLM):
    adapter: BaseLLM
    streaming: bool = True
    
    @property
    def _llm_type(self) -> str:
        return "custom_adapter"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """Non-streaming version"""
        return "".join(self.adapter.stream(prompt))

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """Streaming implementation"""
        for token in self.adapter.stream(prompt):
            yield GenerationChunk(text=token)

    # Required abstract method implementations
    def get_num_tokens(self, text: str) -> int:
        return len(text.split())

    # Optional async implementations
    async def _acall(self, prompt: str, **kwargs: Any) -> str:
        return self._call(prompt, **kwargs)

    async def _astream(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> AsyncIterator[GenerationChunk]:
        for token in self.adapter.stream(prompt):
            yield GenerationChunk(text=token)


class OllamaAdapter(BaseLLM):
    def __init__(self, model_id:str="gemma3:1b", num_ctx:int=32768, num_predict:int=4096, temperature:float=0.5):
        self.llm = OllamaLLM(
            model=model_id,
            num_ctx=num_ctx,
            num_predict=num_predict,
            temperature=temperature,
            base_url=ollama_base_url,
        )
    def stream(self, prompt: str):
        return self.llm.stream(prompt)

    
def get_llm(config):
    provider = config["llm"]["provider"].lower()
    if provider == "ollama":
        return OllamaAdapter(config["llm"])
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
def get_llm_with_memory(config):
    base_llm = get_llm(config)
    return LangChainWrapper(adapter=base_llm)

class BaseEmbeddings:
    def embed_query(self, text: str):
        raise NotImplementedError("embed_query() must be implemented.")
    def prepare_query(self, query: str):
        # Default is no extra processing
        return query

class NomicEmbeddingAdapter(BaseEmbeddings):
    def __init__(self, model_id):
        self.embeddings = OllamaEmbeddings(model=model_id, base_url=ollama_base_url)
        self.query_prefix = ""
    def embed_query(self, text: str):
        return self.embeddings.embed_query(text)
    def prepare_query(self, query: str):
        return self.query_prefix + query
    

def query_kg(question, llm_adapter, emb_adapter, kg, prompt_template, k=30):
    prepared_question = emb_adapter.prepare_query(question)

    doc_query = """
        MATCH (c:Chunk)
        WITH DISTINCT c, vector.similarity.cosine(c.textEmbedding, $embedding) AS score
        ORDER BY score DESC LIMIT $k
        RETURN c.text AS text, score, {source: c.source, chunkId: c.chunkId} AS metadata
    """

    doc_vector = Neo4jVector.from_existing_index(
        emb_adapter.embeddings,
        graph=kg,
        index_name='paper_chunks',
        embedding_node_property='textEmbedding',
        text_node_property='text',
        retrieval_query=doc_query,
    )

    abstract_query = """
        MATCH (c:Paper)
        WHERE c.abstract IS NOT NULL AND c.title IS NOT NULL
        WITH DISTINCT c, vector.similarity.cosine(c.abstractEmbedding, $embedding) AS score
        ORDER BY score DESC LIMIT $k
        RETURN 'Title: ' + c.title + '\n\n' + 'Abstract: ' + c.abstract AS text, score, {source: c.source, chunkId: c.chunkId} AS metadata
    """

    abstract_vector = Neo4jVector.from_existing_index(
        emb_adapter.embeddings,
        graph=kg,
        index_name='abstract_embeddings',
        embedding_node_property='abstractEmbedding',
        text_node_property='text',
        retrieval_query=abstract_query,
    )

    retrieved_docs = doc_vector.similarity_search_with_score(prepared_question, k=k)
    retrieved_abstracts = abstract_vector.similarity_search_with_score(prepared_question, k=k)
    retrieved_docs.extend(retrieved_abstracts)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in retrieved_docs])
    prompt = prompt_template.format(context=context_text, question=question)

    for chunk in llm_adapter.stream(prompt):
        yield chunk

def ask_llm_kg(message:ChatMessage):
    llm_adapter = OllamaAdapter(
        model_id=message.model,
        num_ctx=message.numCtx,
        num_predict=message.numPredict,
        temperature=message.temperature,
    )

    kg = load_default_kg()
    nomic_adapter = NomicEmbeddingAdapter(model_id='nomic-embed-text:v1.5')

    for chunk in query_kg(
        message.message, 
        llm_adapter, 
        nomic_adapter, 
        kg, 
        prompt_template, 
        k=10
    ):
        yield chunk
