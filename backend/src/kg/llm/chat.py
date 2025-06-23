from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from rabbit.events import ChatMessage
from kg.db.queries import retrieve_similar_chunks, retrieve_similar_abstracts
from kg.llm.conversation import get_session_history
from kg.llm.adapter import OllamaAdapter, LangChainWrapper, NomicEmbeddingAdapter

import os
import logging

logger = logging.getLogger(__name__)
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

default_prefix = """
    You are a helpful research assistant that provides detailed answers about academic papers using retrieved context as well as your own knowledge.
    The context consists of both abstracts and chunks of text from the papers.
    Based on the following context, provide a concise response that directly addresses the question, drawing from the context while also including any existing knowledge you have of the topic.
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

def retrieve_context_wrapper(emb_adapter):
    return lambda inputs: retrieve_context(emb_adapter, inputs)

def retrieve_context(emb_adapter, inputs):
    question = inputs["question"]
    prepared_question = emb_adapter.prepare_query(question)
    question_embedding = emb_adapter.embeddings.embed_query(prepared_question)
    chunk_results = retrieve_similar_chunks(question_embedding, k=30)
    abstract_results = retrieve_similar_abstracts(question_embedding, k=30)
    context_text = "\n\n---\n\n".join([result['text'] for result in chunk_results])
    abstract_text = "\n\n---\n\n".join([result['text'] for result in abstract_results])
    
    return {
        "prefix": inputs.get("prefix", default_prefix),
        "abstracts": abstract_text,
        "chunks": context_text,
        "question": question,
        "chat_history": inputs.get("chat_history", [])
    }

def create_rag_chain_with_memory(llm_adapter, emb_adapter):
    chain = retrieve_context_wrapper(emb_adapter) | prompt_template_with_history | llm_adapter
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history",
    )
    
    return chain_with_history

def ask_llm_kg_with_conversation(message: ChatMessage, session_id: str = "default"):
    llm_adapter = LangChainWrapper(adapter=OllamaAdapter(
        model_id=message.model,
        num_ctx=message.numCtx,
        num_predict=message.numPredict,
        temperature=message.temperature,
    ))

    nomic_adapter = NomicEmbeddingAdapter(model_id='nomic-embed-text:v1.5')
    conversational_chain = create_rag_chain_with_memory(llm_adapter, nomic_adapter)
    response = conversational_chain.stream(
        {"question": message.message, "prefix": message.prefix or default_prefix},
        config={"configurable": {"session_id": session_id}}
    )
    
    for chunk in response:
        yield chunk.content if hasattr(chunk, 'content') else str(chunk)


async def ask_kg(message: ChatMessage, cb, complete, session_id: str = "default"):
    logger.info(f"Handling chat request: {message}")
    try:
        for chunk in ask_llm_kg_with_conversation(message, session_id):
            await cb(chunk)
        await complete()
    except Exception as e:
        logger.error(f"Error in ask_kg: {e}")
        await complete()