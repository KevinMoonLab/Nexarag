import asyncio
import logging
from rabbit import publish_message, subscribe_to_queue, ChannelType
from rabbit.schemas import ChatMessage, ChatResponse, ResponseCompleted, DocumentGraphUpdated
from typing import Callable
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import sys
sys.path.append("/app/src") 
from rag import rag_utils as rag
from rag.configs.huggingface_config import config
# from rag.configs.ollama_config import config

from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain

def load_model():
    logger.info("Starting model load...")
    model = rag.get_llm_with_memory(config)
    logger.info("Model loaded!")
    return model

def startup_chatbot():
    global llm_adapter, memory, conversation
    llm_adapter = load_model()
    memory = ConversationSummaryBufferMemory(
        llm=llm_adapter, 
        memory_key='history', 
        max_token_limit=4096
    )
    conversation = ConversationChain(
        llm=llm_adapter, 
        memory=memory,
        verbose=True
    )
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
    # Your code here
    # Example: Load file content
    doc_path = f"/docs/{doc.path}"
    with open(doc_path, "r") as f:
        content = f.read()
        logger.info(f"Received document for {doc.node_id}")
        logger.info(f"Loaded document {doc.id} with content: {content}")

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