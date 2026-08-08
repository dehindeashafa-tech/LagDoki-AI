import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from groq import Groq

router = APIRouter()

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

# Pydantic schema for text symptom input
class TriageRequest(BaseModel):
    text_input: str
    language: Optional[str] = "Nigerian Pidgin"

RED_FLAGS = [
    "chest", "pain", "breathe", "breathing", "die", 
    "unconscious", "bleeding", "dying", "faint", "heart"
]

def evaluate_symptoms(user_text: str, language: str):
    text_lower = user_text.lower()
    is_emergency = any(flag in text_lower for flag in RED_FLAGS)
    
    if is_emergency:
        return {
            "status": "emergency_alert",
            "assessment": (
                "CRITICAL WARNING: Severe clinical red flags detected in symptom description!\n"
                "Symptoms indicate potential acute cardiovascular or respiratory distress.\n\n"
                "RECOMMENDED ACTION: Please proceed to the nearest emergency center immediately."
            ),
            "transcribed_text": user_text,
            "detected_language": language
        }
    
    return {
        "status": "non_emergency",
        "assessment": (
            "Non-emergency assessment complete.\n\n"
            "RECOMMENDED ACTION: Get adequate rest, hydrate well, and monitor your symptoms."
        ),
        "transcribed_text": user_text,
        "detected_language": language
    }


# -------------------------------------------------------------------
# 1. Text Triage Endpoint (Fixes "Not Found" for text input)
# Handles both /api/triage and /triage depending on your main.py router prefix
# -------------------------------------------------------------------
@router.post("/triage")
@router.post("/api/triage")
async def process_text_triage(data: TriageRequest):
    if not data.text_input.strip():
        raise HTTPException(status_code=400, detail="Please enter a symptom description.")
    
    return evaluate_symptoms(data.text_input, data.language or "Nigerian Pidgin")


# -------------------------------------------------------------------
# 2. Voice Triage Endpoint
# -------------------------------------------------------------------
@router.post("/triage/voice")
@router.post("/api/triage/voice")
async def process_voice_triage(
    file: UploadFile = File(...),
    language: str = Form("Nigerian Pidgin")
):
    if not groq_client:
        raise HTTPException(
            status_code=500, 
            detail="GROQ_API_KEY is missing from environment variables."
        )

    content = await file.read()
    if len(content) < 1000:
        return evaluate_symptoms("No audio detected. Please record again.", language)

    ext = os.path.splitext(file.filename or "speech.webm")[1] or ".webm"

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
        temp_audio.write(content)
        temp_audio_path = temp_audio.name

    try:
        with open(temp_audio_path, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=(f"input{ext}", audio_file),
                model="whisper-large-v3",
                response_format="json"
            )
            
            raw_text = transcription.text.strip() if hasattr(transcription, "text") else str(transcription).strip()
            
            if raw_text.lower() in ["you", "you.", "thank you.", "subtitles"]:
                transcribed_text = "No speech detected in audio."
            else:
                transcribed_text = raw_text

    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Groq Speech-to-Text connection failed: {str(e)}"
        )
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

    return evaluate_symptoms(transcribed_text, language)