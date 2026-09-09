import json
import re
from typing import List, Dict, Any
from app.config import settings

SYSTEM_PROMPT = """You are SAHAYA, a legal and cooperative governance information assistant.

You MUST answer ONLY using the supplied verified evidence.
Do not use your pretrained knowledge for legal, financial, government scheme or cooperative-rule claims.
Every factual claim must be supported by the supplied evidence.
Cite the source for every important factual statement.
If the evidence is insufficient, conflicting, outdated, or does not directly support the answer, return INSUFFICIENT_EVIDENCE.

Never invent:
* laws
* deadlines
* eligibility criteria
* monetary amounts
* government rules
* section numbers
* document names
* citations

You are an information assistant, not a lawyer or financial advisor.

You MUST respond strictly in valid JSON format matching one of these two structures:

If the evidence supports the answer:
{
  "status": "SUPPORTED",
  "answer": "Clear, direct, factual answer strictly from the evidence...",
  "citations": [
    {
      "document": "Exact document name from evidence",
      "page": 42,
      "section": "Exact section name from evidence",
      "claim": "The specific verified statement"
    }
  ]
}

If the evidence is insufficient or missing key details:
{
  "status": "INSUFFICIENT_EVIDENCE",
  "answer": null,
  "citations": []
}
"""

def format_evidence_prompt(query: str, chunks: List[Dict[str, Any]]) -> str:
    evidence_blocks = []
    for idx, c in enumerate(chunks, 1):
        block = f"--- EVIDENCE ITEM {idx} ---\n"
        block += f"DOCUMENT: {c.get('document_title', c.get('source'))}\n"
        block += f"FILE: {c.get('source')}\n"
        block += f"PAGE: {c.get('page')}\n"
        block += f"SECTION: {c.get('section')}\n"
        block += f"TEXT:\n{c.get('text')}\n"
        evidence_blocks.append(block)

    prompt = f"USER QUESTION:\n{query}\n\n"
    prompt += "VERIFIED EVIDENCE FRAGMENTS:\n"
    prompt += "\n".join(evidence_blocks) if evidence_blocks else "NO EVIDENCE FOUND."
    prompt += "\n\nProvide your JSON response:"
    return prompt

def grounded_demo_synthesis(query: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic grounded fallback synthesizer when external LLM API key is not configured.
    Strictly answers from top retrieved evidence chunks or rejects if evidence is inadequate.
    """
    if not chunks:
        return {"status": "INSUFFICIENT_EVIDENCE", "answer": None, "citations": []}

    top_chunk = chunks[0]
    # If the top retrieval score is weak (< 0.40), strictly refuse to answer
    if top_chunk.get("score", 0.0) < 0.40:
        return {"status": "INSUFFICIENT_EVIDENCE", "answer": None, "citations": []}

    STOPWORDS = {
        "what", "which", "where", "when", "who", "whom", "this", "that", "these", "those",
        "have", "has", "does", "under", "about", "scheme", "government", "rules", "with",
        "without", "from", "into", "tell", "explain", "give", "procedure", "please", "some"
    }

    # Extract informative query terms
    all_query_terms = re.findall(r'\b[a-zA-Z0-9]{3,}\b', query.lower())
    content_query_terms = [t for t in all_query_terms if t not in STOPWORDS]

    # Check if critical premise terms (e.g. "waiver", "lakh") are completely missing from top evidence
    evidence_corpus = " ".join([c["text"].lower() for c in chunks])
    missing_critical_terms = [t for t in content_query_terms if t not in evidence_corpus]
    
    # If critical specific query nouns like "waiver" are completely missing from evidence:
    if any(term in ["waiver", "waive", "forgive", "cancelled"] for term in missing_critical_terms):
        return {"status": "INSUFFICIENT_EVIDENCE", "answer": None, "citations": []}

    relevant_sentences = []
    citations = []

    for c in chunks[:3]:
        sentences = re.split(r'(?<=[.!?])\s+', c["text"])
        chunk_citations = []
        for s in sentences:
            s_clean = s.strip()
            if not s_clean or len(s_clean) < 25:
                continue
            matching_terms = sum(1 for t in content_query_terms if t in s_clean.lower())
            # Require at least 2 distinct content words to match
            if matching_terms >= 2:
                relevant_sentences.append(s_clean)
                chunk_citations.append({
                    "document": c.get("document_title", c.get("source")),
                    "page": c.get("page", 1),
                    "section": c.get("section", "General Provisions"),
                    "claim": s_clean[:120] + "..." if len(s_clean) > 120 else s_clean
                })
        if chunk_citations and len(citations) < 3:
            citations.extend(chunk_citations[:2])

    # If no sentences adequately match the key content terms, fail safely
    if not relevant_sentences or len(citations) == 0:
        return {"status": "INSUFFICIENT_EVIDENCE", "answer": None, "citations": []}

    # Formulate verified answer
    unique_sentences = list(dict.fromkeys(relevant_sentences[:4]))
    synthesized_answer = " ".join(unique_sentences)

    return {
        "status": "SUPPORTED",
        "answer": synthesized_answer,
        "citations": citations
    }

async def call_llm(query: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calls configured LLM provider (Gemini, OpenAI, Ollama) or falls back to grounded synthesis.
    """
    # Check if external LLM configured
    if settings.LLM_API_KEY and settings.LLM_PROVIDER == "gemini":
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.LLM_API_KEY)
            model = genai.GenerativeModel(
                model_name=settings.LLM_MODEL,
                system_instruction=SYSTEM_PROMPT
            )
            prompt = format_evidence_prompt(query, chunks)
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
                request_options={"timeout": 25.0}
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text)
            parsed = json.loads(raw_text)
            return parsed
        except Exception as e:
            print(f"[RAG] Gemini API call error: {e}. Falling back to grounded synthesis engine.")
            return grounded_demo_synthesis(query, chunks)
    
    # Fallback to local grounded synthesis engine
    return grounded_demo_synthesis(query, chunks)
