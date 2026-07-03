import os
import uuid
import logging
from typing import Optional
from gtts import gTTS

logger = logging.getLogger(__name__)

class TTSService:
    """
    Handles converting text scripts into MP3 audio files using gTTS.
    """
    def __init__(self, audio_dir: str = "app/static/audio"):
        self.audio_dir = audio_dir
        os.makedirs(self.audio_dir, exist_ok=True)

    def generate_audio(self, text: str, language: str) -> Optional[str]:
        """
        Converts text to an MP3 file.
        Returns the relative URL path to the generated file.
        """
        if not text:
            return None
            
        try:
            # Map standard language names to ISO codes supported by gTTS
            lang_code = "en"
            lang_lower = language.lower()
            if "swahili" in lang_lower:
                lang_code = "sw"
            elif "somali" in lang_lower:
                # gTTS does not fully support Somali. Fallback to English or Swahili depending on region.
                # For Phase 2, we fallback to English for TTS if language isn't fully supported.
                lang_code = "en" 
            
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            filename = f"voice_{uuid.uuid4().hex[:12]}.mp3"
            filepath = os.path.join(self.audio_dir, filename)
            
            tts.save(filepath)
            
            return f"/static/audio/{filename}"
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None
