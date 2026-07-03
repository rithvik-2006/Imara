import os
import logging
from flask import Blueprint, request, make_response
from app.extensions import db
from app.models.community import Community
from app.models.hazard_event import HazardEvent
from app.models.delivery import DeliveryLog

logger = logging.getLogger(__name__)
communication_bp = Blueprint('communication', __name__, url_prefix='/api/v1')

@communication_bp.route('/ussd', methods=['POST'])
def ussd_callback():
    """
    USSD Callback webhook for Africa's Talking.
    """
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    
    phone_number = request.values.get("phoneNumber")
    if phone_number:
        # Fix 1: If URL-encoding turned the '+' into a space (" 254...")
        phone_number = phone_number.replace(" ", "+")
        
        # Fix 2: If the '+' was stripped completely ("254...")
        if not phone_number.startswith("+"):
            phone_number = f"+{phone_number}"
        
    text = request.values.get("text", "")
    
    # Split text string to get the latest input. e.g., '1*2*1'
    text_parts = text.split('*')
    latest_input = text_parts[-1] if text else ''

    # Fetch community
    community = db.session.query(Community).filter_by(phone_number=phone_number).first()
    
    if not community:
        response = "END Welcome to AgriPulse. Your number is not registered as a community leader."
        return _ussd_response(response)

    # Check for active hazards
    active_hazard = db.session.query(HazardEvent).join(
        Community, Community.location.ST_Intersects(HazardEvent.geom)
    ).filter(
        Community.id == community.id,
        HazardEvent.is_active == True
    ).first()

    if not active_hazard:
        if latest_input == "":
            response = f"CON Welcome {community.name}. There are currently no active hazards in your area.\n"
            response += "1. Main Menu\n2. Exit"
            return _ussd_response(response)
        else:
            response = "END Thank you for using AgriPulse."
            return _ussd_response(response)

    # USSD Flow for Active Hazard
    if latest_input == "":
        # Initial menu
        response = f"CON ALERT: {active_hazard.severity} {active_hazard.hazard_type} detected.\n"
        response += "1. Listen to advice\n"
        response += "2. Confirm safety"
        return _ussd_response(response)
    
    elif latest_input == "1":
        # Usually we would fetch the generated recommended action from a cache or db.
        # For USSD, keep it short.
        response = f"END Advice: Please stay alert and follow local guidelines regarding the {active_hazard.hazard_type}."
        return _ussd_response(response)
        
    elif latest_input == "2":
        # Mark community as safe (stub)
        response = "END Thank you. We have recorded your community as safe."
        return _ussd_response(response)
        
    else:
        response = "END Invalid option. Please try again."
        return _ussd_response(response)

def _ussd_response(response_text: str):
    """Formats a response for Africa's Talking USSD"""
    res = make_response(response_text, 200)
    res.headers['Content-Type'] = 'text/plain'
    return res


@communication_bp.route('/voice/callback', methods=['POST'])
def voice_callback():
    """
    Voice Callback webhook for Africa's Talking.
    When a call connects, AT hits this URL. We respond with XML to play the MP3.
    """
    # AT sends direction, callerNumber, destinationNumber, isActive
    is_active = request.values.get("isActive", "0")
    
    if is_active == "1":
        # In a real system, we'd look up the generated audio_url for this number.
        # Here we demonstrate the XML structure assuming a static or last-generated file for simplicity.
        # The user requested valid Africa's Talking Voice XML.
        base_url = os.getenv("PUBLIC_BASE_URL", "https://example.com")
        
        # Typically we'd fetch the specific community's audio. For MVP, we provide a generic or dummy link.
        audio_url = f"{base_url}/static/audio/alert_dummy.mp3"
        
        response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Play url="{audio_url}"/>
        </Response>"""
        
        res = make_response(response_xml, 200)
        res.headers['Content-Type'] = 'application/xml'
        return res
    else:
        # Call ended
        return make_response("Success", 200)


@communication_bp.route('/sms/callback', methods=['POST'])
def sms_callback():
    """
    SMS delivery receipt (DLR) webhook.
    Updates the DeliveryLog status.
    """
    # AT sends status, id, networkCode
    message_id = request.values.get("id")
    status = request.values.get("status")
    
    if message_id and status:
        delivery_log = db.session.query(DeliveryLog).filter_by(message_id=message_id).first()
        if delivery_log:
            delivery_log.status = status
            db.session.commit()
            logger.info(f"Updated DeliveryLog {message_id} to {status}")
            
    return make_response("Success", 200)
