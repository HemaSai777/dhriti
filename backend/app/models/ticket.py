import datetime
from sqlalchemy import Column, String, Float, DateTime, Text
from app.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, default="citizen-demo", index=True)
    query = Column(Text, nullable=False)
    language = Column(String, default="en")
    intent = Column(String, default="GENERAL_INFO")
    confidence = Column(Float, default=0.0)
    reason = Column(String, nullable=True)
    candidate_chunks = Column(Text, nullable=True)  # JSON-encoded array of retrieved evidence
    status = Column(String, default="PENDING", index=True)  # PENDING, UNDER_REVIEW, RESOLVED, ESCALATED
    officer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
