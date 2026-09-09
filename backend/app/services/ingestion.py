import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from app.config import settings

# Attempt to import PyMuPDF (fitz)
try:
    import fitz  # PyMuPDF
    HAVE_PYMUPDF = True
except ImportError:
    HAVE_PYMUPDF = False

def clean_text(text: str) -> str:
    """Removes irregular whitespace, non-printable characters, and standardizes spacing."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\r\n\t]+', ' ', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 250, overlap: int = 50) -> List[str]:
    """Splits text into sliding window word chunks with overlap."""
    words = text.split()
    if not words:
        return []
    
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if len(chunk.strip()) > 30:  # Avoid empty or trivial chunks
            chunks.append(chunk)
        if end == len(words):
            break
        start += (chunk_size - overlap)
    return chunks

def extract_section_name(text: str) -> str:
    """Heuristic to detect chapter/section/rule titles like 'Section 14: Claims', 'Clause 3.2'."""
    match = re.search(r'(?:Section|Clause|Rule|Article|Chapter)\s+([0-9A-Za-z\.\-]+)(?:\s*[:\-–]\s*([^\.\n]+))?', text, re.IGNORECASE)
    if match:
        sec_num = match.group(1)
        sec_title = match.group(2)
        if sec_title:
            return f"Section {sec_num}: {sec_title.strip()[:40]}"
        return f"Section {sec_num}"
    
    # Check for uppercase heading lines
    heading_match = re.search(r'([A-Z\s]{4,30})(?:\n|\:)', text)
    if heading_match:
        return heading_match.group(1).strip()
    return "General Provisions"

def parse_txt_file(file_path: Path) -> List[Dict[str, Any]]:
    """Parses a structured TXT document containing page or section markers."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    filename = file_path.name
    doc_id = file_path.stem.upper().replace(" ", "_")
    title = file_path.stem.replace("_", " ")
    
    # Check if text contains explicit [PAGE X] or --- Page X --- markers
    page_splits = re.split(r'(?:\[PAGE\s+(\d+)\]|---+\s*Page\s+(\d+)\s*---+)', content, flags=re.IGNORECASE)
    chunks_data = []
    
    if len(page_splits) > 1:
        current_page = 1
        i = 0
        while i < len(page_splits):
            part = page_splits[i]
            if part is None:
                i += 1
                continue
            if part.isdigit():
                current_page = int(part)
                i += 1
                continue
            
            # Text body for this page
            page_text = clean_text(part)
            if page_text:
                page_chunks = chunk_text(page_text)
                for chunk in page_chunks:
                    section = extract_section_name(chunk)
                    chunks_data.append({
                        "document_id": doc_id,
                        "document_title": title,
                        "source": filename,
                        "page": current_page,
                        "section": section,
                        "text": chunk
                    })
            i += 1
    else:
        # Fallback: estimate page numbers roughly every 350 words
        cleaned = clean_text(content)
        raw_chunks = chunk_text(cleaned, chunk_size=200, overlap=40)
        for idx, chunk in enumerate(raw_chunks):
            page_num = (idx // 2) + 1
            section = extract_section_name(chunk)
            chunks_data.append({
                "document_id": doc_id,
                "document_title": title,
                "source": filename,
                "page": page_num,
                "section": section,
                "text": chunk
            })
            
    return chunks_data

def parse_pdf_file(file_path: Path) -> List[Dict[str, Any]]:
    """Extracts text page-by-page from PDF files using PyMuPDF."""
    if not HAVE_PYMUPDF:
        print(f"[Ingestion] PyMuPDF not available, skipping PDF {file_path.name}")
        return []
    
    filename = file_path.name
    doc_id = file_path.stem.upper().replace(" ", "_")
    title = file_path.stem.replace("_", " ")
    chunks_data = []
    
    try:
        doc = fitz.open(str(file_path))
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            cleaned = clean_text(text)
            if not cleaned:
                continue
            
            page_chunks = chunk_text(cleaned, chunk_size=200, overlap=40)
            for chunk in page_chunks:
                section = extract_section_name(chunk)
                chunks_data.append({
                    "document_id": doc_id,
                    "document_title": title,
                    "source": filename,
                    "page": page_num + 1,
                    "section": section,
                    "text": chunk
                })
        doc.close()
    except Exception as e:
        print(f"[Ingestion] Error parsing PDF {file_path.name}: {e}")
        
    return chunks_data

def ingest_all_documents() -> List[Dict[str, Any]]:
    """Scans settings.DOCUMENTS_DIR for PDFs and TXTs, generates chunks, and writes chunks.json."""
    docs_dir = settings.DOCUMENTS_DIR
    index_dir = settings.INDEX_DIR
    docs_dir.mkdir(parents=True, exist_ok=True)
    index_dir.mkdir(parents=True, exist_ok=True)
    
    all_chunks = []
    files = list(docs_dir.glob("*.txt")) + list(docs_dir.glob("*.pdf"))
    
    print(f"[Ingestion] Found {len(files)} files in {docs_dir}")
    for f in files:
        if f.suffix.lower() == ".txt":
            chunks = parse_txt_file(f)
            all_chunks.extend(chunks)
            print(f"[Ingestion] Processed {f.name}: {len(chunks)} chunks")
        elif f.suffix.lower() == ".pdf":
            chunks = parse_pdf_file(f)
            all_chunks.extend(chunks)
            print(f"[Ingestion] Processed PDF {f.name}: {len(chunks)} chunks")
            
    # Save indexed chunks
    output_path = index_dir / "chunks.json"
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(all_chunks, out, indent=2, ensure_ascii=False)
        
    print(f"[Ingestion] Complete! Stored {len(all_chunks)} chunks in {output_path}")
    return all_chunks
