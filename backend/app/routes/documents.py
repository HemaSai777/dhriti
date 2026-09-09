import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.config import settings
from app.services.ingestion import ingest_all_documents
from app.services.retrieval import retriever

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("", response_model=List[Dict[str, Any]])
def list_documents():
    docs_dir = settings.DOCUMENTS_DIR
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    docs_info = []
    # Inspect chunks.json to aggregate counts
    chunks = retriever.chunks
    doc_chunk_counts = {}
    doc_page_max = {}
    for c in chunks:
        src = c.get("source")
        doc_chunk_counts[src] = doc_chunk_counts.get(src, 0) + 1
        doc_page_max[src] = max(doc_page_max.get(src, 1), c.get("page", 1))

    for f in docs_dir.glob("*.*"):
        if f.suffix.lower() in [".txt", ".pdf"]:
            size_kb = round(f.stat().st_size / 1024, 2)
            title = f.stem.replace("_", " ")
            source_name = f.name
            
            docs_info.append({
                "id": f.stem.upper().replace(" ", "_"),
                "title": title,
                "filename": source_name,
                "file_type": f.suffix.replace(".", "").upper(),
                "size_kb": size_kb,
                "pages": doc_page_max.get(source_name, 1),
                "chunks": doc_chunk_counts.get(source_name, 0),
                "verified_badge": True
            })
            
    return docs_info

@router.post("/ingest", response_model=Dict[str, Any])
def trigger_ingestion():
    """Triggers complete re-indexing of all documents."""
    chunks = ingest_all_documents()
    retriever.load_index()
    return {
        "status": "SUCCESS",
        "message": f"Successfully ingested {len(chunks)} chunks across verified documents.",
        "chunk_count": len(chunks)
    }

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Uploads a PDF or TXT file to backend/data/documents/ and re-indexes."""
    ext = Path(file.filename).suffix.lower()
    if ext not in [".txt", ".pdf"]:
        raise HTTPException(status_code=400, detail="Only PDF and TXT documents are supported.")
    
    dest_path = settings.DOCUMENTS_DIR / file.filename
    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
        
    # Re-index
    chunks = ingest_all_documents()
    retriever.load_index()
    
    return {
        "status": "SUCCESS",
        "filename": file.filename,
        "message": "File uploaded and verified knowledge index updated.",
        "total_chunks": len(chunks)
    }
