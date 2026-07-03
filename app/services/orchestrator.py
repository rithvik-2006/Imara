import time
import logging
from typing import Dict, Any
from app.services.ai_service import AIService
from app.services.translation_service import TranslationService
from app.services.tts_service import TTSService

logger = logging.getLogger(__name__)

class AIOrchestrationService:
    """
    Orchestrates the complete pipeline: Base generation -> Translation -> TTS -> Payload building.
    """
    def __init__(self):
        self.ai_service = AIService()
        self.translator = TranslationService()
        self.tts = TTSService()

    def process_community_alert(self, community, hazard) -> Dict[str, Any]:
        """
        Orchestrates an alert generation for a specific community and hazard.
        """
        logger.info(f"Starting orchestration for community: {community.name}")
        
        # 1. Base AI Generation (English)
        start_time = time.time()
        base_payload = self.ai_service.generate_base_advisory(
            hazard_type=hazard.hazard_type,
            severity=hazard.severity,
            community_name=community.name
        )
        ai_latency = time.time() - start_time
        logger.info(f"AI Generation latency: {ai_latency:.2f}s")
        
        if not base_payload:
            logger.error("Failed to generate base payload. Using fallback.")
            return self._build_fallback_payload(community, hazard)

        # 2. Translation
        start_time = time.time()
        target_lang = community.preferred_language
        
        sms_alert = self.translator.translate(base_payload.get('sms_alert', ''), target_lang)
        voice_script = self.translator.translate(base_payload.get('voice_script', ''), target_lang)
        action = self.translator.translate(base_payload.get('recommended_action', ''), target_lang)
        
        trans_latency = time.time() - start_time
        logger.info(f"Translation latency: {trans_latency:.2f}s")

        # 3. TTS Generation
        start_time = time.time()
        audio_url = self.tts.generate_audio(voice_script, target_lang)
        tts_latency = time.time() - start_time
        logger.info(f"TTS latency: {tts_latency:.2f}s, File: {audio_url}")

        # 4. Build Final Payload
        return {
            "community_name": community.name,
            "hazard_type": hazard.hazard_type,
            "severity": hazard.severity,
            "language": target_lang,
            "sms_alert": sms_alert,
            "voice_script": voice_script,
            "recommended_action": action,
            "urgency": base_payload.get("urgency", "UNKNOWN"),
            "audio_url": audio_url,
            "delivery_status": "pending"
        }

    def _build_fallback_payload(self, community, hazard) -> Dict[str, Any]:
        return {
            "community_name": community.name,
            "hazard_type": hazard.hazard_type,
            "severity": hazard.severity,
            "language": community.preferred_language,
            "sms_alert": f"URGENT: A {hazard.severity} {hazard.hazard_type} is approaching. Please take immediate precautions.",
            "voice_script": "This is an automated alert. A hazard is approaching your community. Please take necessary precautions and stay safe.",
            "recommended_action": "Stay alert and await further instructions.",
            "urgency": "HIGH",
            "audio_url": None,
            "delivery_status": "failed_generation"
        }
