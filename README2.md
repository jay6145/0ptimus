# NCR Voyix Inventory Health Dashboard — Complete Onboarding Guide

**This document is written for new team members who know nothing about the project.**  
Read it top to bottom to understand what we built, why, how it works, and how to run and contribute.

---

## Table of Contents

1. [What Is This Project?](#1-what-is-this-project)
2. [Who Is It For?](#2-who-is-it-for)
3. [What Problem Does It Solve?](#3-what-problem-does-it-solve)
4. [High-Level Architecture](#4-high-level-architecture)
5. [Tech Stack (What We Use)](#5-tech-stack-what-we-use)
6. [Project Folder Structure](#6-project-folder-structure)
7. [How to Run the Project (Step by Step)](#7-how-to-run-the-project-step-by-step)
8. [Environment and Configuration](#8-environment-and-configuration)
9. [Database and Demo Data](#9-database-and-demo-data)
10. [Backend Deep Dive](#10-backend-deep-dive)
11. [Frontend Deep Dive](#11-frontend-deep-dive)
12. [API Endpoints Reference](#12-api-endpoints-reference)
13. [Features in Detail](#13-features-in-detail)
14. [IoT / Hardware Integration](#14-iot--hardware-integration)
15. [Testing and Quality](#15-testing-and-quality)
16. [Troubleshooting](#16-troubleshooting)
17. [Where to Find More Info](#17-where-to-find-more-info)
18. [Glossary](#18-glossary)

---

## 1. What Is This Project?

**Optimus Inventory Health Dashboard** is a **hackathon project** built for **UGAHacks 11**. It is a **web application** that helps restaurant or retail managers:

- See **inventory health** across multiple stores in one place  
- Get **predictions** of when items will run out (stockouts)  
- Get **alerts** when inventory data looks wrong (anomalies)  
- Get **suggestions** to move stock between stores (transfers) instead of buying more  
- See **peak-hour demand** and prep schedules (when to prep how much)  
- See **live IoT sensor data** (e.g., cooler temperature) on the dashboard  

In short: **one dashboard to predict stockouts, detect problems, and suggest transfers and prep schedules**, with optional **IoT sensor monitoring**.

---

## 2. Who Is It For?

- **Hackathon judges** — we demo it to show innovation, feasibility, and impact.  
- **Restaurant/retail managers** (conceptually) — to reduce stockouts, waste, and manual guesswork.  
- **Us (the team)** — to develop, test, and present the project.  

The current version runs with **synthetic demo data** (no real POS or ERP). It is **demo-ready**, not yet production-ready.

---

## 3. What Problem Does It Solve?

| Problem | What We Do |
|--------|------------|
| **Stockouts** | Predict when items will run out (days and hours) and suggest transfers or prep. |
| **Phantom inventory** | Detect when records don’t match reality (shrink, errors) and score “confidence.” |
| **Waste and extra orders** | Prefer moving stock between stores over new purchase orders when possible. |
| **Peak-hour surprises** | Show hourly demand and prep schedules so staff can prep before rushes. |
| **Equipment failures** | (Optional) Show cooler/freezer temps from IoT sensors and flag critical readings. |

---

## 4. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  USER (Browser)                                                          │
│  http://localhost:3000                                                   │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  FRONTEND (Next.js 14, TypeScript, Tailwind, Recharts)                    │
│  - Overview page (alerts, filters, IoT card)                            │
│  - SKU detail (forecast, anomalies, hourly view)                         │
│  - Transfers page (recommendations, drafts)                              │
│  - Peak Hours page (prep schedule, critical items)                       │
│  - Admin page (stats, regenerate demo data)                              │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │ HTTP (REST API)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI, Python 3.11+)                                         │
│  - /api/overview, /api/sku/..., /api/transfers/..., /api/peak-hours/...  │
│  - /api/telemetry (POST for IoT, GET for latest/history)                 │
│  - /api/demo/regenerate, /api/demo/stats                                │
│  Services: forecasting, anomaly detection, confidence, transfer opt,     │
│            peak-hour forecasting, prep schedule                          │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  DATABASE (SQLite for demo; schema is PostgreSQL-ready)                  │
│  - Stores, SKUs, inventory snapshots, sales (daily + hourly)             │
│  - Transfers, recommendations, anomalies, cycle counts, telemetry       │
└─────────────────────────────────────────────────────────────────────────┘

Optional: IoT devices (e.g., Arduino) POST to /api/telemetry.
```

- **One repo**, two main parts: `frontend/` and `backend/`.  
- **Docker Compose** runs both; backend health check passes before frontend starts.  
- **No external services** required for the demo (everything is self-contained).

---

## 5. Tech Stack (What We Use)

| Layer | Technology | Purpose |
|-------|------------|--------|
| **Frontend** | Next.js 14 (App Router) | React framework, routing, SSR-capable |
| | TypeScript | Type safety |
| | Tailwind CSS | Styling |
| | Recharts | Charts (forecast, hourly bars) |
| **Backend** | FastAPI | REST API, auto OpenAPI docs |
| | Python 3.11+ | Runtime |
| | SQLAlchemy 2.x | ORM, database access |
| | Pydantic | Request/response validation |
| **Database** | SQLite | File-based DB for hackathon (no install) |
| **Deployment** | Docker + Docker Compose | One-command run for backend + frontend |
| **IoT (optional)** | REST API | Any device that can HTTP POST (e.g., Arduino, ESP32) |

You do **not** need to install Python or Node on your machine to run the app — only **Docker** and **Docker Compose**.

---

## 6. Project Folder Structure

```
UGAHacks/ (project root)
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py              # App entry, CORS, routers, startup (DB init + demo data check)
│   │   ├── config.py            # Settings (DB URL, CORS, etc.)
│   │   ├── database.py         # SQLAlchemy engine, session, Base
│   │   ├── api/                # Route handlers (overview, sku, transfers, demo, peak_hours, telemetry)
│   │   ├── models/             # SQLAlchemy models (Store, SKU, InventorySnapshot, etc.)
│   │   ├── services/           # Business logic (forecasting, anomaly, confidence, transfer, peak_hour)
│   │   ├── utils/              # demo_data.py (generates stores, SKUs, sales, telemetry, etc.)
│   │   ├── schemas/            # Pydantic schemas (if any)
│   │   └── tests/              # Backend tests
│   ├── data/                   # Where SQLite file lives inside container (volume)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pytest.ini
│
├── frontend/                    # Next.js application
│   ├── src/
│   │   ├── app/                # App Router pages
│   │   │   ├── layout.tsx      # Root layout, nav (Overview, Transfers), logo, footer
│   │   │   ├── page.tsx        # Main overview dashboard (alerts, filters, table, IoT card)
│   │   │   ├── admin/         # Admin page (stats, regenerate demo)
│   │   │   ├── peak-hours/     # Peak hours dashboard (prep schedule, critical items)
│   │   │   ├── transfers/      # Transfer recommendations and drafts
│   │   │   └── sku/[storeId]/[skuId]/  # SKU detail (forecast, anomalies, hourly)
│   │   ├── lib/
│   │   │   ├── api.ts         # API client (getOverview, getSKUDetail, etc.)
│   │   │   └── types.ts       # TypeScript types for API responses
│   │   └── app/globals.css    # Global + Tailwind
│   ├── public/images/         # e.g. ncr-voyix-og.svg
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── hardware/                    # Optional IoT / Arduino
│   ├── dht_sensor_arduino/     # Arduino sketch for DHT sensor
│   └── telemetry_bridge.py     # Bridge script (e.g., serial → HTTP POST)
│
├── plans/                       # Design and planning docs
│   ├── technical-architecture.md
│   ├── implementation-guide.md
│   ├── file-structure.md
│   ├── peak-hour-enhancement.md
│   └── SUMMARY.md
│
├── docker-compose.yml          # Defines backend + frontend services, volumes, env
├── .env.example                # Example env vars (root)
├── README.md                   # Short README for repo
├── README2.md                  # This file — full onboarding
├── SUBMISSION_CHECKLIST.md     # Done / to-do before submission
├── SETUP.md                    # Setup instructions
├── TROUBLESHOOTING.md          # Common issues and fixes
├── STATUS.md                   # Project status and progress
├── TELEMETRY_API.md            # Telemetry API documentation
├── simulate_sensors.sh         # Script to simulate IoT POSTs (demo)
├── test_telemetry.sh           # Test telemetry API
└── verify_fahrenheit.sh         # Verify temp conversion (Fahrenheit)
```

Key files to open first as a new member:

- `backend/app/main.py` — see all API routes and startup.  
- `frontend/src/app/page.tsx` — main dashboard (overview + IoT card).  
- `frontend/src/lib/api.ts` — how the frontend talks to the backend.  
- `docker-compose.yml` — how the two services and DB volume are defined.

---

## 7. How to Run the Project (Step by Step)

### Prerequisites

- **Docker** and **Docker Compose** installed.  
- **Git** (to clone the repo).  
- No need for Python or Node installed locally for the standard run.

### Steps

1. **Clone the repository** (if you haven’t already):
   ```bash
   git clone <repo-url>
   cd UGAHacks   # or whatever the repo root folder is named
   ```

2. **Optional: copy environment files** (defaults in docker-compose are usually enough):
   ```bash
   cp .env.example .env
   # Edit .env if you need different ports or API URL
   ```

3. **Start everything**:
   ```bash
   docker-compose up --build
   ```
   - First time: builds backend and frontend images, then starts both.  
   - Backend runs on port **8000**, frontend on **3000**.  
   - Backend runs a health check; frontend waits for it to be healthy.

4. **Wait until you see**:
   - Backend: `Database initialized`, then either `Demo data generated` or `Found existing data (X stores)`, and `Uvicorn running on http://0.0.0.0:8000`.
   - Frontend: `Next.js 14.x.x`, `Local: http://localhost:3000`.

5. **Open in browser**:
   - **Dashboard:** [http://localhost:3000](http://localhost:3000)  
   - **API docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)  
   - **Health:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

6. **If the overview is empty** (no inventory rows):
   - Go to [http://localhost:3000/admin](http://localhost:3000/admin) and click **Regenerate Demo Data**,  
   - Or run:
     ```bash
     curl -X POST http://localhost:8000/api/demo/regenerate \
       -H "Content-Type: application/json" \
       -d '{"num_stores": 5, "num_skus": 200, "days_history": 60}'
     ```

To stop:

```bash
docker-compose down
```

To reset database (delete data and start fresh):

```bash
docker-compose down -v
docker-compose up --build
```

(On first startup with empty DB, demo data is generated automatically.)

---

## 8. Environment and Configuration

### Root `.env.example`

- Used for reference; actual values can be in `.env` or set in `docker-compose.yml`.
- Typical vars: `DATABASE_URL`, `CORS_ORIGINS`, `SECRET_KEY`, `NEXT_PUBLIC_API_URL`.

### Backend (`backend/.env.example`)

- `DATABASE_URL` — e.g. `sqlite:///data/inventory.db` (path inside container).  
- `CORS_ORIGINS` — e.g. `http://localhost:3000` so the frontend can call the API.  
- `SECRET_KEY` — used for anything that needs a secret (e.g. signing).

### Frontend (`frontend/.env.local.example`)

- `NEXT_PUBLIC_API_URL` — e.g. `http://localhost:8000`. Must be `NEXT_PUBLIC_*` to be available in the browser.

### Docker Compose (`docker-compose.yml`)

- **backend**: build from `./backend`, port 8000, volume for `./backend` and for SQLite data, env for `DATABASE_URL`, `CORS_ORIGINS`, `SECRET_KEY`. Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`.
- **frontend**: build from `./frontend`, port 3000, env `NEXT_PUBLIC_API_URL=http://localhost:8000`, depends on backend health.
- **Volume** `sqlite-data`: persists SQLite file so data survives container restarts.

You usually don’t need to change these for local demo.

---

## 9. Database and Demo Data

### Database

- **SQLite** file path inside backend container: `/app/data/inventory.db` (mapped from Docker volume).  
- **Schema**: stores, skus, inventory_snapshots, sales_daily, sales_hourly, receipts_daily, transfers, cycle_counts, suppliers, sku_suppliers, anomaly_events, transfer_recommendations, store_distances, telemetry, etc.  
- **Creation**: tables are created on first run via SQLAlchemy `Base.metadata.create_all` in `database.py` / startup.

### Demo Data (`backend/app/utils/demo_data.py`)

- **When**: Run automatically on backend startup if no stores exist; or manually via `POST /api/demo/regenerate`.  
- **What it creates**:
  - 5 stores (Chipotle Athens locations).  
  - 200 SKUs (unique names, categories).  
  - 60 days of history: inventory snapshots, daily sales, receipts, hourly sales (for peak-hour feature).  
  - Store distances, suppliers, cycle counts, anomaly events, transfer recommendations.  
  - **Telemetry**: recent cooler/freezer/ambient temp and humidity readings so the IoT card has data.  
- **Regenerate**: `POST /api/demo/regenerate` with body `{ "num_stores": 5, "num_skus": 200, "days_history": 60 }` (or use Admin UI). This **recreates** all data (drops and repopulates).

---

## 10. Backend Deep Dive

### Entry Point

- `backend/app/main.py`:
  - Creates FastAPI app, adds CORS, mounts routers under `/api`.
  - On startup: `init_db()`, then check store count; if 0, run `generate_demo_data()`.
  - Exposes `/api/health` and `/`.

### Routers (all under prefix `/api`)

| Router | File | Purpose |
|--------|------|--------|
| overview | `api/overview.py` | GET overview (alerts, inventory rows with filters). |
| sku | `api/sku.py` | GET SKU detail (forecast, anomalies, hourly forecast). |
| transfers | `api/transfers.py` | GET recommendations, GET/POST transfers (drafts, approve). |
| demo | `api/demo.py` | POST regenerate, GET demo stats. |
| peak_hours | `api/peak_hours.py` | GET peak-hours dashboard (prep schedule, critical items) for a store. |
| telemetry | `api/telemetry.py` | POST telemetry, GET telemetry history, GET latest per store. |

### Services (`backend/app/services/`)

- **forecasting.py** — demand forecast, days-of-cover.  
- **anomaly_detector.py** — residual-based anomaly detection, explanations.  
- **confidence_scorer.py** — 0–100 confidence score for inventory accuracy.  
- **transfer_optimizer.py** — transfer recommendations (distance-weighted).  
- **peak_hour_forecasting.py** — hourly demand, peak periods, prep schedule, stockout-by-hour.

### Models (`backend/app/models/`)

- Store, SKU, InventorySnapshot, SalesDaily, SalesHourly, ReceiptsDaily, Transfer, CycleCount, Supplier, SKUSupplier, AnomalyEvent, TransferRecommendation, StoreDistance, Telemetry, PrepRecommendation, etc.  
- All exported in `models/__init__.py` and used by API and services.

---

## 11. Frontend Deep Dive

### App Router Structure

- **layout.tsx**: Root layout; nav links (Overview, Transfers), logo (e.g. NCR Voyix), footer.  
- **page.tsx**: Main **overview** page:
  - Alert cards (critical stockouts, low confidence, transfer opportunities).  
  - **IoT telemetry card** (cooler/freezer/ambient temp, humidity; Fahrenheit; OK/Warning/Critical).  
  - Store and risk filters, sort, table of inventory rows.  
  - Links to Peak Hours and Transfers.  
- **sku/[storeId]/[skuId]/page.tsx**: SKU detail — forecast chart, anomalies, hourly forecast toggle, recommendations.  
- **transfers/page.tsx**: Transfer recommendations list and draft/approve flow.  
- **peak-hours/page.tsx**: Peak hours dashboard — prep schedule, critical items, next peak.  
- **admin/page.tsx**: Demo stats and “Regenerate Demo Data” button.

### API Client (`src/lib/api.ts`)

- Base URL from `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).  
- Methods: `getOverview`, `getSKUDetail`, `getTransferRecommendations`, `getTransfers`, peak-hours and telemetry calls, etc.  
- All return typed responses (see `types.ts`).

### Styling

- **Tailwind** via `tailwind.config.ts` (including custom NCR colors if defined).  
- **globals.css** for base styles and any extra utilities.

### IoT Card (Overview)

- Fetches latest telemetry for selected store (or default 1) from `/api/telemetry/{storeId}/latest`.  
- Converts temperatures to **Fahrenheit** and applies a **cooler calibration offset** (-20°C) so a “room temp” sensor reading is displayed as a realistic cooler temp (~38°F).  
- Status (OK/Warning/Critical) from thresholds in Celsius (e.g. cooler 1–4°C).  
- Refreshes every 10 seconds.

---

## 12. API Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|--------|
| GET | `/api/health` | Health check. |
| GET | `/api/overview` | Overview data (alerts + inventory rows); query: `store_id`, `risk_only`, `min_confidence`, `limit`. |
| GET | `/api/sku/{store_id}/{sku_id}` | SKU detail; query: `days_history`. |
| GET | `/api/sku/{store_id}/{sku_id}/hourly` | Hourly demand forecast for SKU. |
| GET | `/api/transfers/recommendations` | Transfer recommendations; query: `min_urgency`, `limit`. |
| GET | `/api/transfers` | List transfers; query: `status`, `store_id`, `limit`. |
| POST | `/api/transfers/draft` | Create draft transfer (body: from_store_id, to_store_id, sku_id, qty). |
| GET | `/api/peak-hours/{store_id}` | Peak hours dashboard (prep schedule, critical items). |
| POST | `/api/telemetry` | Submit telemetry (body: store_id, sensor, value, optional unit, metadata). |
| GET | `/api/telemetry/{store_id}/latest` | Latest reading per sensor for store. |
| GET | `/api/telemetry/{store_id}` | Telemetry history; query: sensor, hours, limit. |
| GET | `/api/demo/stats` | Demo stats (counts). |
| POST | `/api/demo/regenerate` | Regenerate demo data; body: num_stores, num_skus, days_history. |

Full interactive docs: **http://localhost:8000/docs**.

---

## 13. Features in Detail

- **Stockout prediction**: Demand forecast and days-of-cover; low cover triggers alerts.  
- **Anomaly detection**: Compares expected vs actual inventory change; flags and explains anomalies.  
- **Confidence scoring**: 0–100 score per store/SKU; used for “low confidence” alerts.  
- **Transfer optimizer**: Suggests moving stock from stores with surplus to stores at risk; distance-aware.  
- **Peak-hour forecasting**: Hourly demand, prep schedule, “will run out at X:XX” during peak.  
- **IoT telemetry**: POST sensor data; dashboard shows latest temps (Fahrenheit) and OK/Warning/Critical.  
- **Demo mode**: All data from `generate_demo_data()`; no external systems.

---

## 14. IoT / Hardware Integration

- **API**: POST JSON to `/api/telemetry` with `store_id`, `sensor`, `value` (optional `unit`, `metadata`).  
- **Docs**: See `TELEMETRY_API.md` for full request/response and examples.  
- **Dashboard**: Overview page shows latest readings (cooler/freezer/ambient temp, humidity) in °F with status badges.  
- **Cooler calibration**: Frontend subtracts 20°C from `cooler_temp_c` so a room-temperature sensor displays as a realistic cooler temp (~38°F).  
- **Hardware**: `hardware/dht_sensor_arduino/` and `telemetry_bridge.py` are optional (Arduino + bridge to HTTP).  
- **Simulation**: `./simulate_sensors.sh` posts sample readings for demo.

---

## 15. Testing and Quality

- **Backend**: `pytest` (see `backend/pytest.ini`). Run from `backend/`: `pytest` or `pytest --cov=app`.  
- **Frontend**: Jest (see `frontend/package.json` scripts: `test`, `test:coverage`).  
- **Manual**: Use Swagger at http://localhost:8000/docs and click through the app.  
- **Telemetry**: `./test_telemetry.sh` and `./verify_fahrenheit.sh` for quick checks.

---

## 16. Troubleshooting

- **Overview empty**: Regenerate demo data (Admin page or `POST /api/demo/regenerate`).  
- **Frontend can’t reach API**: Check backend is up (`curl http://localhost:8000/api/health`), and `NEXT_PUBLIC_API_URL` is `http://localhost:8000` (and CORS in backend allows it).  
- **Port in use**: Change ports in `docker-compose.yml` or stop the process using 3000/8000.  
- **Slow peak-hours**: Peak-hours endpoint does more work; first load can be slow; we’ve added limits and caching in the service.  
- More: see **TROUBLESHOOTING.md**.

---

## 17. Where to Find More Info

| Topic | File or location |
|-------|-------------------|
| Short README | `README.md` |
| Setup | `SETUP.md` |
| Troubleshooting | `TROUBLESHOOTING.md` |
| Project status | `STATUS.md` |
| Submission to-do | `SUBMISSION_CHECKLIST.md` |
| Telemetry API | `TELEMETRY_API.md` |
| Architecture / algorithms | `plans/technical-architecture.md` |
| Implementation / demo script | `plans/implementation-guide.md` |
| Peak-hour feature | `plans/peak-hour-enhancement.md` |
| IoT calibration | `COOLER_CALIBRATION.md`, `SENSOR_CALIBRATION_SUMMARY.md` |

---

## 18. Glossary

- **SKU** — Stock Keeping Unit (one product at one store).  
- **Stockout** — Inventory reaches zero; we predict when it will happen.  
- **Days of cover** — On-hand quantity ÷ daily demand (how many days until stockout).  
- **Anomaly** — Unexplained inventory change (e.g. shrink, receiving error).  
- **Confidence score** — 0–100 score for how much we trust inventory accuracy.  
- **Transfer** — Moving stock from one store to another (recommendation → draft → approve).  
- **Peak hours** — Lunch (11–2) and dinner (5–8) in our model.  
- **Prep schedule** — When and how much to prep before peak.  
- **Telemetry** — Sensor readings (e.g. temperature) sent to `/api/telemetry`.  
- **Demo data** — Synthetic stores, SKUs, sales, inventory, anomalies, telemetry generated by `demo_data.py`.

---

**You’re ready.** Run `docker-compose up --build`, open http://localhost:3000 and http://localhost:8000/docs, and use this doc + `SUBMISSION_CHECKLIST.md` to contribute and prepare for submission.
