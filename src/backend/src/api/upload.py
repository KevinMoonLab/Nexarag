import pymupdf4llm
from fastapi import UploadFile, HTTPException
from .util import create_id
import tempfile
import os
from typing import List
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
import re
import logging
from urllib.parse import unquote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_FILE_TYPES = {"application/pdf", "text/markdown", "text/plain"}
class UploadFileResponse(BaseModel):
    id: str
    path: str
    og_path: str
    name: str
    message: str
    size: int

def clean_filename(filename: str) -> str:
    if not filename:
        return filename
    
    cleaned = unquote(filename)
    return cleaned

def get_file_type_from_extension(filename: str) -> str:
    if not filename:
        return "unknown"
    
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == ".pdf":
        return "application/pdf"
    elif ext == ".md":
        return "text/markdown"
    elif ext == ".txt":
        return "text/plain"
    else:
        return "unknown"

def is_allowed_file(doc: UploadFile) -> bool:
    if doc.content_type in {"application/pdf", "text/markdown", "text/plain"}:
        return True
    
    if doc.content_type == "application/octet-stream":
        file_type = get_file_type_from_extension(doc.filename)
        return file_type in {"application/pdf", "text/markdown", "text/plain"}
    
    return False

def get_effective_content_type(doc: UploadFile) -> str:
    if doc.content_type == "application/octet-stream":
        return get_file_type_from_extension(doc.filename)
    return doc.content_type

async def upload_many(docs: List[UploadFile], ollama_base_url: str) -> List[UploadFileResponse]:
    upload_info = []
    for doc in docs:
        try:
            result = await upload(doc, ollama_base_url)
            upload_info.append(result)
        except HTTPException as e:
            logger.error(f"{e.status_code}: {e.detail}")
            logger.error(f"Failed to upload {doc.filename}: {e.detail}")
            # Don't re-raise, continue with other files
        except Exception as e:
            logger.error(f"Unexpected error uploading {doc.filename}: {str(e)}")
    return upload_info

def extract_title_ollama(content: str, filename: str, ollama_base_url: str, model: str = "gemma3:12b", max_chars: int = 2000) -> str:
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

        llm = OllamaLLM(model=model, base_url=ollama_base_url)
        response = llm.invoke(prompt)
        
        title = response.strip()
        title = re.sub(r'^(Title:\s*|The title is:\s*|"\s*|Title\s*[-:]\s*)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'["\n\r]+', '', title)
        title = title.strip()
        
        if title and 5 <= len(title) <= 100 and not title.lower().startswith(('i ', 'the document', 'this document')):
            return title
        else:
            return extract_title_heuristic(content, filename)
            
    except Exception as e:
        logger.error(f"Error extracting title with Ollama: {e}")
        return extract_title_heuristic(content, filename)

def extract_title_heuristic(content: str, filename: str) -> str:
    lines = content.strip().split('\n')
    
    while lines and not lines[0].strip():
        lines.pop(0)
    
    if not lines:
        return os.path.splitext(filename)[0]
    
    for line in lines[:10]:
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
        elif line.startswith('## '):
            return line[3:].strip()
    
    for line in lines[:5]:
        line = line.strip()
        if line and len(line) < 100:
            if not any(pattern in line.lower() for pattern in ['date:', 'author:', 'email:', 'http']):
                if len(line.split()) >= 2:
                    return line
    
    return os.path.splitext(filename)[0]

async def upload(doc: UploadFile, ollama_base_url: str, extraction_method: str = "ollama", ollama_model: str = "gemma3:1b") -> UploadFileResponse:
    # Check if file is allowed
    if not is_allowed_file(doc):
        allowed_extensions = [".pdf", ".md", ".txt"]
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed file extensions are: {allowed_extensions}. Received: {doc.content_type} for {doc.filename}"
        )
    
    # Get effective content type (handles application/octet-stream cases)
    effective_content_type = get_effective_content_type(doc)
    
    # Clean the filename to remove URL encoding
    clean_name = clean_filename(doc.filename)
    
    logger.info(f"Uploading {clean_name} - Original MIME: {doc.content_type}, Effective: {effective_content_type}")
    
    content = await doc.read()
    file_id = create_id()
    extracted_title = None

    if effective_content_type == "application/pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(content)
            temp_pdf_path = temp_pdf.name
        
        try:
            markdown_content = pymupdf4llm.to_markdown(temp_pdf_path)
            
            if extraction_method == "ollama":
                extracted_title = extract_title_ollama(markdown_content, clean_name, ollama_base_url, ollama_model)
            else:
                extracted_title = extract_title_heuristic(markdown_content, clean_name)
            
        except Exception as e:
            os.unlink(temp_pdf_path)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to convert PDF to markdown: {str(e)}"
            )
        finally:
            os.unlink(temp_pdf_path)
        
        og_name, _ = os.path.splitext(clean_name)  # Use cleaned name
        markdown_filename = f"{og_name}-{file_id}.md"
        
        with open(f"/docs/{markdown_filename}", "w", encoding="utf-8") as md_file:
            md_file.write(markdown_content)

        # Save original file with cleaned name
        with open(f"/docs/{clean_name}", "wb") as pdf_file:
            pdf_file.write(content)

        return UploadFileResponse(
            id=file_id,
            path=markdown_filename,
            og_path=clean_name,  # Use cleaned name
            name=extracted_title,
            message="PDF uploaded and converted to markdown successfully",
            size=len(markdown_content)
        )

    else: 
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail=f"File {clean_name} is not a valid text file"
            )
        
        if extraction_method == "ollama":
            extracted_title = extract_title_ollama(text_content, clean_name, ollama_base_url, ollama_model)
        else:
            extracted_title = extract_title_heuristic(text_content, clean_name)
        
        if effective_content_type == "text/markdown" or clean_name.endswith('.md'):
            file_extension = "md"
        else:
            file_extension = "txt"
            
        filename = f"{file_id}.{file_extension}"
        
        with open(f"/docs/{filename}", "wb") as file:
            file.write(content)

        # Save original file with cleaned name
        with open(f"/docs/{clean_name}", "wb") as original_file:
            original_file.write(content)
        
        return UploadFileResponse(
            id=file_id,
            path=filename,
            og_path=clean_name,
            name=extracted_title or os.path.splitext(clean_name)[0],
            message="File uploaded successfully",
            size=len(content)
        )