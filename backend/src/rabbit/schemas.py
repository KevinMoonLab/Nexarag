from pydantic import BaseModel
from typing import List

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