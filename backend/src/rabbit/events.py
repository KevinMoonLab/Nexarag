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

class EmbeddingPlotCreated(BaseModel):
    embeddings: List[List[float]]
    labels: List[str]
    paper_ids: List[str]

    @classmethod
    def from_numpy(cls, embeddings_np, labels, paper_id_chunks):
        paper_ids = [pid for chunk in paper_id_chunks for pid in chunk.tolist()]
        return cls(
            embeddings=embeddings_np.tolist(),
            labels=labels,
            paper_ids=paper_ids
        )

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
    path: str
    og_path: str
    node_id: Optional[str] = None
    name: Optional[str] = Field(default="Document", description="Document name")

class DocumentGraphUpdated(BaseModel):
    doc: DocumentCreated

class DocumentsCreated(BaseModel):
    documents: List[DocumentCreated]

class DocumentUploaded(BaseModel):
    id: str