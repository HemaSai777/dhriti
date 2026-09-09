import json
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.ticket import Ticket

router = APIRouter(prefix="/tickets", tags=["Tickets"])

class TicketUpdate(BaseModel):
    status: Optional[str] = None  # PENDING, UNDER_REVIEW, RESOLVED, ESCALATED
    officer_notes: Optional[str] = None

class TicketResponse(BaseModel):
    id: str
    user_id: str
    query: str
    language: str
    intent: str
    confidence: float
    reason: Optional[str]
    status: str
    officer_notes: Optional[str]
    candidate_chunks: Optional[List[Dict[str, Any]]] = None
    created_at: str
    updated_at: str

def format_ticket(t: Ticket) -> Dict[str, Any]:
    chunks = []
    if t.candidate_chunks:
        try:
            chunks = json.loads(t.candidate_chunks)
        except Exception:
            chunks = []
            
    return {
        "id": t.id,
        "user_id": t.user_id,
        "query": t.query,
        "language": t.language,
        "intent": t.intent,
        "confidence": t.confidence,
        "reason": t.reason,
        "status": t.status,
        "officer_notes": t.officer_notes,
        "candidate_chunks": chunks,
        "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else "",
        "updated_at": t.updated_at.strftime("%Y-%m-%d %H:%M:%S") if t.updated_at else ""
    }

@router.get("", response_model=List[Dict[str, Any]])
def list_tickets(
    status: Optional[str] = Query(None),
    intent: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Ticket)
    if status and status != "ALL":
        query = query.filter(Ticket.status == status)
    if intent and intent != "ALL":
        query = query.filter(Ticket.intent == intent)
    if language and language != "ALL":
        query = query.filter(Ticket.language == language)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter((Ticket.query.ilike(search_fmt)) | (Ticket.id.ilike(search_fmt)))

    tickets = query.order_by(desc(Ticket.created_at)).all()
    return [format_ticket(t) for t in tickets]

@router.get("/{ticket_id}", response_model=Dict[str, Any])
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not t:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return format_ticket(t)

@router.patch("/{ticket_id}", response_model=Dict[str, Any])
def update_ticket(ticket_id: str, update: TicketUpdate, db: Session = Depends(get_db)):
    t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not t:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    
    if update.status:
        valid_statuses = ["PENDING", "UNDER_REVIEW", "RESOLVED", "ESCALATED"]
        if update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")
        t.status = update.status

    if update.officer_notes is not None:
        t.officer_notes = update.officer_notes

    db.commit()
    db.refresh(t)
    return format_ticket(t)
