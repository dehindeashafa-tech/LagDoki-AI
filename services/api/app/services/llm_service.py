import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "gsk_your_actual_groq_api_key_here":
            raise ValueError("Please set your actual GROQ_API_KEY in the .env file!")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def analyze_symptoms(self, patient_input: str, language: str = "English"):
        """
        Processes symptoms and returns triage assessment via LagDoki-AI.
        """
        system_prompt = (
            "You are LagDoki-AI, an empathetic and culturally attuned public health triage assistant. "
            "Analyze the symptoms provided. Clearly identify the urgency level: "
            "(Red = Emergency, Yellow = See Doctor Soon, Green = Safe for Self Care). "
            "Respond simply, clearly, and supportively in standard text."
        )
        
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Language: {language}\nPatient Symptoms: {patient_input}"}
            ],
            model=self.model,
            temperature=0.2, # Low temperature prevents hallucinations
        )
        return response.choices[0].message.content