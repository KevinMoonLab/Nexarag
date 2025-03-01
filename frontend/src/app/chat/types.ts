export type ChatMessage = {
    message: string;
    chatId: string;
    messageId: string;
}

export type ChatResponse = {
    responseId: string;
    userMessageId: string;
    message: string;
    chatId: string;
}

export type ViewChatMessage = {
    text: string;
    isUser: boolean;
    messageId: string;
}