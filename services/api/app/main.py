from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from app.services.llm_service import LLMService
from app.services.safety_engine import SafetyEngine
from app.services.audio_service import AudioService

app = FastAPI(
    title="LagDoki-AI API",
    description="Multilingual Voice and Text Triage Engine (English, Yoruba, and Nigerian Pidgin).",
    version="0.3.0"
)

llm_service = LLMService()
safety_engine = SafetyEngine()
audio_service = AudioService()

class TriageRequest(BaseModel):
    text_input: str
    language: str = "English"

@app.get("/")
def read_root():
    return {"status": "LagDoki-AI Service Active", "version": "0.3.0"}

# --- TEXT TRIAGE ENDPOINT ---
@app.post("/api/triage")
def triage_patient(request: TriageRequest):
    if not request.text_input.strip():
        raise HTTPException(status_code=400, detail="Symptom text cannot be empty.")
    
    # 1. Deterministic Red-Flag Check
    safety_result = safety_engine.check_red_flags(request.text_input)
    if safety_result["is_emergency"]:
        return {
            "status": "emergency_alert",
            "ai_agent": "LagDoki-AI",
            "triage_code": safety_result["triage_code"],
            "language": request.language,
            "assessment": safety_result["message"]
        }

    # 2. Enrich text with local idiom translation
    enriched_input = safety_engine.map_local_idioms(request.text_input, request.language)

    # 3. LLM Reasoning via Groq
    try:
        assessment = llm_service.analyze_symptoms(
            patient_input=enriched_input,
            language=request.language
        )
        return {
            "status": "success",
            "ai_agent": "LagDoki-AI",
            "triage_code": "NON_EMERGENCY",
            "language": request.language,
            "assessment": assessment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- VOICE TRIAGE ENDPOINT ---
@app.post("/api/triage/voice")
async def triage_voice_patient(
    file: UploadFile = File(...),
    language: Optional[str] = Form("Nigerian Pidgin")
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No audio file uploaded.")

    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # 1. Speech-to-Text Transcription
        transcription_result = audio_service.transcribe_audio(file_bytes, file.filename)
        spoken_text = transcription_result["transcript"]

        if not spoken_text.strip():
            raise HTTPException(status_code=400, detail="Could not transcribe clear speech from audio.")

        # 2. Deterministic Red-Flag Check on transcribed speech
        safety_result = safety_engine.check_red_flags(spoken_text)
        if safety_result["is_emergency"]:
            return {
                "status": "emergency_alert",
                "ai_agent": "LagDoki-AI",
                "triage_code": safety_result["triage_code"],
                "transcribed_text": spoken_text,
                "detected_language": transcription_result["detected_language"],
                "assessment": safety_result["message"]
            }

        # 3. Enrich text with local idioms
        enriched_input = safety_engine.map_local_idioms(spoken_text, language)

        # 4. LLM Reasoning via Groq
        assessment = llm_service.analyze_symptoms(
            patient_input=enriched_input,
            language=language
        )

        return {
            "status": "success",
            "ai_agent": "LagDoki-AI",
            "triage_code": "NON_EMERGENCY",
            "transcribed_text": spoken_text,
            "detected_language": transcription_result["detected_language"],
            "assessment": assessment
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")