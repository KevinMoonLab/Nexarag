from pydantic import BaseModel, Field
from typing import List
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
    messageId: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ChatResponse(BaseModel):
    message: str
    chatId: str
    messageId: str