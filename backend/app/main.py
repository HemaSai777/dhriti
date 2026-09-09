from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.utils.seed_data import init_db, seed_demo_data
from app.services.retrieval import retriever

from app.routes.chat import router as chat_router
from app.routes.tickets import router as tickets_router
from app.routes.documents import router as documents_router
from app.routes.stats import router as stats_router
from app.routes.voice import router as voice_router
from app.routes.faq import router as faq_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure DB exists and seed data is populated
    print(f"[{settings.PROJECT_NAME}] Starting up...")
    seed_demo_data()
    yield
    print(f"[{settings.PROJECT_NAME}] Shutting down...")

app = FastAPI(
    title="SAHAYA API",
    description="Multilingual Cooperative Governance & Legal Assistance API with Citation-Gated RAG",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat_router, prefix=settings.API_PREFIX)
app.include_router(tickets_router, prefix=settings.API_PREFIX)
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(stats_router, prefix=settings.API_PREFIX)
app.include_router(voice_router, prefix=settings.API_PREFIX)
app.include_router(faq_router, prefix=settings.API_PREFIX)

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "SAHAYA Backend Gateway",
        "indexed_chunks": len(retriever.chunks),
        "safety_threshold": settings.CONFIDENCE_THRESHOLD,
        "sensitive_threshold": settings.SENSITIVE_CONFIDENCE_THRESHOLD,
        "provider": settings.LLM_PROVIDER
    }

# Check for production frontend build (for Render or unified full-stack hosting)
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import HTTPException

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API route not found")
        target = FRONTEND_DIST / full_path
        if target.is_file():
            return FileResponse(target)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "service": "SAHAYA Backend Gateway",
            "status": "ONLINE",
            "health_check": "/api/health",
            "docs": "/docs"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
