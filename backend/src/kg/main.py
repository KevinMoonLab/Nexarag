import asyncio
import logging
from rabbit import get_publisher, publish_message, subscribe_to_queue, ChannelType
from rabbit.events import ChatMessage, ChatResponse, ResponseCompleted, DocumentGraphUpdated
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Callable, Awaitable
from kg.docs import create_chunk_nodes
from db.util import load_default_kg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import sys
sys.path.append("/app/src") 
from rag import rag_utils as rag
from rag.configs.huggingface_config import config
from langchain_neo4j import Neo4jVector
# from rag.configs.ollama_config import config

from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate

def load_model():
    logger.info("Starting model load...")
    model = rag.get_llm_with_memory(config)
    logger.info("Model loaded!")
    return model

def load_kg_retriever():
    logger.info("Loading KG")
    kg = load_default_kg()
    logger.info("loading embedder")
    emb_adapter = rag.get_embeddings(config)

    custom_query = """
    MATCH (c:Chunk)
    WITH DISTINCT c, vector.similarity.cosine(c.textEmbedding, $embedding) AS score
    ORDER BY score DESC LIMIT $k
    RETURN c.text AS text, score, {source: c.source, chunkId: c.chunkId} AS metadata
    """

    logger.info("Creating chunk nodes Neo4jVector")
    chunk_vector = Neo4jVector.from_existing_index(
        emb_adapter.embeddings,
        graph=kg, 
        index_name=config["rag"]["index_name"],
        embedding_node_property=config["rag"]["embedding_node_property"],
        text_node_property=config["rag"]["text_node_property"],
        retrieval_query=custom_query,
    )

    logger.info("Convert to retriever")
    neo4j_retriever = chunk_vector.as_retriever()
    return neo4j_retriever

def startup_chatbot():
    global llm_adapter, memory, conversation
    llm_adapter = load_model()
    kg_retriever = load_kg_retriever()

    simple_rag_chain = (
        {"context": llm_adapter, "question": RunnablePassthrough()}
        | PromptTemplate.from_template("Answer: {context}\nQuestion: {question}")
        | llm_adapter
    )

    # memory = ConversationSummaryBufferMemory(
    #     llm=llm_adapter, 
    #     memory_key='history', 
    #     max_token_limit=4096
    # )
    # conversation = ConversationChain(
    #     llm=llm_adapter, 
    #     memory=memory,
    #     verbose=True
    # )
    logger.info("Conversation initialized")

def startup_agent():
    pass

async def handle_request(message: ChatMessage, cb: Callable, complete: Callable):
    try:
        response = conversation.predict(input=f"User message: {message.message}\nRespond helpfully:")
        await cb(response.strip())
        await complete()
        
    except Exception as e:
        logger.error(f"LLM Error: {str(e)}")
        await cb("Sorry, I'm having trouble processing your request")
        await complete()

async def handle_documents_created(update: DocumentGraphUpdated):
    doc = update.doc
    logger.info(f"Received documents created: {doc}")
    # Load file content
    doc_path = f"/docs/{doc.path}"
    with open(doc_path, "r") as f:
        content = f.read()
    
    kg = load_default_kg()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000, # FIXME
        chunk_overlap  = 200,
        length_function = len,
        is_separator_regex = False,
    )
    
    create_chunk_nodes(kg, content, doc.node_id, text_splitter)
    logger.info(f"Created chunk nodes for document: {doc.node_id}: {doc.path}")

def callbacks(message: ChatMessage):
    first_response = ChatResponse(message="", chatId=message.chatId, userMessageId=message.messageId)
    make_response = lambda msg: ChatResponse(message=msg, chatId=message.chatId, userMessageId=message.messageId, responseId=first_response.responseId)
    async def async_chat_callback(msg: str):
        await publish_message(ChannelType.CHAT_RESPONSE, make_response(msg))
    async def async_completion_callback():
        await publish_message(ChannelType.RESPONSE_COMPLETED, ResponseCompleted(chatId = message.chatId, responseId = first_response.responseId))
    return (async_chat_callback, async_completion_callback)

async def handle_chat_message(message: ChatMessage):
    logger.info(f"Received chat message: {message}")
    response_callback, completion_callback = callbacks(message)
    await handle_request(message, response_callback, completion_callback)

async def main():
    logger.info("Subscribing to RabbitMQ events...")
    if True:
        startup_chatbot()
    else:
        startup_agent()
    await asyncio.gather(
        subscribe_to_queue(ChannelType.CHAT_MESSAGE_CREATED, handle_chat_message, ChatMessage),
        subscribe_to_queue(ChannelType.DOCUMENT_GRAPH_UPDATED, handle_documents_created, DocumentGraphUpdated)
    )

if __name__ == "__main__":
    logger.info("Starting Knowledge Graph worker...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())