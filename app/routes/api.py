from flask import Blueprint, request, jsonify
from shapely.geometry import shape
from app.extensions import db
from app.models.community import Community
from app.models.hazard_event import HazardEvent
from app.services.orchestrator import AIOrchestrationService
from app.services.africastalking_service import ATService
from app.models.delivery import DeliveryLog

api_bp = Blueprint('api', __name__)

@api_bp.route('/community', methods=['POST'])
def create_community():
    """
    Creates a new community.
    Expected JSON payload:
    {
        "name": "Eldoret Farmers Coop",
        "lat": 0.5143,
        "lng": 35.2698,
        "language": "Swahili",
        "phone": "+254712345678"
    }
    """
    data = request.get_json()
    
    if not all(k in data for k in ('name', 'lat', 'lng', 'language', 'phone')):
        return jsonify({"error": "Missing required fields"}), 400
        
    # Construct WKT (Well-Known Text) for the spatial POINT
    point_wkt = f"SRID=4326;POINT({data['lng']} {data['lat']})"
    
    community = Community(
        name=data['name'],
        location=point_wkt,
        preferred_language=data['language'],
        phone_number=data['phone']
    )
    
    db.session.add(community)
    db.session.commit()
    
    return jsonify({"message": "Community created successfully", "id": str(community.id)}), 201


@api_bp.route('/ingest/hazard', methods=['POST'])
def ingest_hazard():
    """
    Ingests a hazard event from an external API (like ICPAC GeoJSON).
    Expected JSON payload:
    {
        "hazard_type": "Flood",
        "severity": "High",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[35.0, 0.0], [35.5, 0.0], [35.5, 0.5], [35.0, 0.5], [35.0, 0.0]]]
        }
    }
    """
    data = request.get_json()
    
    if not all(k in data for k in ('hazard_type', 'severity', 'geometry')):
        return jsonify({"error": "Missing required fields"}), 400
        
    try:
        # Convert raw GeoJSON to a Shapely Geometry, then parse to WKT for insertion
        geom_shape = shape(data['geometry'])
        polygon_wkt = f"SRID=4326;{geom_shape.wkt}"
    except Exception as e:
        return jsonify({"error": f"Invalid geometry data: {str(e)}"}), 400
        
    hazard = HazardEvent(
        hazard_type=data['hazard_type'],
        severity=data['severity'],
        geom=polygon_wkt,
        is_active=True
    )
    
    db.session.add(hazard)
    db.session.commit()
    
    return jsonify({"message": "Hazard event ingested successfully", "id": str(hazard.id)}), 201


@api_bp.route('/check-alerts', methods=['GET'])
def check_alerts():
    """
    Core Spatial Route: Finds all communities intersecting with active hazard 
    events and generates custom AI SMS alerts for them using NVIDIA NIM.
    """
    # Optimized spatial join using PostGIS ST_Intersects:
    # This filters both the relationship and the active status completely in the database tier
    affected_records = db.session.query(
        Community, HazardEvent
    ).join(
        HazardEvent, 
        Community.location.ST_Intersects(HazardEvent.geom)
    ).filter(
        HazardEvent.is_active == True
    ).all()
    
    alerts = []
    orchestrator = AIOrchestrationService()
    at_service = ATService()
    
    for community, hazard in affected_records:
        payload = orchestrator.process_community_alert(community, hazard)
        
        # Log delivery and dispatch AT
        sms_id = None
        voice_id = None
        
        if payload.get("sms_alert"):
            sms_id = at_service.send_sms(community.phone_number, payload["sms_alert"])
            db.session.add(DeliveryLog(
                community_id=community.id,
                channel='SMS',
                status='Sent' if sms_id else 'Failed',
                message_id=sms_id
            ))
            
        if payload.get("audio_url"):
            voice_id = at_service.initiate_voice_call(community.phone_number)
            db.session.add(DeliveryLog(
                community_id=community.id,
                channel='VOICE',
                status='Initiated' if voice_id else 'Failed',
                message_id=voice_id
            ))
            
        db.session.commit()
        
        alerts.append(payload)
        
    return jsonify({
        "total_alerts": len(alerts),
        "alerts": alerts
    }), 200

@api_bp.route('/seed', methods=['POST', 'GET'])
def seed_data():
    """
    Populates the database with dummy data for the demo.
    """
    if db.session.query(Community).count() == 0:
        communities = [
            Community(name="Eldoret Farmers Coop", location="SRID=4326;POINT(35.2698 0.5143)", preferred_language="Swahili", phone_number="+254712345678"),
            Community(name="Nairobi Agricultural Trust", location="SRID=4326;POINT(36.8219 -1.2921)", preferred_language="English", phone_number="+254712345679"),
            Community(name="Kisumu Fishers and Farmers", location="SRID=4326;POINT(34.7617 -0.0917)", preferred_language="Swahili", phone_number="+254712345680")
        ]
        db.session.add_all(communities)
        
        polygon_wkt = "SRID=4326;POLYGON((34.0 -1.0, 36.0 -1.0, 36.0 1.0, 34.0 1.0, 34.0 -1.0))"
        hazard = HazardEvent(
            hazard_type="Heavy Rainfall and Flood",
            severity="High",
            geom=polygon_wkt,
            is_active=True
        )
        db.session.add(hazard)
        db.session.commit()
        return jsonify({"message": "Dummy data seeded successfully"}), 201
    
    return jsonify({"message": "Database already contains data"}), 200
