from langchain_ollama.llms import OllamaLLM
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk
from typing import Any, AsyncIterator, Iterator, List, Optional
from langchain_neo4j import Neo4jVector
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory, SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from db.util import load_default_kg
from rabbit.events import ChatMessage

import os
import logging

logger = logging.getLogger(__name__)
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

default_prefix = """
    You are a helpful research assistant that provides detailed answers about academic papers using retrieved context as well as your own knowledge.
    The context consists of both abstracts and chunks of text from the papers.
    Based on the following context, provide as much detail as possible in response to the question based primarily on the context, but also including any existing knowledge you have of the topic.
    If the context lacks the requested information, provide a reasonable response while acknowledging your limited knowledge of the topic.
    Always explicitly cite the title in the context you used to answer the question, if it is available.
    
    Use the conversation history to provide contextually relevant responses and refer back to previous exchanges when appropriate.
"""

# Updated prompt template with conversation history using MessagesPlaceholder
prompt_template_with_history = ChatPromptTemplate.from_messages([
    ("system", """{prefix}

Abstracts:
{abstracts}

Chunks:
{chunks}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

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

    def get_num_tokens(self, text: str) -> int:
        return len(text.split())

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
        return query

class NomicEmbeddingAdapter(BaseEmbeddings):
    def __init__(self, model_id):
        self.embeddings = OllamaEmbeddings(model=model_id, base_url=ollama_base_url)
        self.query_prefix = ""
    def embed_query(self, text: str):
        return self.embeddings.embed_query(text)
    def prepare_query(self, query: str):
        return self.query_prefix + query

# SQLite storage for conversation histories
from langchain_community.chat_message_histories import SQLChatMessageHistory

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Get or create a SQLite-backed chat message history for a session"""
    return SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:///chat_conversations.db"
    )

def create_rag_chain_with_memory(llm_adapter, emb_adapter, kg):
    """Create a RAG chain with conversation memory"""
    
    def retrieve_context(inputs):
        """Retrieve relevant documents and abstracts"""
        question = inputs["question"]
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

        retrieved_docs = doc_vector.similarity_search_with_score(prepared_question, k=10)
        retrieved_abstracts = abstract_vector.similarity_search_with_score(prepared_question, k=10)
        
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in retrieved_docs])
        abstract_text = "\n\n---\n\n".join([doc.page_content for doc, _ in retrieved_abstracts])
        
        return {
            "prefix": inputs.get("prefix", default_prefix),
            "abstracts": abstract_text,
            "chunks": context_text,
            "question": question,
            "chat_history": inputs.get("chat_history", [])
        }
    
    # Create the chain: retrieve context -> format prompt -> LLM
    chain = retrieve_context | prompt_template_with_history | llm_adapter
    
    # Wrap with message history
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history",
    )
    
    return chain_with_history

def ask_llm_kg_with_conversation(message: ChatMessage, session_id: str = "default"):
    """Ask LLM with conversation memory using built-in LangChain functionality"""
    llm_adapter = LangChainWrapper(adapter=OllamaAdapter(
        model_id=message.model,
        num_ctx=message.numCtx,
        num_predict=message.numPredict,
        temperature=message.temperature,
    ))

    kg = load_default_kg()
    nomic_adapter = NomicEmbeddingAdapter(model_id='nomic-embed-text:v1.5')
    
    # Create the chain with conversation memory
    conversational_chain = create_rag_chain_with_memory(llm_adapter, nomic_adapter, kg)
    
    # Invoke with session configuration
    response = conversational_chain.stream(
        {"question": message.message, "prefix": message.prefix or default_prefix},
        config={"configurable": {"session_id": session_id}}
    )
    
    for chunk in response:
        yield chunk.content if hasattr(chunk, 'content') else str(chunk)

def clear_conversation_history(session_id: str = "default"):
    """Clear conversation history for a session"""
    # For SQLite, we create a new instance and clear it
    history = SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:///chat_conversations.db"
    )
    history.clear()

def get_conversation_history(session_id: str):
    """Retrieve conversation history for a session"""
    history = SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:///chat_conversations.db"
    )
    return history.messages

def list_all_sessions():
    """List all conversation sessions in the database"""
    import sqlite3
    conn = sqlite3.connect("chat_conversations.db")
    cursor = conn.cursor()
    
    # Get all unique session IDs
    cursor.execute("SELECT DISTINCT session_id FROM message_store")
    sessions = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return sessions

def get_session_summary(session_id: str):
    """Get a summary of a conversation session"""
    history = get_conversation_history(session_id)
    if not history:
        return {"session_id": session_id, "message_count": 0, "last_message": None}
    
    return {
        "session_id": session_id,
        "message_count": len(history),
        "first_message": history[0].content if history else None,
        "last_message": history[-1].content if history else None,
        "last_timestamp": history[-1].additional_kwargs.get('timestamp') if history else None
    }

def restore_conversation_from_backup(backup_file: str, target_db: str = "chat_conversations.db"):
    """Restore conversations from a backup SQLite file"""
    import shutil
    shutil.copy2(backup_file, target_db)
    print(f"Conversations restored from {backup_file}")

def backup_conversations(backup_file: str = "chat_backup.db"):
    """Create a backup of all conversations"""
    import shutil
    shutil.copy2("chat_conversations.db", backup_file)
    print(f"Conversations backed up to {backup_file}")

async def ask_kg(message: ChatMessage, cb, complete, session_id: str = "default"):
    """Updated async function to use conversation memory"""
    logger.info(f"Handling chat request: {message}")
    try:
        for chunk in ask_llm_kg_with_conversation(message, session_id):
            await cb(chunk)
        await complete()
    except Exception as e:
        logger.error(f"Error in ask_kg: {e}")
        await complete()

# Keep the original function for backward compatibility
def ask_llm_kg(message: ChatMessage):
    """Original function without conversation history"""
    llm_adapter = OllamaAdapter(
        model_id=message.model,
        num_ctx=message.numCtx,
        num_predict=message.numPredict,
        temperature=message.temperature,
    )

    kg = load_default_kg()
    nomic_adapter = NomicEmbeddingAdapter(model_id='nomic-embed-text:v1.5')

    # Original prompt template without conversation history
    original_prompt_template = """
        {prefix}

        Abstracts:
        {abstracts}

        Chunks:
        {chunks}

        Question:
        {question}

        Answer:
    """

    prepared_question = nomic_adapter.prepare_query(message.message)

    doc_query = """
        MATCH (c:Chunk)
        WITH DISTINCT c, vector.similarity.cosine(c.textEmbedding, $embedding) AS score
        ORDER BY score DESC LIMIT $k
        RETURN c.text AS text, score, {source: c.source, chunkId: c.chunkId} AS metadata
    """

    doc_vector = Neo4jVector.from_existing_index(
        nomic_adapter.embeddings,
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
        nomic_adapter.embeddings,
        graph=kg,
        index_name='abstract_embeddings',
        embedding_node_property='abstractEmbedding',
        text_node_property='text',
        retrieval_query=abstract_query,
    )

    retrieved_docs = doc_vector.similarity_search_with_score(prepared_question, k=10)
    retrieved_abstracts = abstract_vector.similarity_search_with_score(prepared_question, k=10)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in retrieved_docs])
    abstract_text = "\n\n---\n\n".join([doc.page_content for doc, _ in retrieved_abstracts])
    prompt = original_prompt_template.format(
        prefix=message.prefix or default_prefix, 
        abstracts=abstract_text, 
        chunks=context_text, 
        question=message.message
    )

    for chunk in llm_adapter.stream(prompt):
        yield chunk