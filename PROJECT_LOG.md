# Project Log — Documentation Summary

**Project:** Inventory Health Dashboard (NCR Voyix / Optimus — UGAHacks 11)  
**Purpose:** Chronological and thematic summary of development: goals, phases, features, fixes, decisions, and documentation.  
**Audience:** Team, judges, and future maintainers.

---

## 1. Project Overview

| Item | Description |
|------|-------------|
| **Name** | Inventory Health Dashboard |
| **Event** | UGAHacks 11 |
| **Goal** | Hackathon prototype for restaurant/retail inventory health: stockout prediction, anomaly detection, transfer optimization, peak-hour prep, and IoT telemetry. |
| **Stack** | Next.js 14 (frontend), FastAPI (backend), SQLite (demo), Docker Compose (run). |
| **Status** | Demo-ready; core features complete; testing and polish in progress. |

---

## 2. Development Phases (Log Timeline)

### Phase 1 — Planning & setup
- **Scope:** Requirements, architecture, repo structure, Docker, env templates.
- **Deliverables:** Technical architecture (`plans/technical-architecture.md`), implementation guide, file structure, database schema, core algorithms (forecasting, anomaly, confidence, transfer).
- **Outcome:** One-command run via `docker-compose up --build`; backend and frontend containers with health check and auto demo data when DB is empty.

### Phase 2 — Backend core
- **Scope:** FastAPI app, SQLAlchemy models, database init, demo data generator.
- **Deliverables:** Stores, SKUs, inventory snapshots, daily sales, receipts, transfers, cycle counts, suppliers, anomalies, transfer recommendations; demand forecasting, anomaly detection, confidence scoring, transfer optimizer services.
- **Outcome:** REST API with overview, SKU detail, transfer recommendations, and demo regenerate endpoints; SQLite DB populated on first run.

### Phase 3 — Frontend core
- **Scope:** Next.js App Router, TypeScript, Tailwind, Recharts, API client.
- **Deliverables:** Overview page (alerts, filters, table), SKU detail (forecast, anomalies, recommendations), Transfers page (recommendations, draft/approve), Admin page (stats, regenerate).
- **Outcome:** Full UI for core flows; layout with nav (Overview, Transfers), logo, footer.

### Phase 4 — Peak hour feature
- **Scope:** Hourly demand, prep schedule, stockout-by-hour, dedicated dashboard.
- **Deliverables:** `SalesHourly`, `PrepRecommendation` models; peak hour forecasting service; `/api/peak-hours/{store_id}` and SKU hourly forecast; Peak Hours page (prep schedule, critical items).
- **Outcome:** Peak-hour dashboard and prep schedule; performance tuned (limits, caching) to avoid long timeouts.
- **Docs:** `plans/peak-hour-enhancement.md`.

