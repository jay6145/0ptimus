# Submission Checklist — UGAHacks 11

Use this checklist to see **everything we have done so far** and **everything we need to do before submitting** the project.

---

## Part 1: What We Have Done So Far

### Planning & documentation
- [x] Requirements and scope defined (inventory health, stockout prediction, anomalies, transfers)
- [x] Technical architecture document (`plans/technical-architecture.md`)
- [x] Implementation guide and demo script (`plans/implementation-guide.md`)
- [x] File structure documentation (`plans/file-structure.md`)
- [x] Peak hour enhancement plan (`plans/peak-hour-enhancement.md`)
- [x] Project README (`README.md`)
- [x] Detailed onboarding README for new members (`README2.md`)
- [x] Setup guide (`SETUP.md`), troubleshooting (`TROUBLESHOOTING.md`), status (`STATUS.md`)
- [x] Telemetry API docs (`TELEMETRY_API.md`), cooler calibration docs (`COOLER_CALIBRATION.md`, etc.)
- [x] Submission checklist (this file)

### Project setup
- [x] Git repo with `.gitignore`
- [x] Docker Compose for backend + frontend
- [x] Backend Dockerfile and `requirements.txt`
- [x] Frontend Dockerfile and `package.json`
- [x] Environment examples (`.env.example`, `backend/.env.example`, `frontend/.env.local.example`)
- [x] Directory structure with `__init__.py` and clear separation of API / services / models

### Backend — core
- [x] FastAPI app with CORS, health check, docs at `/docs`
- [x] Database config and SQLAlchemy (SQLite for demo)
- [x] All models: Store, SKU, InventorySnapshot, SalesDaily, SalesHourly, ReceiptsDaily, Transfer, CycleCount, Supplier, SKUSupplier, AnomalyEvent, TransferRecommendation, StoreDistance, Telemetry, PrepRecommendation, etc.
- [x] Startup: DB init + auto demo data generation when empty

### Backend — business logic
- [x] Demand forecasting service
- [x] Anomaly detection service (residual-based, explanations)
- [x] Confidence scoring service (0–100)
- [x] Transfer optimization service (distance-weighted)
- [x] Peak hour forecasting service (hourly demand, prep schedule, stockout-by-hour)
- [x] Demo data generator (stores, SKUs, 60 days history, hourly sales, telemetry, anomalies, recommendations)

### Backend — API endpoints
- [x] `GET /api/health`
- [x] `GET /api/overview` (with store_id, risk_only, min_confidence, limit)
- [x] `GET /api/sku/{store_id}/{sku_id}` (with days_history)
- [x] `GET /api/sku/{store_id}/{sku_id}/hourly`
- [x] `GET /api/transfers/recommendations`
- [x] `GET /api/transfers` (list with filters)
- [x] `POST /api/transfers/draft`
- [x] `GET /api/peak-hours/{store_id}`
- [x] `POST /api/telemetry`
- [x] `GET /api/telemetry/{store_id}/latest`
- [x] `GET /api/telemetry/{store_id}` (history)
- [x] `GET /api/demo/stats`
- [x] `POST /api/demo/regenerate`

### Frontend — structure and UI
- [x] Next.js 14 App Router, TypeScript, Tailwind, Recharts
- [x] Root layout with nav (Overview, Transfers), NCR Voyix logo, footer
- [x] Overview page: alert cards, store/risk filters, sort, inventory table
- [x] SKU detail page: forecast chart, anomalies, recommendations, hourly forecast toggle
- [x] Transfers page: recommendations list, draft/approve flow
- [x] Peak Hours page: prep schedule, critical items, next peak
- [x] Admin page: demo stats, “Regenerate Demo Data” button
- [x] API client (`api.ts`) and types (`types.ts`) for all used endpoints

### Frontend — features and polish
- [x] Multi-store filter with all 5 stores in dropdown
- [x] “All stores” shows data from all stores (overview query fixed for distribution)
- [x] Unique SKU names in demo data (no duplicate “Tomatoes (Roma)”)
- [x] React keys fixed for table rows (`store_id-sku_id`)
- [x] Peak Hours button styling (font) matches other nav buttons
- [x] NCR Voyix logo in navbar (from `public/images/ncr-voyix-og.svg`), size adjusted

### IoT / telemetry
- [x] Telemetry model and table
- [x] POST /api/telemetry and GET latest/history
- [x] IoT card on overview: cooler/freezer/ambient temp, humidity
- [x] Temperatures displayed in Fahrenheit (conversion from Celsius)
- [x] Cooler temp calibration (-20°C offset so room-temp sensor shows realistic cooler temp ~38°F)
- [x] Status badges (OK / Warning / Critical) with thresholds
- [x] Auto-refresh every 10 seconds
- [x] Demo data includes telemetry; `simulate_sensors.sh` and `test_telemetry.sh` for demo/testing

### Performance and data fixes
- [x] Peak hour endpoint: limited critical SKUs, caching, reduced N+1 queries
- [x] Overview: ordering and limit tweaks so “All stores” returns data from all stores
- [x] Demo data: unique SKU names, SalesHourly and Telemetry generation

