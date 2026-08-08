import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form
from groq import Groq

router = APIRouter()

groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

RED_FLAGS = [
    "chest", "pain", "breathe", "breathing", "die", 
    "unconscious", "bleeding", "dying", "faint", "heart"
]

def format_whatsapp_triage(user_text: str) -> str:
    text_lower = user_text.lower()
    is_emergency = any(flag in text_lower for flag in RED_FLAGS)
    
    if is_emergency:
        return (
            "🚨 *EMERGENCY RED FLAG DETECTED* 🚨\n\n"
            f"*Your Input:* \"{user_text}\"\n\n"
            "⚠️ *Assessment:* Severe clinical red flags detected! "
            "Your symptoms indicate potential acute cardiovascular or respiratory distress.\n\n"
            "🏥 *RECOMMENDED ACTION:* Please proceed to the nearest emergency center or hospital immediately."
        )
    
    return (
        "🟢 *LagDoki-AI Triage Result*\n\n"
        f"*Transcribed Input:* \"{user_text}\"\n\n"
        "✅ *Assessment:* Non-emergency symptoms detected.\n\n"
        "💡 *RECOMMENDED ACTION:* Get adequate rest, hydrate well, and monitor your symptoms. "
        "If pain worsens or you have trouble breathing, visit a clinic immediately."
    )

@router.post("/whatsapp/webhook")
@router.post("/api/whatsapp/webhook")
async def whatsapp_webhook(
    Body: str = Form(""),
    From: str = Form(""),
    file: UploadFile = File(None)
):
    transcribed_text = ""

    if file:
        temp_audio_path = None
        try:
            content = await file.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
                temp_audio.write(content)
                temp_audio_path = temp_audio.name

            if groq_client:
                with open(temp_audio_path, "rb") as audio_file:
                    try:
                        transcription = groq_client.audio.transcriptions.create(
                            file=("voice.ogg", audio_file),
                            model="whisper-large-v3",
                            prompt="Patient speaking in Nigerian Pidgin or English describing medical symptoms",
                            response_format="json"
                        )
                        transcribed_text = transcription.text.strip()
                    except Exception as groq_err:
                        print(f"Groq API Error: {str(groq_err)}")
                        return {"reply": f"⚠️ Groq Transcription Failed: {str(groq_err)}"}
            else:
                return {"reply": "⚠️ Error: GROQ_API_KEY is not set in backend environment."}

        except Exception as e:
            print(f"File Exception: {str(e)}")
            return {"reply": f"⚠️ Could not process voice file: {str(e)}"}
        finally:
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

    elif Body.strip():
        transcribed_text = Body.strip()

    if not transcribed_text:
        return {"reply": "Please send a text message or voice note describing your symptoms."}

    reply_text = format_whatsapp_triage(transcribed_text)
    return {"reply": reply_text}
    