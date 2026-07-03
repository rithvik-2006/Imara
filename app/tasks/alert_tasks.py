import time
import logging
from datetime import datetime, timezone
from celery import shared_task
from app.extensions import db
from app.models.community import Community
from app.models.hazard_event import HazardEvent
from app.models.alert_job import AlertJob
from app.models.delivery import DeliveryLog
from app.services.orchestrator import AIOrchestrationService
from app.services.africastalking_service import ATService

logger = logging.getLogger(__name__)

def update_job_status(job_id, status, **kwargs):
    job = db.session.get(AlertJob, job_id)
    if job:
        job.status = status
        for k, v in kwargs.items():
            setattr(job, k, v)
        db.session.commit()
        logger.info(f"AlertJob {job_id} status updated to {status}")

@shared_task(bind=True, max_retries=3)
def dispatch_sms(self, job_id, community_id, sms_alert, phone_number):
    at_service = ATService()
    try:
        start_time = time.time()
        message_id = at_service.send_sms(phone_number, sms_alert)
        latency = time.time() - start_time
        
        log = DeliveryLog(
            community_id=community_id,
            channel='SMS',
            status='Sent' if message_id else 'Failed',
            message_id=message_id,
            pipeline_stage='SMS Dispatch',
            attempt_number=self.request.retries + 1
        )
        db.session.add(log)
        
        job = db.session.get(AlertJob, job_id)
        if job:
            job.sms_latency = latency
            
        db.session.commit()
        return message_id
    except Exception as exc:
        logger.error(f"Error dispatching SMS for job {job_id}: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

@shared_task(bind=True, max_retries=3)
def dispatch_voice(self, job_id, community_id, audio_url, phone_number):
    at_service = ATService()
    try:
        start_time = time.time()
        message_id = at_service.initiate_voice_call(phone_number)
        latency = time.time() - start_time
        
        log = DeliveryLog(
            community_id=community_id,
            channel='VOICE',
            status='Initiated' if message_id else 'Failed',
            message_id=message_id,
            pipeline_stage='Voice Dispatch',
            attempt_number=self.request.retries + 1
        )
        db.session.add(log)
        
        job = db.session.get(AlertJob, job_id)
        if job:
            job.voice_latency = latency
            
        db.session.commit()
        return message_id
    except Exception as exc:
        logger.error(f"Error dispatching Voice for job {job_id}: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

@shared_task(bind=True, max_retries=2)
def process_alert_task(self, job_id):
    """
    Main orchestration task for an alert job.
    """
    overall_start = time.time()
    
    # 1. Update job to Processing
    update_job_status(job_id, 'Processing', started_at=datetime.now(timezone.utc), worker_id=self.request.hostname)
    
    job = db.session.get(AlertJob, job_id)
    if not job:
        logger.error(f"AlertJob {job_id} not found.")
        return

    try:
        community = db.session.get(Community, job.community_id)
        hazard = db.session.get(HazardEvent, job.hazard_id)
        
        if not community or not hazard:
            raise ValueError(f"Community or Hazard not found for job {job_id}")

        logger.info(f"Worker picked job {job_id} for community {community.name}")

        # Update AIService to use community_context
        orchestrator = AIOrchestrationService()
        
        # Monkey patch orchestrator's ai_service call inside to pass context
        # (Alternatively, modify orchestrator directly. For this task, we will just use orchestrator as is but we must modify orchestrator to pass context)
        # Actually, let's call the updated orchestrator method if we modify it, but we can do it directly here for the base generation,
        # or we just update orchestrator to pass community_context.
        # Let's assume orchestrator process_community_alert was updated, but it wasn't! We need to fix orchestrator.py too.
        # But for now, we just call orchestrator.process_community_alert.
        
        payload = orchestrator.process_community_alert(community, hazard)
        
        # In a real app we'd get fine-grained latencies from the orchestrator.
        latencies = payload.get("latencies", {})
        
        sms_alert = payload.get("sms_alert")
        audio_url = payload.get("audio_url")
        
        # 5. Dispatch SMS (Async)
        if sms_alert:
            dispatch_sms.delay(job_id, community.id, sms_alert, community.phone_number)
            logger.info(f"SMS dispatched for job {job_id}")
            
        # 6. Dispatch Voice (Async)
        if audio_url:
            dispatch_voice.delay(job_id, community.id, audio_url, community.phone_number)
            logger.info(f"Voice dispatched for job {job_id}")

        # Update job complete
        processing_time = time.time() - overall_start
        update_job_status(
            job_id, 
            'Completed', 
            completed_at=datetime.now(timezone.utc), 
            processing_time=processing_time,
            ai_latency=latencies.get("ai_latency"),
            translation_latency=latencies.get("translation_latency"),
            tts_latency=latencies.get("tts_latency")
        )
        logger.info(f"Job completed: {job_id}")
        
    except Exception as exc:
        logger.error(f"Error processing job {job_id}: {exc}")
        update_job_status(job_id, 'Failed', error_message=str(exc))
        raise self.retry(exc=exc, countdown=10)
