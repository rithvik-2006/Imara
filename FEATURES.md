# Imara - Features

This document provides a detailed summary of the features and core logic implemented for the Imara backend.

## 1. Application Architecture
* **Flask Application Factory**: The backend is structured using the App Factory pattern (`app/__init__.py`), ensuring it is highly modular, scalable, and easy to test.
* **Separation of Concerns**: The codebase is cleanly separated into `models`, `routes`, `services`, and `extensions`.

## 2. Spatial Database Integration
* **PostgreSQL + PostGIS**: Full integration with PostGIS for advanced geospatial querying.
* **GeoAlchemy2 ORM**: SQLAlchemy is augmented with GeoAlchemy2 to elegantly manage PostGIS geometry data types directly within Python objects.
* **Alembic Migrations**: Fully configured database migration system that correctly handles PostGIS extensions and ignores internal spatial tables (e.g., `spatial_ref_sys`) to prevent migration conflicts.

## 3. Core Data Models
* **`Community`**: Represents a farming community. Includes fields for UUID, name, preferred language, phone number, and a spatial `POINT` (SRID 4326). Extended with demographic fields (`primary_livelihood`, `population`, `risk_level`, etc.) for deep AI personalization.
* **`HazardEvent`**: Represents a crisis like a flood, drought, or locust swarm. Includes fields for hazard type, severity level, active status, and a spatial `POLYGON` (SRID 4326).
* **`DeliveryLog`**: Tracks dispatch attempts for SMS and Voice payloads, enhanced with advanced state-tracking (`pipeline_stage`, `attempt_number`, `failure_reason`).
* **`AlertJob`**: A dedicated tracking model that monitors the state of background asynchronous processing tasks (`Queued`, `Processing`, `Completed`, `Failed`), keeping detailed metrics on individual AI/Translation/TTS latencies.
* **`KnowledgeDocument`**: Stores structured metadata for humanitarian guidelines used in the RAG pipeline.

## 4. AI Orchestration & RAG Engine (Phase 2)
The AI alerting system operates as a modular, highly scalable orchestration pipeline augmented with local context:
* **Retrieval-Augmented Generation (RAG)**: Uses a local, lightning-fast FAISS vector store and `sentence-transformers` (`all-MiniLM-L6-v2`) to retrieve expert humanitarian guidelines (e.g., WHO/FAO manuals). These guidelines are directly injected into the LLM context to ensure accurate, expert-backed advisories.
* **`ai_service.py`**: Generates structured, localized advisories purely in English using Llama-3.1-70b-instruct via NVIDIA NIM. It dynamically pulls in both RAG context and the specific `Community` demographic profile to personalize the output.
* **`translation_service.py`**: A dedicated translation layer using NVIDIA NIM that contextually translates the generated English alerts into the farmer's preferred local language (e.g., Swahili, Somali).
* **`tts_service.py`**: Converts the translated voice scripts into natural-sounding `.mp3` audio files using `gTTS`, stored locally in `app/static/audio/`.
* **`orchestrator.py`**: The `AIOrchestrationService` ties all services together, handling the data flow, capturing per-step pipeline latencies, and constructing the final delivery payload.

## 4.5. Event-Driven Background Processing
To scale alerting across thousands of communities without blocking the API:
* **Celery & Redis**: All heavy orchestration steps (LLM generation, translation, TTS, SMS/Voice dispatch) are offloaded to background workers.
* **Automatic Retries & Resilience**: Exponential backoff policies protect the system against external API rate limits or failures.
* **`alert_tasks.py`**: Contains modular worker tasks (`process_alert_task`, `dispatch_sms`, `dispatch_voice`) that execute sequentially, strictly updating the `AlertJob` database record in real-time.

## 5. RESTful API Endpoints
The `api_bp` blueprint exposes three critical endpoints:
* **`POST /api/v1/community`**: 
  Accepts a JSON payload with standard coordinates (lat/lng) and registers a new farming community, converting the coordinates into a PostGIS-compatible WKT (Well-Known Text) Point.
* **`POST /api/v1/ingest/hazard`**: 
  Ingests GeoJSON polygon payloads representing hazard zones (simulating external APIs like ICPAC) and saves the geometry to the database.
* **`POST /api/v1/alerts/process`**: 
  **The core spatial engine route.** It executes a highly-optimized database-tier spatial join using `ST_Intersects` to instantly find all `Communities` whose locations fall inside any active `HazardEvent` polygon. It then *asynchronously queues* `AlertJob`s for every affected community and returns immediately.
* **`GET /api/v1/alerts/jobs`**: Fetches the status of all current `AlertJob`s (Queued, Processing, Completed).
* **`GET /api/v1/alerts/jobs/<job_id>`**: Fetches the fine-grained status and latencies of a specific background job.

The `communication_bp` blueprint exposes three webhooks for Africa's Talking:
* **`POST /api/v1/ussd`**: Serves the interactive USSD menu to farmers dialing in. It includes robust phone number parsing and dynamically checks for intersecting hazards.
* **`POST /api/v1/voice/callback`**: Feeds XML instructions to Africa's Talking during outbound calls to play the generated MP3 file.
* **`POST /api/v1/sms/callback`**: Listens for SMS delivery receipts (DLR) to update the `DeliveryLog` status in real-time.

## 6. Husika-Style Delivery Network (Phase 3)
The system leverages Africa's Talking to distribute alerts out to communities using a multi-channel approach:
* **`africastalking_service.py`**: A centralized SDK wrapper that exposes methods to send outbound SMS (`send_sms`) and trigger outbound Voice calls (`initiate_voice_call`) using a virtual AT number.
* **USSD Fallback**: Allows farmers to proactively dial into the system (e.g., `*384*123#`), fetching any active alerts intersecting their location and providing a basic interactive safety menu. 
* **Automated Dispatch**: Tightly integrated into the `check-alerts` pipeline to fire off SMS and Voice calls seamlessly as soon as the AI payload generation completes.

## 7. Next.js Admin Dashboard (Phase 4)
A real-time command center built with Next.js 14 (App Router) and Tailwind CSS to visually monitor the entire orchestrator pipeline.
* **`GET /api/v1/dashboard/stats`**: Aggregates live PostGIS and AT Delivery Log metrics.
* **`GET /api/v1/dashboard/jobs`**: Provides real-time aggregation of the background Celery job queue, displaying counts for active/failed jobs and computing the average pipeline latencies (AI, Translation, SMS, etc.).
* **`GET /api/v1/dashboard/map`**: Dynamically queries PostGIS using `ST_AsGeoJSON()` to return a unified FeatureCollection of all active Hazard polygons and Community points.
* **Interactive Map**: Uses `react-leaflet` to plot the hazard polygons (red/orange) and communities (safe/at-risk/alerted) based on the geospatial data.
* **Live Pipeline Trigger**: The "Simulate Trigger" button fires the async spatial join endpoint. The UI polls the jobs endpoint to show real-time progress bars and alerts as the backend background workers churn through the queue.
