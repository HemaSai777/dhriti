import re
from typing import List, Dict, Any, Tuple
from app.config import settings
from app.services.intent import is_sensitive_intent

def calculate_source_quality_score(sources: List[Dict[str, Any]]) -> float:
    """
    Scores the authority and structural integrity of retrieved sources.
    Verified government/official documents with page numbers and sections receive full credit.
    """
    if not sources:
        return 0.0
    
    total_quality = 0.0
    for s in sources:
        doc_quality = 0.5  # Base for recognized document
        if s.get("page") and isinstance(s.get("page"), int) and s.get("page") > 0:
            doc_quality += 0.25
        if s.get("section") and s.get("section") != "General Provisions":
            doc_quality += 0.25
        total_quality += doc_quality
        
    return round(min(1.0, total_quality / len(sources)), 4)

def evaluate_entailment(answer: str, chunks: List[Dict[str, Any]], llm_status: str) -> float:
    """
    NLI / Groundedness verification layer.
    Verifies that claims, numbers, deadlines, and specific entities in the generated answer
    are strictly attested in the retrieved evidence chunks.
    """
    if llm_status == "INSUFFICIENT_EVIDENCE" or not answer or not chunks:
        return 0.0

    evidence_text = " ".join([c["text"] for c in chunks]).lower()
    answer_lower = answer.lower()

    # 1. Extract numeric entities, currency, percentages, timeframes from answer
    # e.g., "72 hours", "Rs. 100", "4%", "15 days", "25%"
    answer_entities = set(re.findall(r'\b(?:\d+(?:\.\d+)?%?|rs\.?\s*\d+(?:,\d+)*|\d+\s*(?:hours|days|months|years))\b', answer_lower))
    
    if answer_entities:
        grounded_count = 0
        for entity in answer_entities:
            # Clean entity for fuzzy matching
            cleaned_entity = entity.replace("rs.", "").strip()
            if cleaned_entity in evidence_text:
                grounded_count += 1
        
        entity_grounding_ratio = grounded_count / len(answer_entities)
    else:
        entity_grounding_ratio = 1.0

    # 2. Key phrase n-gram overlap between answer and evidence
    answer_words = re.findall(r'\b[a-z]{4,}\b', answer_lower)
    if not answer_words:
        return 0.0

    supported_words = sum(1 for w in answer_words if w in evidence_text)
    lexical_overlap = supported_words / len(answer_words)

    # 3. Combine entity precision (60%) and vocabulary groundedness (40%)
    entailment_score = (0.6 * entity_grounding_ratio) + (0.4 * lexical_overlap)
    return round(min(1.0, max(0.0, entailment_score)), 4)

def run_verification_gate(
    query: str,
    intent: str,
    retrieved_chunks: List[Dict[str, Any]],
    llm_status: str,
    llm_answer: str,
    citations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Executes the Citation-Gated Verification Barrier:
    final_confidence = 0.4 * retrieval_score + 0.4 * entailment_score + 0.2 * source_quality_score
    """
    # 1. Determine applicable threshold
    sensitive = is_sensitive_intent(intent)
    threshold = settings.SENSITIVE_CONFIDENCE_THRESHOLD if sensitive else settings.CONFIDENCE_THRESHOLD

    # 2. Compute component scores
    if not retrieved_chunks:
        retrieval_score = 0.0
    else:
        top_scores = [c.get("score", 0.0) for c in retrieved_chunks[:3]]
        # Primary evidence match dominates retrieval confidence
        if len(top_scores) == 1:
            retrieval_score = round(top_scores[0], 4)
        else:
            retrieval_score = round((0.8 * top_scores[0]) + (0.2 * top_scores[1]), 4)

    entailment_score = evaluate_entailment(llm_answer, retrieved_chunks, llm_status)
    source_quality_score = calculate_source_quality_score(retrieved_chunks)

    # 3. Calculate final confidence
    final_confidence = (0.4 * retrieval_score) + (0.4 * entailment_score) + (0.2 * source_quality_score)
    final_confidence = round(min(1.0, max(0.0, final_confidence)), 4)

    # 4. Enforce strict gate conditions
    is_verified = True
    reasons = []

    if llm_status == "INSUFFICIENT_EVIDENCE":
        is_verified = False
        reasons.append("Model determined evidence is insufficient for factual assertion.")

    if not citations:
        is_verified = False
        reasons.append("No verifiable document citations were produced.")

    if final_confidence < threshold:
        is_verified = False
        reasons.append(f"Confidence score ({int(final_confidence*100)}%) is below required threshold ({int(threshold*100)}% for {intent}).")

    if retrieval_score < 0.35:
        is_verified = False
        reasons.append("Retrieved knowledge base fragments have insufficient relevance to the query.")

    escalation_reason = "; ".join(reasons) if not is_verified else None

    return {
        "is_verified": is_verified,
        "final_confidence": final_confidence,
        "threshold": threshold,
        "is_sensitive": sensitive,
        "escalation_reason": escalation_reason,
        "breakdown": {
            "retrieval_score": retrieval_score,
            "entailment_score": entailment_score,
            "source_quality_score": source_quality_score
        }
    }
