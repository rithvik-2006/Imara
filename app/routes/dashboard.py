import json
from flask import Blueprint, jsonify
from sqlalchemy import func
from app.extensions import db
from app.models.community import Community
from app.models.hazard_event import HazardEvent
from app.models.delivery import DeliveryLog
from app.models.alert_job import AlertJob

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Returns high-level metrics for the Admin Dashboard.
    """
    total_communities = db.session.query(Community).count()
    active_hazards = db.session.query(HazardEvent).filter_by(is_active=True).count()
    
    total_deliveries = db.session.query(DeliveryLog).count()
    successful_deliveries = db.session.query(DeliveryLog).filter(DeliveryLog.status.in_(['Sent', 'Delivered', 'Success'])).count()
    
    success_rate = 0
    if total_deliveries > 0:
        success_rate = round((successful_deliveries / total_deliveries) * 100, 1)
        
    return jsonify({
        "total_communities": total_communities,
        "active_hazards": active_hazards,
        "total_alerts": total_deliveries,
        "delivery_success_rate": success_rate
    }), 200


@dashboard_bp.route('/map', methods=['GET'])
def get_map_data():
    """
    Returns a GeoJSON FeatureCollection of all active hazards and communities.
    The frontend Next.js application will use this to plot markers and polygons on the Leaflet map.
    """
    # Get active hazards as GeoJSON
    hazards = db.session.query(
        HazardEvent.id,
        HazardEvent.hazard_type,
        HazardEvent.severity,
        func.ST_AsGeoJSON(HazardEvent.geom).label('geometry')
    ).filter_by(is_active=True).all()
    
    hazard_features = []
    for h in hazards:
        geom = json.loads(h.geometry)
        hazard_features.append({
            "type": "Feature",
            "properties": {
                "id": str(h.id),
                "type": "hazard",
                "hazard_type": h.hazard_type,
                "severity": h.severity
            },
            "geometry": geom
        })
        
    # Get all communities as GeoJSON
    communities = db.session.query(
        Community.id,
        Community.name,
        func.ST_AsGeoJSON(Community.location).label('geometry')
    ).all()
    
    community_features = []
    for c in communities:
        # Determine status by checking if it intersects an active hazard
        is_at_risk = db.session.query(HazardEvent).join(
            Community, Community.location.ST_Intersects(HazardEvent.geom)
        ).filter(
            Community.id == c.id,
            HazardEvent.is_active == True
        ).first() is not None
        
        status = 'At Risk' if is_at_risk else 'Safe'
        
        # Check if an alert was delivered recently
        has_delivery = db.session.query(DeliveryLog).filter_by(community_id=c.id).first() is not None
        if is_at_risk and has_delivery:
            status = 'Alerted'
            
        geom = json.loads(c.geometry)
        community_features.append({
            "type": "Feature",
            "properties": {
                "id": str(c.id),
                "type": "community",
                "name": c.name,
                "status": status
            },
            "geometry": geom
        })
        
    return jsonify({
        "type": "FeatureCollection",
        "features": hazard_features + community_features
    }), 200

@dashboard_bp.route('/jobs', methods=['GET'])
def get_jobs_stats():
    """
    Returns statistics about AlertJobs (Queued, Running, Completed, Failed).
    """
    queued = db.session.query(AlertJob).filter_by(status='Queued').count()
    running = db.session.query(AlertJob).filter_by(status='Processing').count()
    completed = db.session.query(AlertJob).filter_by(status='Completed').count()
    failed = db.session.query(AlertJob).filter_by(status='Failed').count()
    
    total = queued + running + completed + failed
    progress = 0
    if total > 0:
        progress = round(((completed + failed) / total) * 100, 1)
        
    avg_processing = db.session.query(func.avg(AlertJob.processing_time)).filter_by(status='Completed').scalar() or 0
    avg_ai = db.session.query(func.avg(AlertJob.ai_latency)).filter_by(status='Completed').scalar() or 0
    avg_trans = db.session.query(func.avg(AlertJob.translation_latency)).filter_by(status='Completed').scalar() or 0
    avg_tts = db.session.query(func.avg(AlertJob.tts_latency)).filter_by(status='Completed').scalar() or 0
    avg_sms = db.session.query(func.avg(AlertJob.sms_latency)).filter_by(status='Completed').scalar() or 0
    avg_voice = db.session.query(func.avg(AlertJob.voice_latency)).filter_by(status='Completed').scalar() or 0
    
    return jsonify({
        "queued": queued,
        "running": running,
        "completed": completed,
        "failed": failed,
        "progress_percentage": progress,
        "avg_processing_time": round(avg_processing, 2),
        "avg_ai_latency": round(avg_ai, 2),
        "avg_translation_latency": round(avg_trans, 2),
        "avg_tts_latency": round(avg_tts, 2),
        "avg_sms_latency": round(avg_sms, 2),
        "avg_voice_latency": round(avg_voice, 2),
        "queue_size": queued
    }), 200
