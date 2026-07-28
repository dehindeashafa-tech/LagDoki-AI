import json
import os
import re

class SafetyEngine:
    def __init__(self):
        # Critical life-threatening patterns (English, Pidgin, Yoruba)
        self.red_flag_patterns = [
            # Chest & Heart
            r"\b(chest pain|heart pain|aya ń gba|my heart dey pain)\b",
            # Severe Breathing
            r"\b(cannot breathe|shortness of breath|breath dey seized|mi ko le mi)\b",
            # Unconsciousness / Seizures
            r"\b(fainted|unconscious|convulsion|pikin body dey shake|gbonra)\b",
            # Severe Bleeding / Stroke
            r"\b(severe bleeding|coughing blood|eje|paralyzed|face drooping)\b",
            # Severe Pediatric Dehydration
            r"\b(no fit drink water|vomiting everything|pikin no dey wake)\b"
        ]

        # Path to local idiom dictionary
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dict_path = os.path.normpath(os.path.join(base_dir, "../../../../data/dictionary/idioms.json"))
        
        self.idioms = {}
        if os.path.exists(dict_path):
            with open(dict_path, "r", encoding="utf-8") as f:
                self.idioms = json.load(f)

    def check_red_flags(self, text_input: str) -> dict:
        """
        Scans input for immediate emergency red flags.
        Returns a dict indicating if an emergency was detected.
        """
        clean_text = text_input.lower()

        for pattern in self.red_flag_patterns:
            if re.search(pattern, clean_text):
                return {
                    "is_emergency": True,
                    "triage_code": "RED",
                    "action_required": "IMMEDIATE_EMERGENCY_REFERRAL",
                    "message": (
                        "🚨 RED FLAG EMERGENCY DETECTED 🚨\n"
                        "These symptoms require IMMEDIATE medical attention. "
                        "Please go to the nearest Primary Health Centre (PHC) or Emergency Room immediately. "
                        "Do not wait."
                    )
                }

        return {"is_emergency": False, "triage_code": "GREEN_OR_YELLOW"}

    def map_local_idioms(self, text_input: str, language: str) -> str:
        """
        Enriches patient input by translating local health idioms into clinical descriptors.
        """
        lang_key = language.lower()
        if lang_key in ["pidgin", "nigerian pidgin", "pcm"]:
            lang_dict = self.idioms.get("pidgin", {})
        elif lang_key in ["yoruba", "yorùbá", "yo"]:
            lang_dict = self.idioms.get("yoruba", {})
        else:
            return text_input

        enriched_text = text_input
        for idiom, clinical_meaning in lang_dict.items():
            if idiom in enriched_text.lower():
                enriched_text += f" (Clinical note: '{idiom}' usually indicates {clinical_meaning})"

        return enriched_text