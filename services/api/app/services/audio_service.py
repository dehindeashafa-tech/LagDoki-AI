import os
import tempfile
from faster_whisper import WhisperModel

class AudioService:
    def __init__(self):
        # Using "small" for significantly better Pidgin/Yoruba vocabulary support
        self.model_size = "small"
        self.model = WhisperModel(
            self.model_size, 
            device="cpu", 
            compute_type="int8"
        )
        
        # Initial prompt primes Whisper to expect Pidgin and Yoruba health phrases
        self.initial_prompt = (
            "Patient speaking in Nigerian Pidgin, Yoruba, or English. "
            "Keywords: body dey hot scatter, my head dey split, belle dey do gbi-gbi, "
            "pikin body dey shake, water dey run, eye dey turn me, fever, vomit, headache, "
            "mọ́mọ́ ń ru wọ́le, ori mi wọ́ le ki, àyà ń gba."
        )

    def transcribe_audio(self, file_bytes: bytes, filename: str) -> dict:
        ext = os.path.splitext(filename)[1] or ".wav"

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
            temp_audio.write(file_bytes)
            temp_audio_path = temp_audio.name

        try:
            segments, info = self.model.transcribe(
                temp_audio_path, 
                beam_size=5,
                initial_prompt=self.initial_prompt, # <--- Primes vocabulary
                vad_filter=True # <--- Filters out silence/background noise
            )

            transcript = " ".join([segment.text.strip() for segment in segments])

            return {
                "detected_language": info.language,
                "language_probability": round(info.language_probability, 2),
                "transcript": transcript
            }

        finally:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)