### Documentation and scripts
- [x] README, README2 (onboarding), SETUP, TROUBLESHOOTING, STATUS
- [x] TELEMETRY_API.md, COOLER_CALIBRATION.md, IOT_TELEMETRY_CARD.md, etc.
- [x] simulate_sensors.sh, test_telemetry.sh, verify_fahrenheit.sh
- [x] plans/ docs (architecture, implementation, peak-hour, file structure)

---

## Part 2: What We Need to Do Before Submitting

### Pre-submission — critical (must do)
- [ ] **Confirm one-command run**: `docker-compose up --build` and open http://localhost:3000 and http://localhost:8000/docs; verify overview loads and API responds.
- [ ] **Regenerate demo data once**: Either via Admin UI or `POST /api/demo/regenerate` so judges see full data (stores, SKUs, alerts, telemetry).
- [ ] **Smoke-test main flows**: Overview → click a SKU → SKU detail; Transfers → recommendations; Peak Hours; Admin → regenerate. No broken links or blank screens.
- [ ] **Check submission platform**: If Devpost/Hackathon platform: know deadline, required fields (repo link, demo video, team, description, tags).
- [ ] **Fill in repo metadata**: In README or submission form, add team name, member names, demo credentials if any (e.g. “No login required; use Admin to regenerate data if needed”).
- [ ] **Ensure repo is pushable**: All files committed (no uncommitted secrets); `.env` not in repo; `docker-compose up` works from a fresh clone.

### Pre-submission — recommended (should do)
- [ ] **Record a short demo video**: 2–5 minutes showing: Peak Hours → Overview (alerts + IoT card) → SKU detail (forecast + hourly) → Transfers → Admin regenerate. Upload to YouTube/Vimeo and add link to submission.
- [ ] **Update README.md**: Add “UGAHacks 11”, team name, demo link (e.g. “Demo: [video link]”), and “Quick start” so judges can run with Docker in 3 steps.
- [ ] **Test from a clean clone**: On another machine or a new folder, `git clone`, `docker-compose up --build`, then run through the smoke test again.
- [ ] **List judging criteria**: In README or a one-pager, briefly map features to Innovation / Feasibility / Impact (or whatever the hackathon uses).
- [ ] **Prepare a 1–2 minute pitch**: What problem, what we built, what’s next (IoT in production, more stores, etc.).

### Pre-submission — optional (nice to have)
- [ ] **Backend unit tests**: Run `pytest` from `backend/`; add or fix tests for at least health and overview (or one critical endpoint).
- [ ] **Frontend lint**: Run `npm run lint` in `frontend/` and fix any blocking errors.
- [ ] **Screenshots**: Add 2–3 screenshots (overview, peak hours, IoT card) to README or `docs/screenshots/`.
- [ ] **.env.example notes**: In root and backend/frontend examples, add one-line comments so judges know what to change if they deploy elsewhere.
- [ ] **License file**: Add LICENSE (e.g. MIT) if the hackathon or org requires it.

### Submission day — checklist
- [ ] **Submit before deadline**: Link repo, video, description, team.
- [ ] **Double-check links**: Repo URL, video URL, and “How to run” (Docker commands) work.
- [ ] **Slack/Discord**: If the hackathon uses it, post repo + video in the channel and mention “NCR Voyix Inventory Health Dashboard”.
- [ ] **Team availability**: At least one person ready to answer questions or re-demo if judges reach out.

---

## Part 3: Quick Reference — Commands for Judges

Paste this into the README or submission form so judges can run the project easily:

```bash
# Clone and run
git clone <your-repo-url>
cd <repo-folder-name>
docker-compose up --build

# Wait until you see:
#   backend  | Uvicorn running on http://0.0.0.0:8000
#   frontend | Local: http://localhost:3000

# Then open:
#   Dashboard:  http://localhost:3000
#   API docs:  http://localhost:8000/docs

# If the overview is empty, regenerate demo data:
curl -X POST http://localhost:8000/api/demo/regenerate \
  -H "Content-Type: application/json" \
  -d '{"num_stores": 5, "num_skus": 200, "days_history": 60}'
# Or use the Admin page: http://localhost:3000/admin → "Regenerate Demo Data"
```

---

## Part 4: Summary

| Category              | Done | To do (before submit) |
|-----------------------|------|-------------------------|
| Planning & docs       | ✅   | Optional: judging-criteria blurb |
| Backend               | ✅   | Smoke test + optional tests |
| Frontend              | ✅   | Smoke test + optional lint |
| IoT / telemetry       | ✅   | — |
| Docker & run          | ✅   | Verify from clean clone |
| Demo video            | —    | **Recommended** |
| Submission form       | —    | **Required** (repo, video, team, description) |
| README for judges     | ✅   | Add team name, demo link, quick start |

**Bottom line:** We have built and documented the full stack (backend, frontend, IoT card, peak hours, transfers, demo data). Before submitting: **run once end-to-end, regenerate data, record a short demo video, fill out the submission form, and optionally add a “Quick start” and judging-criteria section to the README.**
