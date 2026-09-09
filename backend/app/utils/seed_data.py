import json
import datetime
from app.database import SessionLocal, Base, engine
from app.models.ticket import Ticket
from app.models.document import DocumentMetadata
from app.services.ingestion import ingest_all_documents
from app.services.retrieval import retriever
from app.config import settings

def init_db():
    print("[Seed] Creating database tables...")
    Base.metadata.create_all(bind=engine)

def seed_demo_data():
    db = SessionLocal()
    init_db()

    # 1. Ingest documents and build retrieval index
    print("[Seed] Ingesting documents...")
    chunks = ingest_all_documents()
    retriever.load_index()

    # 2. Seed Document Metadata if empty
    existing_docs = db.query(DocumentMetadata).count()
    if existing_docs == 0:
        docs_dir = settings.DOCUMENTS_DIR
        for f in docs_dir.glob("*.*"):
            if f.suffix.lower() in [".txt", ".pdf"]:
                # Count chunks for this doc
                doc_chunks = [c for c in chunks if c.get("source") == f.name]
                max_page = max([c.get("page", 1) for c in doc_chunks], default=1)
                
                doc_record = DocumentMetadata(
                    id=f.stem.upper().replace(" ", "_"),
                    title=f.stem.replace("_", " "),
                    filename=f.name,
                    file_type=f.suffix.replace(".", "").upper(),
                    pages=max_page,
                    chunk_count=len(doc_chunks),
                    source_department="Department of Agriculture & Cooperation, Govt of India",
                    uploaded_at=datetime.datetime.utcnow()
                )
                db.add(doc_record)
        db.commit()
        print("[Seed] Populated DocumentMetadata records.")

    # 3. Seed Demo Tickets if empty
    existing_tickets = db.query(Ticket).count()
    if existing_tickets == 0:
        print("[Seed] Populating realistic demo Grievance Tickets for Officer Portal...")
        sample_tickets = [
            Ticket(
                id="GRV-2026-00421",
                user_id="farmer-suresh-88",
                query="Can I get a loan waiver of 10 lakh rupees without land records under PMFBY?",
                language="en",
                intent="PMFBY_CLAIM",
                confidence=0.38,
                reason="Model identified no supporting evidence for unilateral 10 lakh waiver without land title in verified guidelines.",
                status="PENDING",
                officer_notes=None,
                candidate_chunks=json.dumps([
                    {"title": "PMFBY Operational Guidelines", "page": 1, "section": "Section 1", "score": 0.35, "excerpt": "The scheme covers all Food & Oilseeds crops and Annual Commercial crops for which yield data is available..."},
                    {"title": "Kisan Credit Scheme Norms", "page": 5, "section": "Chapter II", "score": 0.32, "excerpt": "No collateral security or mortgage required up to Rs. 1,60,000 crop loans."}
                ]),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
            ),
            Ticket(
                id="GRV-2026-00388",
                user_id="farmer-murugan-42",
                query="விதை மற்றும் உர மானிய ரசீது வழங்க கூட்டுறவு செயலாளர் மறுக்கிறார்",
                language="ta",
                intent="GRIEVANCE",
                confidence=0.52,
                reason="Grievance regarding refusal of receipt by PACS Secretary. Evidence requires field verification.",
                status="UNDER_REVIEW",
                officer_notes="Contacted PACS Nodal Officer at Thanjavur branch. Audit of fertilizer dispatch register scheduled for tomorrow.",
                candidate_chunks=json.dumps([
                    {"title": "PACS Grievance Redressal Protocol", "page": 7, "section": "Section 3", "score": 0.58, "excerpt": "Any member may register a grievance regarding irregularities in fertilizer/seed distribution or non-issuance of receipts."}
                ]),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            ),
            Ticket(
                id="GRV-2026-00105",
                user_id="farmer-ramesh-19",
                query="Severe inundation damaged 4 acres of paddy. Surveyor not arrived after 48 hours.",
                language="en",
                intent="PMFBY_CLAIM",
                confidence=0.49,
                reason="Time-sensitive claim escalation. Surveyor appointment exceeded mandated 48 hours.",
                status="RESOLVED",
                officer_notes="Coordinated with Agriculture Insurance Company (AIC) district lead. Surveyor deputed; joint loss report filed at 65% loss; on-account relief sanctioned.",
                candidate_chunks=json.dumps([
                    {"title": "PMFBY Operational Guidelines", "page": 42, "section": "Section 11: Claim Settlement", "score": 0.72, "excerpt": "An appointed loss assessor or surveyor must be deputed within 48 hours of intimation."}
                ]),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=3)
            ),
            Ticket(
                id="GRV-2026-00214",
                user_id="farmer-balwinder-55",
                query="सहकारी समिति चुनाव में बिना किसी कारण के मेरा मतदान अधिकार रद्द कर दिया गया है।",
                language="hi",
                intent="COOPERATIVE_BYLAW",
                confidence=0.61,
                reason="Dispute regarding disqualification of voting rights under Cooperative By-laws Rule 19.",
                status="ESCALATED",
                officer_notes="Forwarded formal case file to District Deputy Registrar for statutory hearing under Section 5.2 (Tier 2).",
                candidate_chunks=json.dumps([
                    {"title": "Model Cooperative Societies Bylaws", "page": 15, "section": "Chapter IV, Rule 19", "score": 0.65, "excerpt": "Every ordinary member shall have one vote. Disqualification applies only if member defaulted for continuous period exceeding 12 months."}
                ]),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
            )
        ]
        for t in sample_tickets:
            db.add(t)
        db.commit()
        print(f"[Seed] Successfully seeded {len(sample_tickets)} sample tickets.")

    db.close()
    print("[Seed] Seed data initialization complete!")

if __name__ == "__main__":
    seed_demo_data()
