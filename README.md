# ABM for Site Planning & Tenancy Management

## Project Overview
This project implements an **Agent-Based Model (ABM)** for **Site Planning and Tenancy Management**, designed as a **Distributed Synchronized Digital Twin**.  
The system simulates tenants, environmental conditions, and occupancy dynamics in real time, providing a 3D visualization of buildings, agent movement, and decision workflows.  

The ABM incorporates **real-world signals**, such as IoT sensor data, market factors (FX Beta), and environmental effects (NOAA Sea Level Rise), while enabling **human-in-the-loop governance** for high-impact scenarios.  

---

## Architecture Pattern

### **Distributed Synchronized Digital Twin**
The system is structured in layers:

1. **Ingest (Connectivity Layer)**  
   - **MQTT / IoT Core → FastAPI → Redis**  
   - Real-time ingestion of physical sensor data (occupancy, air quality, etc.) into a Redis state store.

2. **Process (Orchestration & Logic Layer)**  
   - **Celery + Redis Workers + Python Logic (Mesa/Custom)**  
   - Agent ticks are scheduled and distributed across workers.  
   - Physics applied: NOAA Sea Level Rise, FX Beta, Transit Decay (2026 models).

3. **Govern (Human-in-the-Loop)**  
   - **Band C Escalation triggers a “State Lock” in Redis**.  
   - High-impact decisions require human approval via FastAPI endpoints before agents can continue.

4. **Visualize (Frontend / Spatial Engine)**  
   - **Next.js + React + Mapbox GL JS v3**  
   - 3D Digital Twin of buildings with extrusions, real-time agent traces, and dynamic map views via WebSockets.

---

## Key Flow

```text
Sensors (Occupancy, Air Quality)
        │
        ▼
MQTT / IoT → FastAPI → Redis (agent state store)
        │
        ▼
Celery Workers + Python Logic (Mesa/Custom)
        │
        ▼
Band C Escalation? → State Lock → Human-in-the-loop via FastAPI
        │
        ▼
Next.js + Mapbox GL JS v3 → 3D Building Extrusions & Agent Traces