### Phase 5 — Multi-store & data fixes
- **Scope:** Correct “All stores” behavior, store dropdown, duplicate SKU names.
- **Issues:** Overview with “All stores” showed only one store; dropdown listed one store; same SKU name for different SKUs (e.g. “Tomatoes (Roma)” twice).
- **Fixes:** Overview query reordered and limit increased for even store distribution; store filter options hardcoded to all 5 stores; demo data generator updated for unique SKU names (e.g. “Tomatoes (Roma) #2”).
- **Outcome:** Multi-store view and dropdown correct; no duplicate display names.
- **Docs:** `plans/ALL_STORES_FILTER_FIX.md`, `plans/DUPLICATE_SKU_FIX.md`, `plans/MULTI_STORE_EXPLANATION.md`.

### Phase 6 — Branding & UI polish
- **Scope:** NCR Voyix branding, logo, button styling.
- **Deliverables:** Navbar logo from `public/images/ncr-voyix-og.svg`; logo size and placement; Peak Hours button font aligned with other nav buttons; optional filter-bar logo and divider.
- **Outcome:** Consistent branding and nav styling.

### Phase 7 — IoT telemetry
- **Scope:** Ingest sensor data, show live readings on dashboard, status badges.
- **Deliverables:** `Telemetry` model and table; `POST /api/telemetry`, `GET /api/telemetry/{store_id}/latest` (and history); IoT card on overview (cooler/freezer/ambient temp, humidity); Fahrenheit conversion; cooler calibration (-20°C offset for room-temp sensor); OK/Warning/Critical badges; 10s auto-refresh; demo data and scripts (`simulate_sensors.sh`, `test_telemetry.sh`).
- **Outcome:** Dashboard shows realistic cooler temp (~38°F), other sensors; judges can demo live or simulated IoT.
- **Docs:** `plans/TELEMETRY_API.md`, `plans/IOT_TELEMETRY_CARD.md`, `plans/COOLER_CALIBRATION.md`, `plans/SENSOR_CALIBRATION_SUMMARY.md`, `plans/FAHRENHEIT_CONVERSION.md`, `plans/IMPLEMENTATION_SUMMARY.md`, `plans/CHECKLIST.md`.

### Phase 8 — Documentation & submission prep
- **Scope:** Onboarding, submission checklist, project log.
- **Deliverables:** `README2.md` (detailed onboarding for new members); `SUBMISSION_CHECKLIST.md` (done vs to-do before submit); `PROJECT_LOG.md` (this document).
- **Outcome:** New members can onboard from README2; team can track submission tasks; project history is summarized in one place.

---

## 3. Major Features Delivered

| Feature | Description | Key files / endpoints |
|--------|-------------|------------------------|
| **Stockout prediction** | Demand forecast, days-of-cover, alerts | `services/forecasting.py`, `api/overview.py`, overview page |
| **Anomaly detection** | Residual-based anomalies, plain-English explanations | `services/anomaly_detector.py`, SKU detail |
| **Confidence scoring** | 0–100 inventory accuracy score | `services/confidence_scorer.py`, overview alerts |
| **Transfer optimizer** | Distance-weighted recommendations, draft/approve | `services/transfer_optimizer.py`, `api/transfers.py`, Transfers page |
| **Peak hour forecasting** | Hourly demand, prep schedule, stockout-by-hour | `services/peak_hour_forecasting.py`, `api/peak_hours.py`, Peak Hours page |
| **IoT telemetry** | POST sensor data, latest per store, dashboard card (Fahrenheit, calibration) | `api/telemetry.py`, `models/telemetry.py`, overview IoT card |
| **Demo mode** | Synthetic data: 5 stores, 200 SKUs, 60 days, hourly sales, telemetry | `utils/demo_data.py`, `api/demo.py`, Admin page |

---

## 4. Bug Fixes & Improvements (Summary)

| Issue | Fix | Reference |
|-------|-----|-----------|
| Peak-hours page “Error Loading Data” / timeout | KeyError fix (`peak_period` in all return paths); query limits and caching; reduced N+1 | Peak hour service and API |
| “All stores” showed only one store | Overview query `ORDER BY store_id, sku_id` and higher limit for distribution | `plans/ALL_STORES_FILTER_FIX.md` |
| Store dropdown listed one store | Hardcoded list of 5 stores in frontend | Overview page |
| Duplicate SKU names (e.g. “Tomatoes (Roma)” twice) | Unique names in demo generator (e.g. “#2” suffix) | `plans/DUPLICATE_SKU_FIX.md` |
| Temperatures in Celsius | Display in Fahrenheit with conversion | `plans/FAHRENHEIT_CONVERSION.md` |
| Cooler temp unrealistic (room temp) | -20°C calibration offset for `cooler_temp_c` only | `plans/COOLER_CALIBRATION.md` |
| Logo size/placement | Navbar logo and optional filter-bar logo; font consistency for Peak Hours button | Layout and overview page |

---

## 5. Technical Decisions (Log)

| Decision | Rationale |
|----------|-----------|
| **FastAPI + separate frontend** | Clear separation; Python for data/ML; OpenAPI docs; frontend can be deployed separately. |
| **SQLite for demo** | No external DB; single file; schema compatible with PostgreSQL for production. |
| **Docker Compose** | One-command run; same environment for all; backend health check before frontend. |
| **Demo data on startup** | Empty DB auto-populates so judges see data without extra steps. |
| **Telemetry calibration on frontend** | Backend stays unit-agnostic; display and thresholds adjusted in UI for demo (room-temp sensor → cooler temp). |
| **Peak hour limits and caching** | Avoid timeouts and N+1 while keeping feature usable for demo. |

---

## 6. Documentation Produced

| Document | Purpose |
|----------|--------|
| **README.md** | Short project intro, quick start, features, demo script, API summary. |
| **README2.md** | Full onboarding for new members (architecture, setup, backend/frontend, API, glossary). |
| **SUBMISSION_CHECKLIST.md** | What’s done vs what to do before submission; judge commands. |
| **PROJECT_LOG.md** | This file — project log documentation summary. |
| **SETUP.md** | Step-by-step setup (e.g. Windows + Docker). |
| **TROUBLESHOOTING.md** | Common issues (no data, API unreachable, ports, etc.). |
| **plans/STATUS.md** | Progress by area (planning, backend, frontend, testing, performance). |
| **plans/SUMMARY.md** | Goals, differentiators, stack, architecture decisions. |
| **plans/technical-architecture.md** | System design, schema, algorithms. |
| **plans/implementation-guide.md** | Demo script, API examples, deployment notes. |
| **plans/file-structure.md** | Directory tree and file roles. |
| **plans/peak-hour-enhancement.md** | Peak hour feature plan and implementation notes. |
| **plans/TELEMETRY_API.md** | Telemetry API: endpoints, request/response, examples. |
| **plans/IOT_TELEMETRY_CARD.md** | IoT card behavior, thresholds, demo. |
| **plans/COOLER_CALIBRATION.md** | Cooler temp calibration and thresholds. |
| **plans/SENSOR_CALIBRATION_SUMMARY.md** | Sensor calibration summary. |
| **plans/FAHRENHEIT_CONVERSION.md** | Fahrenheit display and conversion. |
| **plans/ALL_STORES_FILTER_FIX.md** | “All stores” overview fix. |
| **plans/DUPLICATE_SKU_FIX.md** | Unique SKU names in demo data. |
| **plans/MULTI_STORE_EXPLANATION.md** | Multi-store behavior. |
| **plans/IMPLEMENTATION_SUMMARY.md** | IoT telemetry implementation summary. |
| **plans/CHECKLIST.md** | IoT card completion checklist. |

---

## 7. Scripts & Tools

| Script | Purpose |
|--------|--------|
| **simulate_sensors.sh** | Simulate IoT devices POSTing telemetry (demo). |
| **test_telemetry.sh** | End-to-end telemetry API test. |
| **verify_fahrenheit.sh** | Verify temperature conversion (C → F). |

---

## 8. Current State (Summary)

- **Backend:** All core and peak-hour and telemetry endpoints implemented; demo data includes hourly sales and telemetry; DB init and optional auto seed on startup.
- **Frontend:** Overview (alerts, filters, table, IoT card), SKU detail (forecast, anomalies, hourly toggle), Transfers, Peak Hours, Admin; Fahrenheit and cooler calibration on IoT card.
- **Testing:** Manual and ad-hoc scripts; automated unit/integration tests partial.
- **Performance:** Peak hour and overview tuned for demo; further caching possible.
- **Docs:** README, README2, submission checklist, project log, setup, troubleshooting, and plan docs in place.

For detailed next steps and submission tasks, see **SUBMISSION_CHECKLIST.md**. For progress by area, see **plans/STATUS.md**.

---

## 9. Quick Reference

| Need | Document or location |
|------|----------------------|
| Run the project | README.md “Quick Start” or README2.md “How to Run” |
| Onboard a new member | README2.md |
| Prepare for submission | SUBMISSION_CHECKLIST.md |
| Fix common issues | TROUBLESHOOTING.md |
| Understand architecture | plans/technical-architecture.md |
| Demo script for judges | README.md “Demo Script” |
| Telemetry API | plans/TELEMETRY_API.md |
| Project history and decisions | This file (PROJECT_LOG.md) |

---

*Last updated: 2026-02-07 (post–IoT telemetry, documentation, and submission checklist).*
