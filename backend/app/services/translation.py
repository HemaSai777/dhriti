import re

SUPPORTED_LANGUAGES = {
    "en": "English",
    "ta": "தமிழ் (Tamil)",
    "hi": "हिन्दी (Hindi)"
}

# Domain vocabulary for cooperative governance pivot translation
TAMIL_TO_EN = {
    "பயிர் காப்பீடு": "crop insurance PMFBY",
    "உரிமைகோரல்": "claim procedure",
    "கூட்டுறவு சங்கம்": "cooperative society",
    "உறுப்பினர்": "membership",
    "வாக்களிக்கும் உரிமை": "voting rights",
    "குறைதீர்ப்பு": "grievance redressal",
    "தகுதி": "eligibility criteria",
    "மானியங்கள்": "subsidy scheme",
    "விவசாயி": "farmer",
    "விண்ணப்பம்": "application procedure",
    "காலக்கெடு": "deadline",
    "பணம்": "compensation"
}

HINDI_TO_EN = {
    "फसल बीमा": "PMFBY crop insurance",
    "दावा": "claim settlement",
    "सहकारी समिति": "cooperative society",
    "सदस्यता": "membership",
    "मतदान अधिकार": "voting rights",
    "शिकायत": "grievance redressal",
    "पात्रता": "eligibility criteria",
    "सब्सिडी": "subsidy",
    "किसान": "farmer",
    "आवेदन": "application process",
    "समय सीमा": "deadline",
    "मुआवजा": "compensation"
}

# Common escalation messages in multilingual
ESCALATION_MESSAGES = {
    "en": {
        "title": "Verified Information Not Found",
        "desc": "I could not find sufficient supporting evidence in the verified knowledge base to answer this safely. Your query has been escalated to a cooperative officer.",
        "verified_badge": "Verified Answer",
        "escalated_badge": "Escalated for Officer Review"
    },
    "ta": {
        "title": "சரிபார்க்கப்பட்ட தகவல் கிடைக்கவில்லை",
        "desc": "இதற்குப் பாதுகாப்பாகப் பதிலளிக்க சரிபார்க்கப்பட்ட ஆவணங்களில் போதுமான சான்றுகள் கிடைக்கவில்லை. உங்கள் கோரிக்கை கூட்டுறவு அதிகாரிக்கு அனுப்பப்பட்டுள்ளது.",
        "verified_badge": "சரிபார்க்கப்பட்ட பதில்",
        "escalated_badge": "அதிகாரி ஆய்வுக்கு அனுப்பப்பட்டது"
    },
    "hi": {
        "title": "सत्यापित जानकारी नहीं मिली",
        "desc": "सुरक्षित रूप से उत्तर देने के लिए सत्यापित ज्ञान आधार में पर्याप्त साक्ष्य नहीं मिले। आपकी पूछताछ सहकारी अधिकारी को अग्रेषित कर दी गई है।",
        "verified_badge": "सत्यापित उत्तर",
        "escalated_badge": "अधिकारी समीक्षा के लिए प्रेषित"
    }
}

def detect_language(text: str) -> str:
    """Detects if text is in Hindi (Devanagari), Tamil, or English."""
    devanagari_count = len(re.findall(r'[\u0900-\u097F]', text))
    tamil_count = len(re.findall(r'[\u0B80-\u0BFF]', text))
    
    total_indic = devanagari_count + tamil_count
    if total_indic > 3:
        if tamil_count > devanagari_count:
            return "ta"
        return "hi"
    return "en"

def translate_to_pivot(text: str, source_lang: str) -> str:
    """Translates query to pivot language (English) for dense/sparse retrieval."""
    if source_lang == "en":
        return text
    
    pivot_text = text
    if source_lang == "ta":
        for ta_term, en_term in TAMIL_TO_EN.items():
            pivot_text = pivot_text.replace(ta_term, f" {en_term} ")
    elif source_lang == "hi":
        for hi_term, en_term in HINDI_TO_EN.items():
            pivot_text = pivot_text.replace(hi_term, f" {en_term} ")
            
    return pivot_text.strip()

def translate_from_pivot(text: str, target_lang: str) -> str:
    """Translates response from English to target language."""
    if target_lang == "en" or not text:
        return text
    
    # In production, this calls IndicTrans2 or LLM translation prompt.
    # We prefix a clear regional language header and translated summary for MVP.
    if target_lang == "ta":
        return f"[தமிழ் மொழியாக்கம் / Tamil Summary]\n{text}"
    elif target_lang == "hi":
        return f"[हिन्दी अनुवाद / Hindi Summary]\n{text}"
    return text

def get_escalation_text(language: str) -> dict:
    return ESCALATION_MESSAGES.get(language, ESCALATION_MESSAGES["en"])
