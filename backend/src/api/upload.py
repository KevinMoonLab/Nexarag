import pymupdf4llm
from fastapi import UploadFile, HTTPException
from .util import create_id
import tempfile
import os
from typing import List
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
import re

ALLOWED_FILE_TYPES = {"application/pdf", "text/markdown", "text/plain"}
class UploadFileResponse(BaseModel):
    id: str
    path: str
    og_path: str
    name: str
    message: str
    size: int

async def upload_many(docs: List[UploadFile], ollama_base_url: str) -> List[UploadFileResponse]:
    upload_info = []
    for doc in docs:
        result = await upload(doc, ollama_base_url)
        upload_info.append(result)
    return upload_info

def extract_title_ollama(content: str, filename: str, ollama_base_url:str, model: str = "gemma3:12b", max_chars: int = 2000) -> str:
    try:
        content_sample = content.strip()[:max_chars]
        
        if len(content_sample.strip()) < 50:
            return extract_title_heuristic(content, filename)
        
        prompt = f"""You are a document analysis expert. Extract a concise, descriptive title from the following document content. 

Requirements:
- Return ONLY the title, nothing else
- Keep it under 80 characters
- Make it descriptive and specific
- Do not include quotes or extra formatting
- If the document already has a clear title, use that
- If no clear title exists, create one based on the main topic

Document content:
{content_sample}

Title:"""

        # Use your existing Ollama setup
        llm = OllamaLLM(model=model, base_url=ollama_base_url)
        response = llm.invoke(prompt)
        
        # Clean up the response
        title = response.strip()
        
        # Remove common prefixes that models sometimes add
        title = re.sub(r'^(Title:\s*|The title is:\s*|"\s*|Title\s*[-:]\s*)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'["\n\r]+', '', title)  # Remove quotes and newlines
        title = title.strip()
        
        # Validate the extracted title
        if title and 5 <= len(title) <= 100 and not title.lower().startswith(('i ', 'the document', 'this document')):
            return title
        else:
            # Fallback to heuristic if AI response is poor
            return extract_title_heuristic(content, filename)
            
    except Exception as e:
        print(f"Error extracting title with Ollama: {e}")
        return extract_title_heuristic(content, filename)

def extract_title_heuristic(content: str, filename: str) -> str:
    lines = content.strip().split('\n')
    
    # Remove empty lines from the beginning
    while lines and not lines[0].strip():
        lines.pop(0)
    
    if not lines:
        return os.path.splitext(filename)[0]
    
    # Look for markdown headers first
    for line in lines[:10]:
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
        elif line.startswith('## '):
            return line[3:].strip()
    
    # Look for lines that might be titles
    for line in lines[:5]:
        line = line.strip()
        if line and len(line) < 100:
            if not any(pattern in line.lower() for pattern in ['date:', 'author:', 'email:', 'http']):
                if len(line.split()) >= 2:
                    return line
    
    return os.path.splitext(filename)[0]

async def upload(doc: UploadFile, ollama_base_url:str, extraction_method: str = "ollama", ollama_model: str = "gemma3:12b") -> UploadFileResponse:
    if doc.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {doc.content_type} not allowed. Allowed types are: {ALLOWED_FILE_TYPES}"
        )
    
    content = await doc.read()
    file_id = create_id()
    extracted_title = None

    if doc.content_type == "application/pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(content)
            temp_pdf_path = temp_pdf.name
        
        try:
            markdown_content = pymupdf4llm.to_markdown(temp_pdf_path)
            
            # Extract title based on method
            if extraction_method == "ollama":
                extracted_title = extract_title_ollama(markdown_content, doc.filename, ollama_base_url, ollama_model)
            else:
                extracted_title = extract_title_heuristic(markdown_content, doc.filename)
            
        except Exception as e:
            os.unlink(temp_pdf_path)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to convert PDF to markdown: {str(e)}"
            )
        finally:
            os.unlink(temp_pdf_path)
        
        og_name, _ = os.path.splitext(doc.filename)
        markdown_filename = f"{og_name}-{file_id}.md"
        
        with open(f"/docs/{markdown_filename}", "w", encoding="utf-8") as md_file:
            md_file.write(markdown_content)

        with open(f"/docs/{doc.filename}", "wb") as pdf_file:
            pdf_file.write(content)

        return UploadFileResponse(
            id=file_id,
            path=markdown_filename,
            og_path=doc.filename,
            name=extracted_title,
            message="PDF uploaded and converted to markdown successfully",
            size=len(markdown_content)
        )

    else:  # Text/markdown files
        text_content = content.decode('utf-8')
        
        # Extract title based on method
        if extraction_method == "ollama":
            extracted_title = extract_title_ollama(text_content, doc.filename, ollama_model)
        else:
            extracted_title = extract_title_heuristic(text_content, doc.filename)
        
        file_extension = "md" if doc.content_type == "text/markdown" else "txt"
        filename = f"/docs/{file_id}.{file_extension}"
        
        with open(filename, "wb") as file:
            file.write(content)
        
        return UploadFileResponse(
            id=file_id,
            path=filename,
            og_path=doc.filename,
            name=extracted_title or os.path.splitext(doc.filename)[0],
            message="File uploaded successfully",
            size=len(content)
        )
        
        