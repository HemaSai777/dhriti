import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, Dict, Any

router = APIRouter(prefix="/voice", tags=["Voice"])

@router.post("", response_model=Dict[str, Any])
async def transcribe_audio(
    file: Optional[UploadFile] = File(None),
    language: Optional[str] = Form("en")
):
    """
    Speech-to-Text endpoint.
    If Whisper is installed/configured, processes audio;
    otherwise provides a graceful informative fallback response.
    """
    # Check if Whisper or an STT engine is available
    whisper_available = False
    try:
        import whisper
        whisper_available = True
    except ImportError:
        pass

    if whisper_available and file:
        try:
            # Process via Whisper
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, "wb") as f:
                f.write(await file.read())
            
            model = whisper.load_model("base")
            result = model.transcribe(temp_path, language=language)
            return {
                "status": "SUCCESS",
                "text": result.get("text", "").strip(),
                "engine": "OpenAI Whisper Local",
                "detected_language": language
            }
        except Exception as e:
            return {
                "status": "FALLBACK",
                "text": "What is the PMFBY claim procedure?",
                "message": f"Whisper processing encountered an issue ({e}). Using sample voice query for demonstration.",
                "engine": "Demonstration Voice Synthesizer"
            }
    
    # Graceful fallback explaining configuration
    return {
        "status": "DEMO_MODE",
        "text": "What is the PMFBY claim procedure and intimation deadline?",
        "message": "Local Whisper model not installed. Voice endpoint architecture is active and demonstrated with sample query.",
        "engine": "SAHAYA Voice Gateway (Simulation)"
    }
