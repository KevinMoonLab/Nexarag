from rabbit.events import DocumentsCreated, DocumentCreated
from db.models import Document, Paper 
from pydantic import BaseModel
from typing import List

class SaveDocumentResult(BaseModel):
    success: bool
    message: str
    

async def add_document_refs(docs: DocumentsCreated) -> List[SaveDocumentResult]:
    results = []
    for doc in docs.documents:
        paper = await Paper.nodes.get_or_none(paper_id=doc.node_id)
        if not paper:
            results.append(SaveDocumentResult(success=False, message=f"Paper with id {doc.node_id} not found"))
            continue
        await Document(node_id=doc.node_id, document_id=doc.id, path=doc.path).save()
        new_doc = await Document.nodes.get(document_id=doc.id)
        await paper.documents.connect(new_doc)
        results.append(SaveDocumentResult(success=True, message=f"Document {doc.id} saved for paper {doc.node_id}"))
    return results