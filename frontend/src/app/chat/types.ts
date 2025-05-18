export type ChatMessage = {
    message: string;
    prefix:string;
    chatId: string;
    messageId: string;
    model: string;
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

export type ModelDetails = {
    model: string;
    size: number;
}