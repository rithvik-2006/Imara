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
* **`Community`**: Represents a farming community. Includes fields for UUID, name, preferred language, phone number, and a spatial `POINT` (SRID 4326) mapping their exact GPS location.
* **`HazardEvent`**: Represents a crisis like a flood, drought, or locust swarm. Includes fields for hazard type, severity level, active status, and a spatial `POLYGON` (SRID 4326) that accurately maps the geographic boundary of the hazard.
* **`DeliveryLog`**: Tracks dispatch attempts for SMS and Voice payloads, linking the message ID back to the community and tracking the real-time AT delivery status.

## 4. AI Orchestration Engine (Phase 2)
The AI alerting system has been decoupled into a modular, highly scalable orchestration pipeline:
* **`ai_service.py`**: Generates structured, base advisories purely in English using Llama-3.1-70b-instruct via NVIDIA NIM. Returns strict JSON containing an SMS alert, voice script, recommended action, and urgency level.
* **`translation_service.py`**: A dedicated translation layer using NVIDIA NIM that contextually translates the generated English alerts into the farmer's preferred local language (e.g., Swahili, Somali).
* **`tts_service.py`**: Converts the translated voice scripts into natural-sounding `.mp3` audio files using `gTTS`, stored locally in `app/static/audio/`.
* **`orchestrator.py`**: The `AIOrchestrationService` ties all services together, handling the data flow, calculating per-step latencies, and constructing the final delivery payload containing texts and audio URLs.

## 5. RESTful API Endpoints
The `api_bp` blueprint exposes three critical endpoints:
* **`POST /api/v1/community`**: 
  Accepts a JSON payload with standard coordinates (lat/lng) and registers a new farming community, converting the coordinates into a PostGIS-compatible WKT (Well-Known Text) Point.
* **`POST /api/v1/ingest/hazard`**: 
  Ingests GeoJSON polygon payloads representing hazard zones (simulating external APIs like ICPAC) and saves the geometry to the database.
* **`GET /api/v1/check-alerts`**: 
  **The core spatial engine route.** It executes a highly-optimized database-tier spatial join using `ST_Intersects`. It instantly finds all `Communities` whose locations fall inside any active `HazardEvent` polygon, iterates through the affected communities, hits the `AIOrchestrationService` to generate translated text and audio alerts, dispatches the payloads via Africa's Talking, logs the deliveries, and returns a comprehensive payload.

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
* **`GET /api/v1/dashboard/stats`**: Aggregates live PostGIS and AT Delivery Log metrics, feeding the top row of the frontend dashboard (Total Communities, Active Hazards, Alerts Dispatched, Success Rate).
* **`GET /api/v1/dashboard/map`**: Dynamically queries PostGIS using `ST_AsGeoJSON()` to return a unified FeatureCollection of all active Hazard polygons and Community points, automatically calculating safety status based on spatial intersections and delivery receipts.
* **Interactive Map**: Uses `react-leaflet` to plot the hazard polygons (red/orange) and communities (safe/at-risk/alerted) based on the geospatial data.
* **Live Pipeline Trigger**: The "Simulate Trigger" button allows admins to execute the PostGIS spatial join, trigger the NVIDIA NIM AI orchestration, and fire Africa's Talking dispatches directly from the UI, with a real-time activity feed tracking every step.
