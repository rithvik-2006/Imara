import os
import json
import logging
from typing import Dict, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

def get_openai_client() -> OpenAI:
    """
    Initializes and returns the OpenAI client configured for the NVIDIA NIM API.
    """
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=os.getenv("NVIDIA_API_KEY"),
        timeout=15.0 # Fail fast so Celery can retry or mark as Failed
    )

class AIService:
    """
    Handles generation of English base advisories in strict JSON format using NVIDIA NIM.
    """
    def __init__(self):
        self.client = get_openai_client()
        self.model = "meta/llama-3.1-70b-instruct"
        # We initialize it locally to avoid circular imports if any
        self.retrieval_service = None

    def _get_retrieval_service(self):
        if self.retrieval_service is None:
            from app.services.retrieval_service import RetrievalService
            self.retrieval_service = RetrievalService()
        return self.retrieval_service

    def generate_base_advisory(
        self, 
        hazard_type: str, 
        severity: str, 
        community_name: str,
        community_context: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, str]]:
        """
        Generates a structured advisory strictly in English.
        """
        system_prompt = (
            "You are an expert agronomist and disaster response coordinator for East Africa. "
            "You translate complex climate hazard data into actionable, localized advice for rural farmers."
        )
        
        
        context_str = ""
        if community_context:
            context_str = "\nCommunity Profile:\n"
            for key, value in community_context.items():
                if value:
                    context_str += f"- {key}: {value}\n"
                    
        # Try to retrieve RAG context
        rag_context = ""
        try:
            rag_query = f"{hazard_type} safety for {community_context.get('Primary Livelihood', 'farmers')}" if community_context else f"{hazard_type} safety"
            rag_docs = self._get_retrieval_service().retrieve_context(rag_query)
            if rag_docs:
                rag_context = f"\nRelevant Expert Guidelines:\n{rag_docs}\n"
        except Exception as e:
            logger.warning(f"Failed to retrieve RAG context: {e}")

        user_prompt = f"""
        A {severity} {hazard_type} has been detected affecting {community_name}. 
        Target Language: English.
        {context_str}
        {rag_context}
        Generate four outputs:
        1. 'sms_alert': A highly actionable SMS text strictly under 160 characters.
        2. 'voice_script': A slightly longer, empathetic, and clear script to be read out over a voice call (3-5 sentences). Suitable for the described demographic.
        3. 'recommended_action': Specific step-by-step action the community should take based on their profile.
        4. 'urgency': The level of urgency (e.g., HIGH, MEDIUM, LOW).

        Return ONLY a valid JSON object with the exact keys: "sms_alert", "voice_script", "recommended_action", "urgency". 
        Do not include markdown blocks, code formatting, or any other text. Output RAW JSON.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=800
            )
            
            raw_text = response.choices[0].message.content.strip()
            
            # Clean up potential markdown formatting
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:-3]
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:-3]
                
            return json.loads(raw_text.strip())
            
        except Exception as e:
            logger.error(f"Error generating base AI advisory: {e}")
            return None
