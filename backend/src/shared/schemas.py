from pydantic import BaseModel
from typing import List

class AddPapersByTitle(BaseModel):
    titles: List[str]

class ClearGraph(BaseModel):
    reason: str

class PaperRef(BaseModel):
    paperId: str
    paperDbId: str

class PapersAdded(BaseModel):
    paperRefs: List[PaperRef]