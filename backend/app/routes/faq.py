from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/faq", tags=["FAQ"])

OFFLINE_FAQS: List[Dict[str, Any]] = [
    {
        "id": "FAQ-01",
        "question": "What is the deadline to report crop damage under PMFBY?",
        "answer": "Under Section 11 of PMFBY Guidelines, an insured farmer must notify the Insurance Company, Agriculture Department official, or PACS within 72 hours of the localized calamity (hailstorm, landslide, inundation, cloud burst).",
        "source": "PMFBY Operational Guidelines (Page 42, Section 11)",
        "cached": True
    },
    {
        "id": "FAQ-02",
        "question": "What is the maximum premium rate payable by farmers for Kharif food crops?",
        "answer": "According to PMFBY Guidelines Section 4, the maximum premium payable by the farmer is 2.0% of Sum Insured for Kharif food and oilseed crops, 1.5% for Rabi crops, and 5.0% for Annual Commercial/Horticultural crops.",
        "source": "PMFBY Operational Guidelines (Page 18, Section 4)",
        "cached": True
    },
    {
        "id": "FAQ-03",
        "question": "Who is eligible to become an ordinary member of a Primary Agricultural Credit Society (PACS)?",
        "answer": "Under Rule 14 of PACS Model By-laws, an individual must be an Indian citizen of at least 18 years of age, sound mind, hold agricultural land or tenant farming rights in the operational area, and purchase at least 1 share of Rs. 100 with Rs. 10 entrance fee.",
        "source": "PACS Model By-laws (Page 12, Chapter III, Rule 14)",
        "cached": True
    },
    {
        "id": "FAQ-04",
        "question": "What is the effective interest rate for prompt repayment of crop loans under Kisan Credit Card?",
        "answer": "Under RBI/NABARD Modified Interest Subvention Scheme (MISS), short-term crop loans up to Rs. 3,00,000 carry a base rate of 9%, with 2% government subvention and 3% prompt repayment incentive, resulting in a net 4.0% per annum effective rate.",
        "source": "KCC and Subsidy Norms (Page 16, Chapter V, Norm 12)",
        "cached": True
    },
    {
        "id": "FAQ-05",
        "question": "What are the stages of escalating an unresolved cooperative grievance?",
        "answer": "The grievance protocol provides a 3-tier hierarchy: Tier 1 (Society Nodal Officer - 15 days), Tier 2 (District Deputy Registrar of Cooperatives - 30 days), Tier 3 (State Cooperative Ombudsman/Tribunal - 45 days).",
        "source": "PACS Grievance Redressal Protocol (Page 14, Section 5, Clause 5.2)",
        "cached": True
    }
]

@router.get("", response_model=List[Dict[str, Any]])
def get_offline_faqs():
    """Returns static verified FAQ cache for offline kiosk mode."""
    return OFFLINE_FAQS
