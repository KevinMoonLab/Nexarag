from pydantic import BaseModel, Field
from typing import List, Optional

class AddPapersById(BaseModel):
    paper_ids: List[str]

class PaperTitleWithYear(BaseModel):
    title: str
    year: Optional[int] = None

class AddPapersByTitle(BaseModel):
    papers: List[PaperTitleWithYear]

class AddPaperCitations(BaseModel):
    paper_ids: List[str]

class AddPaperReferences(BaseModel):
    paper_ids: List[str]

class ClearGraph(BaseModel):
    reason: str

class CreateEmbeddingPlot(BaseModel):
    queries: List[str]
    color_var: str
    model_id: Optional[str] = Field(default="nomic-embed-text:v1.5")
    num_docs: Optional[int] = Field(default=10)
    num_components: Optional[float] = Field(default=0.95)
    labels: Optional[List[str]] = None