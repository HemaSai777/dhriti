import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseModel):
    PROJECT_NAME: str = "SAHAYA — Cooperative Governance & Legal Assistance"
    API_PREFIX: str = "/api"
    
    # Verification Gate Thresholds
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))
    SENSITIVE_CONFIDENCE_THRESHOLD: float = float(os.getenv("SENSITIVE_CONFIDENCE_THRESHOLD", "0.85"))
    
    # Model & Provider Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")  # gemini, openai, ollama, mock
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-3.6-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/sahaya.db")
    
    # Storage Paths
    DOCUMENTS_DIR: Path = BASE_DIR / "data" / "documents"
    INDEX_DIR: Path = BASE_DIR / "data" / "index"
    
    # Retrieval Tuning
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    BM25_WEIGHT: float = 0.5
    DENSE_WEIGHT: float = 0.5

settings = Settings()
