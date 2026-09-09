import re

INTENT_KEYWORDS = {
    "PMFBY_CLAIM": [
        "pmfby", "crop insurance", "claim", "claims", "harvest", "crop loss", "yield loss",
        "indemnity", "localized calamity", "post-harvest", "mid-season adversity", "surveyor",
        "72 hours", "insurance company", "fasal bima", "crop damage"
    ],
    "COOPERATIVE_BYLAW": [
        "bylaw", "by-law", "by laws", "membership", "voting rights", "share capital", "dividend",
        "quorum", "managing committee", "board of directors", "general body", "agm", "registrar",
        "expulsion of member", "pacs", "cooperative society", "audit", "bye-law"
    ],
    "SCHEME_ELIGIBILITY": [
        "eligible", "eligibility", "criteria", "subsidy", "interest subvention", "kisan credit card",
        "kcc", "loan limit", "scale of finance", "small farmer", "marginal farmer", "tenant farmer",
        "scheme", "qualification", "how to apply"
    ],
    "GRIEVANCE": [
        "grievance", "complaint", "fraud", "delay", "rejection", "dispute", "appeal",
        "ombudsman", "redressal", "officer review", "helpline", "escalate", "cheat", "corrupt"
    ]
}

SENSITIVE_INTENTS = {"PMFBY_CLAIM", "COOPERATIVE_BYLAW", "GRIEVANCE"}

def detect_intent(query: str) -> str:
    """Classifies the user query into a domain-specific cooperative intent."""
    normalized = query.lower()
    scores = {}
    for intent, kws in INTENT_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in normalized)
        if score > 0:
            scores[intent] = score
            
    if not scores:
        return "GENERAL_INFO"
    
    return max(scores.items(), key=lambda x: x[1])[0]

def is_sensitive_intent(intent: str) -> bool:
    """Returns True if the intent requires the strict SENSITIVE_CONFIDENCE_THRESHOLD."""
    return intent in SENSITIVE_INTENTS
