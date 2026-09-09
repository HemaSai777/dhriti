import json
import random
import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ticket import Ticket
from app.services.intent import detect_intent
from app.services.translation import detect_language, translate_to_pivot, translate_from_pivot, get_escalation_text
from app.services.retrieval import retriever
from app.services.rag import call_llm
from app.services.verification import run_verification_gate

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    query: str
    language: Optional[str] = "en"
    user_id: Optional[str] = "citizen-demo"

class SourceCitation(BaseModel):
    document: str
    page: int
    section: str
    score: float
    claim: Optional[str] = None

class ChatResponse(BaseModel):
    status: str  # "SUPPORTED" or "ESCALATED"
    answer: Optional[str] = None
    confidence: float
    threshold: float
    intent: str
    language: str
    sources: List[Dict[str, Any]]
    ticket_id: Optional[str] = None
    reason: Optional[str] = None
    breakdown: Optional[Dict[str, float]] = None

def generate_ticket_id() -> str:
    year = datetime.datetime.now().year
    rand_num = random.randint(10000, 99999)
    return f"GRV-{year}-{rand_num}"

@router.post("", response_model=ChatResponse)
async def process_chat(req: ChatRequest, db: Session = Depends(get_db)):
    raw_query = req.query.strip()
    if not raw_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. Detect language (or honor requested)
    detected_lang = detect_language(raw_query)
    lang = req.language if req.language in ["en", "ta", "hi"] else detected_lang

    # 2. Translate to pivot language (English)
    pivot_query = translate_to_pivot(raw_query, lang)

    # 3. Detect intent & sensitivity
    intent = detect_intent(pivot_query)

    # 4. Perform Hybrid Retrieval (BM25 + Dense Semantic)
    retrieved_chunks = retriever.hybrid_search(pivot_query, top_k=5)

    # 5. Send retrieved evidence to Citation-Gated LLM
    llm_output = await call_llm(pivot_query, retrieved_chunks)
    llm_status = llm_output.get("status", "INSUFFICIENT_EVIDENCE")
    llm_answer = llm_output.get("answer")
    llm_citations = llm_output.get("citations", [])

    # 6. Run Verification Gate
    gate_result = run_verification_gate(
        query=pivot_query,
        intent=intent,
        retrieved_chunks=retrieved_chunks,
        llm_status=llm_status,
        llm_answer=llm_answer,
        citations=llm_citations
    )

    # 7. Check Gate Outcome
    if gate_result["is_verified"]:
        # Translate verified answer back to selected language if necessary
        final_answer = translate_from_pivot(llm_answer, lang)

        # Build clean citation list
        formatted_sources = []
        for c in retrieved_chunks[:3]:
            formatted_sources.append({
                "document": c["document_title"],
                "page": c["page"],
                "section": c["section"],
                "score": c["score"],
                "excerpt": c["text"][:180] + "..." if len(c["text"]) > 180 else c["text"]
            })

        return ChatResponse(
            status="SUPPORTED",
            answer=final_answer,
            confidence=gate_result["final_confidence"],
            threshold=gate_result["threshold"],
            intent=intent,
            language=lang,
            sources=formatted_sources,
            ticket_id=None,
            reason=None,
            breakdown=gate_result["breakdown"]
        )
    else:
        # NO EVIDENCE -> NO ANSWER -> HUMAN ESCALATION
        # Answer is strictly DISCARDED.
        ticket_id = generate_ticket_id()
        escalation_reason = gate_result["escalation_reason"] or "Insufficient verified evidence in knowledge base."

        # Save Grievance Ticket in SQLite database for the Officer Portal
        candidate_summary = [
            {
                "title": c.get("document_title"),
                "page": c.get("page"),
                "section": c.get("section"),
                "score": c.get("score"),
                "excerpt": c.get("text", "")[:200]
            } for c in retrieved_chunks
        ]

        ticket = Ticket(
            id=ticket_id,
            user_id=req.user_id or "citizen-demo",
            query=raw_query,
            language=lang,
            intent=intent,
            confidence=gate_result["final_confidence"],
            reason=escalation_reason,
            candidate_chunks=json.dumps(candidate_summary, ensure_ascii=False),
            status="PENDING",
            created_at=datetime.datetime.utcnow()
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return ChatResponse(
            status="ESCALATED",
            answer=None,  # Suppressed completely
            confidence=gate_result["final_confidence"],
            threshold=gate_result["threshold"],
            intent=intent,
            language=lang,
            sources=[],
            ticket_id=ticket_id,
            reason=escalation_reason,
            breakdown=gate_result["breakdown"]
        )
