import pymupdf4llm
from fastapi import UploadFile, HTTPException
from .util import create_id
import tempfile
import os
from typing import List

ALLOWED_FILE_TYPES = {"application/pdf", "text/markdown", "text/plain"}

async def upload_many(docs: List[UploadFile]):
    upload_info = []
    for doc in docs:
        result = await upload(doc)
        upload_info.append(result)
    return upload_info

async def upload(doc: UploadFile):
    if doc.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {doc.content_type} not allowed. Allowed types are: {ALLOWED_FILE_TYPES}"
        )
    
    # Read file content
    content = await doc.read()

    # Extract PDFs to markdown
    if doc.content_type == "application/pdf":
        # Save the PDF content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(content)
            temp_pdf_path = temp_pdf.name
        
        try:
            # Convert PDF to markdown using pymupdf4llm
            markdown_content = pymupdf4llm.to_markdown(temp_pdf_path)
        except Exception as e:
            # Clean up the temporary file
            os.unlink(temp_pdf_path)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to convert PDF to markdown: {str(e)}"
            )
        finally:
            # Ensure the temporary file is deleted even if an error occurs
            os.unlink(temp_pdf_path)
        
        # Save the markdown content to a file
        file_id = create_id()
        og_name, _ = os.path.splitext(doc.filename)
        markdown_filename = f"{og_name}-{file_id}.md"
        with open(f"/docs/{markdown_filename}", "w", encoding="utf-8") as md_file:
            md_file.write(markdown_content)
        
        return {
            "id": file_id,
            "path": markdown_filename,
            "message": "PDF uploaded and converted to markdown successfully",
            "size": len(markdown_content)
        }
    # Handle text/markdown files
    else:
        file_id = create_id()
        file_extension = "md" if doc.content_type == "text/markdown" else "txt"
        filename = f"/docs/{file_id}.{file_extension}"
        with open(filename, "wb") as file:
            file.write(content)
        return {
            "id": file_id,
            "path": filename,
            "message": "File uploaded successfully",
            "size": len(content)
        }
        
        