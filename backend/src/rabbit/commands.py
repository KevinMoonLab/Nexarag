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
    num_docs: int
    n_components: float  