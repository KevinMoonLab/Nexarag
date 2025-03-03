from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

class AddPapersById(BaseModel):
    paperIds: List[str]

class AddPaperCitations(BaseModel):
    paperIds: List[str]

class AddPaperReferences(BaseModel):
    paperIds: List[str]

class ClearGraph(BaseModel):
    reason: str

class PaperRef(BaseModel):
    paperId: str
    paperDbId: str

class GraphUpdated(BaseModel):
    nodeIds: List[str]

class ChatMessage(BaseModel):
    message: str 
    chatId: str
    messageId: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))

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
    