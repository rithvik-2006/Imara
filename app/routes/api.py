from flask import Blueprint, request, jsonify
from shapely.geometry import shape
from app.extensions import db
from app.models.community import Community
from app.models.hazard_event import HazardEvent
from app.models.delivery import DeliveryLog
from app.models.alert_job import AlertJob
from app.tasks.alert_tasks import process_alert_task

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
    events and creates AlertJobs.
    """
    affected_records = db.session.query(
        Community, HazardEvent
    ).join(
        HazardEvent, 
        Community.location.ST_Intersects(HazardEvent.geom)
    ).filter(
        HazardEvent.is_active == True
    ).all()
    
    jobs_created = 0
    
    for community, hazard in affected_records:
        job = AlertJob(
            community_id=community.id,
            hazard_id=hazard.id,
            status='Queued'
        )
        db.session.add(job)
        db.session.flush()
        
        process_alert_task.delay(str(job.id))
        jobs_created += 1
        
    db.session.commit()
        
    return jsonify({
        "status": "Processing Started",
        "jobs_created": jobs_created
    }), 200

@api_bp.route('/alerts/process', methods=['POST'])
def process_alerts():
    """
    Alias for check-alerts trigger.
    """
    return check_alerts()

@api_bp.route('/alerts/jobs', methods=['GET'])
def get_alert_jobs():
    """
    Returns all alert jobs.
    """
    jobs = AlertJob.query.order_by(AlertJob.created_at.desc()).all()
    return jsonify([{
        "id": str(job.id),
        "status": job.status,
        "community_id": str(job.community_id),
        "hazard_id": str(job.hazard_id),
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at
    } for job in jobs]), 200

@api_bp.route('/alerts/jobs/<job_id>', methods=['GET'])
def get_alert_job(job_id):
    """
    Returns a specific alert job.
    """
    job = AlertJob.query.get_or_404(job_id)
    return jsonify({
        "id": str(job.id),
        "status": job.status,
        "community_id": str(job.community_id),
        "hazard_id": str(job.hazard_id),
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "processing_time": job.processing_time,
        "error_message": job.error_message
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
