import logging
from typing import Optional
from app.services.ai_service import get_openai_client

logger = logging.getLogger(__name__)

class TranslationService:
    """
    Handles translating text into various supported languages.
    Currently utilizes NVIDIA NIM LLMs for high quality contextual translation.
    """
    def __init__(self):
        self.client = get_openai_client()
        self.model = "meta/llama-3.1-70b-instruct"

    def translate(self, text: str, target_language: str) -> Optional[str]:
        """
        Translates the given text into the target language.
        Returns the original text if target is English or if translation fails.
        """
        if not text:
            return text
            
        if target_language.lower() == "english":
            return text
            
        system_prompt = (
            "You are an expert, highly accurate professional translator specializing in East African languages. "
            "You must translate the given text exactly, preserving tone, urgency, and formatting. "
            "Return ONLY the translated text. Do not add any conversational text, explanations, or quotes."
        )
        
        user_prompt = f"Translate the following text into {target_language}:\n\n{text}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Translation failed for language {target_language}: {e}")
            return text # Fallback to original text on failure
