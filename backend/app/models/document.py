import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from app.database import Base

class DocumentMetadata(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, default="txt")
    pages = Column(Integer, default=1)
    chunk_count = Column(Integer, default=0)
    source_department = Column(String, default="Cooperative Governance")
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
