import os
import logging
from typing import Optional
import africastalking

logger = logging.getLogger(__name__)

class ATService:
    """
    Service to handle interactions with the Africa's Talking API.
    """
    def __init__(self):
        self.username = os.getenv("AT_USERNAME", "sandbox")
        self.api_key = os.getenv("AT_API_KEY")
        self.virtual_number = os.getenv("AT_VIRTUAL_NUMBER")
        
        if self.username and self.api_key:
            africastalking.initialize(self.username, self.api_key)
            self.sms = africastalking.SMS
            self.voice = africastalking.Voice
        else:
            logger.warning("Africa's Talking credentials not found. ATService will not function.")
            self.sms = None
            self.voice = None

    def send_sms(self, phone_number: str, message: str) -> Optional[str]:
        """
        Sends an SMS to the specified phone number.
        Returns the Africa's Talking message ID if successful.
        """
        if not self.sms:
            logger.error("SMS service not initialized.")
            return None
            
        try:
            # send() returns a response dict
            response = self.sms.send(message, [phone_number])
            # Parse response for messageId
            recipients = response.get('SMSMessageData', {}).get('Recipients', [])
            if recipients:
                message_id = recipients[0].get('messageId')
                logger.info(f"SMS sent successfully. MessageId: {message_id}")
                return message_id
            return None
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            return None

    def initiate_voice_call(self, phone_number: str) -> Optional[str]:
        """
        Initiates an outbound voice call to the specified phone number.
        The actual MP3 playing will be handled by the Voice webhook callback.
        """
        if not self.voice:
            logger.error("Voice service not initialized.")
            return None
            
        if not self.virtual_number:
            logger.error("AT_VIRTUAL_NUMBER not set.")
            return None

        try:
            # Make a call from our virtual number to the user's phone
            response = self.voice.call(self.virtual_number, [phone_number])
            
            # The response contains session IDs and statuses
            entries = response.get('entries', [])
            if entries:
                session_id = entries[0].get('sessionId')
                logger.info(f"Voice call initiated. SessionId: {session_id}")
                return session_id
            return None
        except Exception as e:
            logger.error(f"Failed to initiate voice call to {phone_number}: {e}")
            return None
