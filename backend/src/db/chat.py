from db.models import Chat, ChatResponse, ChatMessage
from rabbit.schemas import ChatMessage as RabbitChatMessage, ChatResponse as RabbitChatResponse
import logging

logger = logging.getLogger(__name__)

async def create_chat_message(message: RabbitChatMessage):
    message = await ChatMessage(message_id=message.messageId, message=message.message).save()
    return message    


async def update_chat_response(response: RabbitChatResponse):
    chat_message = await ChatMessage.nodes.get_or_none(message_id=response.userMessageId)
    existing_response = await ChatResponse.nodes.get_or_none(response_id=response.responseId)

    if existing_response:
        existing_response.message += f" {response.message}"
        await existing_response.save()
        chat_response = existing_response
    else:
        chat_response = await ChatResponse(message=response.message, response_id=response.responseId).save()

    if chat_message:
        await chat_response.response_to.connect(chat_message)
    return chat_response
