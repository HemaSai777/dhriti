from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from app.database import get_db
from app.models.ticket import Ticket
from app.services.retrieval import retriever
from app.config import settings

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("", response_model=Dict[str, Any])
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_tickets = db.query(Ticket).count()
    pending = db.query(Ticket).filter(Ticket.status == "PENDING").count()
    under_review = db.query(Ticket).filter(Ticket.status == "UNDER_REVIEW").count()
    resolved = db.query(Ticket).filter(Ticket.status == "RESOLVED").count()
    escalated = db.query(Ticket).filter(Ticket.status == "ESCALATED").count()
    
    avg_conf_row = db.query(func.avg(Ticket.confidence)).first()
    avg_confidence = round(float(avg_conf_row[0] or 0.0), 2)

    docs_dir = settings.DOCUMENTS_DIR
    doc_count = len(list(docs_dir.glob("*.txt")) + list(docs_dir.glob("*.pdf"))) if docs_dir.exists() else 0
    chunk_count = len(retriever.chunks)

    return {
        "total_tickets": total_tickets,
        "pending": pending,
        "under_review": under_review,
        "resolved": resolved,
        "escalated": escalated,
        "avg_confidence": avg_confidence,
        "total_documents": doc_count,
        "total_chunks": chunk_count,
        "safety_threshold": settings.CONFIDENCE_THRESHOLD,
        "sensitive_threshold": settings.SENSITIVE_CONFIDENCE_THRESHOLD
    }
