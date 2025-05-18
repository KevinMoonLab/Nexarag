from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

class PaperRef(BaseModel):
    paper_id: str
    paperDbId: str

class GraphUpdated(BaseModel):
    nodeIds: List[str]

class ChatMessage(BaseModel):
    message: str 
    prefix: str
    chatId: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    messageId: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    numCtx: Optional[int] = Field(default_factory=lambda: 32768)
    numPredict: Optional[int] = Field(default_factory=lambda: 4096)
    temperature: Optional[float] = Field(default_factory=lambda: 0.5)
    model: Optional[str] = Field(default_factory=lambda: "gemma3:1b")

class ChatResponse(BaseModel):
    message: str
    chatId: str
    userMessageId: str
    responseId: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ResponseCompleted(BaseModel):
    chatId: str
    responseId: str

class DocumentCreated(BaseModel):
    id: str
    node_id: str
    path: str

class DocumentGraphUpdated(BaseModel):
    doc: DocumentCreated

class DocumentsCreated(BaseModel):
    documents: List[DocumentCreated]

class DocumentUploaded(BaseModel):
    id: str

class EmbeddingPlotCreated(BaseModel):
    x: List[float]
    y: List[float]
    color: List[str]
    title: str
    xlabel: str
    ylabel: str