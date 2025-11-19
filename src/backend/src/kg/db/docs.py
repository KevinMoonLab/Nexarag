from rabbit.events import DocumentsCreated
from kg.db.models import Document, Paper 
from pydantic import BaseModel
from typing import List

class SaveDocumentResult(BaseModel):
    success: bool
    message: str
    

async def add_document_refs(docs: DocumentsCreated) -> List[SaveDocumentResult]:
    results = []
    for doc in docs.documents:
        paper = await Paper.nodes.get_or_none(paper_id=doc.node_id)
        await Document(document_id=doc.id, path=doc.path, og_path=doc.og_path, name=doc.name).save()
        if not paper:
            results.append(SaveDocumentResult(success=True, message=f"Document {doc.id} saved without associated paper"))
            continue
        new_doc = await Document.nodes.get(document_id=doc.id)
        await paper.documents.connect(new_doc)
        results.append(SaveDocumentResult(success=True, message=f"Document {doc.id} saved and linked to paper {paper.paper_id}"))
    return results