# Project Summary - NCR Voyix Inventory Health Dashboard

## Overview

This document provides a high-level summary of the Inventory Health Dashboard project for quick reference.

---

## Project Goals

Build a hackathon prototype that:
1. **Predicts stockouts** 3-7 days in advance using demand forecasting
2. **Detects anomalies** and provides inventory accuracy confidence scores
3. **Recommends cross-store transfers** to prevent stockouts before placing new purchase orders

**Timeline:** <48 hours (hackathon constraint)

---

## Key Differentiators

### 1. Anomaly Detection + Confidence Scoring
- **What**: Detects unexplained inventory drops (shrink, theft, receiving errors)
- **How**: Residual-based detection (expected vs actual inventory change)
- **Output**: Plain-English explanations + 0-100 confidence score
- **Value**: Prioritizes cycle counts, reduces phantom inventory

### 2. Cross-Store Transfer Optimizer
- **What**: Recommends inter-store transfers before new purchase orders
- **How**: Distance-weighted greedy matching algorithm
- **Output**: Transfer recommendations with cost-benefit rationale
- **Value**: Prevents stockouts faster and cheaper than new orders

### 3. Optional Arduino Integration (Future)
- **What**: IoT sensors for real-time inventory validation
- **Options**: Smart bin scales OR cold-chain temperature monitoring
- **Value**: Detects phantom inventory and spoilage risk

---

## Technical Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| Frontend | Next.js 14 + TypeScript + Tailwind | Modern, fast, great DX, SSR support |
| Backend | FastAPI + Python 3.11+ | Fast, async, auto-docs, ML ecosystem |
| Database | SQLite (demo) / PostgreSQL (prod) | Fast setup, no dependencies, production-ready |
| Charts | Recharts | Simple, React-native, good for hackathons |
| Deployment | Docker Compose | One-command startup, consistent environment |
| Testing | pytest + Jest | Industry standard, good coverage |

---

## Architecture Decisions

### Why FastAPI over Next.js API Routes?
- Better separation of concerns
- Python ML/data science ecosystem
- Auto-generated OpenAPI documentation
- Easier to scale backend independently

### Why SQLite over PostgreSQL?
- Faster setup (no Docker dependency for DB)
- Good enough for demo (200 SKUs, 5 stores, 60 days)
- Production-ready: Just change connection string to PostgreSQL
- Easier to reset/regenerate demo data

### Why Weighted Moving Average over ML?
- **Explainable**: Judges can understand the logic
- **Fast**: No training required, instant predictions
- **Accurate enough**: Captures weekday/weekend patterns
- **Hackathon-friendly**: Delivers working demo in <48 hours

### Why Greedy Matching over Optimization?
- **Simple**: O(n log n) complexity, fast computation
- **Explainable**: Clear rationale for each recommendation
- **Good enough**: Optimal for single-SKU scenarios
- **Extensible**: Can upgrade to linear programming later

---

## Data Model (Simplified)

```
stores (5 stores)
  ├── inventory_snapshots (daily on-hand)
  ├── sales_daily (daily sales)
  ├── receipts_daily (incoming stock)
  └── transfers (inter-store movements)

skus (200 SKUs)
  ├── category (Beverages, Snacks, Dairy, etc.)
  ├── is_perishable (boolean)
  └── cost/price

anomaly_events (detected issues)
  ├── residual (unexplained change)
  ├── severity (low/medium/high/critical)
  └── explanation_hint (plain English)

transfer_recommendations (suggested transfers)
  ├── from_store → to_store
  ├── urgency_score
  └── rationale
```

---

## Core Algorithms

### 1. Demand Forecasting
```
Input: Historical sales (7/14/28 days)
Process: 
  - Separate weekday vs weekend sales
  - Calculate weighted moving average (recent days weighted higher)
  - Determine next day's expected demand
Output: daily_demand, demand_std, days_of_cover
```

### 2. Anomaly Detection
```
Input: Inventory snapshots, sales, receipts, transfers
Process:
  - expected_delta = receipts - sales + transfers_in - transfers_out
  - actual_delta = on_hand_today - on_hand_yesterday
  - residual = actual_delta - expected_delta
  - if residual < threshold: flag anomaly
Output: anomaly_events with explanations
```

### 3. Confidence Scoring
```
Input: Anomaly history, cycle count history, SKU properties
Process:
  - Start at 100 points
  - Deduct for: anomaly frequency, magnitude, days since count, perishable risk
Output: 0-100 confidence score
```

### 4. Transfer Optimization
```
Input: Inventory states, demand forecasts, store distances
Process:
  - Calculate need (receivers) and surplus (donors) for each store
  - Sort receivers by urgency (lowest days-of-cover)
  - Match with donors using distance-weighted scoring
  - Generate rationale for each transfer
Output: transfer_recommendations
```

---

## API Endpoints (Summary)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/overview` | GET | Inventory health list with filters |
| `/api/sku/{store_id}/{sku_id}` | GET | SKU detail with forecast & anomalies |
| `/api/transfers/recommendations` | GET | Transfer recommendations |
| `/api/transfers/draft` | POST | Create transfer draft |
| `/api/transfers/{id}` | PATCH | Update transfer status |
| `/api/demo/regenerate` | POST | Regenerate demo data |
| `/api/health` | GET | Health check |
| `/docs` | GET | Swagger UI (auto-generated) |

---

## Frontend Pages

| Route | Purpose | Key Components |
|-------|---------|----------------|
| `/` | Overview dashboard | AlertsBar, InventoryTable, Filters |
| `/sku/[storeId]/[skuId]` | SKU detail | ForecastChart, AnomalyTimeline, RecommendationCards |
| `/transfers` | Transfer management | TransferList, TransferCard, WorkflowDiagram |
| `/admin` | Data admin | DemoDataForm, StatsDisplay, UserList |

---

## Demo Data Specifications

- **Stores**: 5 (Atlanta, Boston, Chicago, Denver, Seattle)
- **SKUs**: 200 across 8 categories
- **History**: 60 days
- **Sales Pattern**: Weekday/weekend variation + noise
- **Injected Anomalies**: 
  - 10-15 shrink events (unexplained drops)
  - 3-5 receiving errors (expected receipt didn't arrive)
  - 2-3 systematic shrink patterns (consistent negative residuals)
- **Transfer Opportunities**: 5-8 scenarios where transfer prevents stockout
- **Cycle Counts**: 20% of SKUs counted in last 30 days

---

## Success Criteria (Hackathon)

### Must Have (MVP)
- ✅ Working local demo with Docker Compose
- ✅ Overview dashboard with alerts and filters
- ✅ SKU detail page with forecast and anomalies
- ✅ Transfer recommendations with rationale
- ✅ Demo data generator with realistic patterns
- ✅ Clean UI with Tailwind CSS
- ✅ Basic error handling

### Should Have
- ✅ Anomaly explanations in plain English
- ✅ Confidence scoring with breakdown
- ✅ Distance-weighted transfer optimization
- ✅ Mock authentication
- ✅ Unit tests for core logic
- ✅ Comprehensive README with demo script

### Nice to Have (If Time Permits)
- ⏳ Arduino integration (simulated or real)
- ⏳ CSV upload for custom data
- ⏳ Email/SMS alerts
- ⏳ Mobile-responsive design
- ⏳ Advanced analytics dashboard

---

## Implementation Phases

### Phase 1: Backend Foundation (6-8 hours)
1. Set up project structure
2. Create database schema and models
3. Build demo data generator
4. Implement core services (forecasting, anomaly, transfer, confidence)
5. Create API endpoints
6. Write unit tests

### Phase 2: Frontend Foundation (6-8 hours)
1. Set up Next.js with TypeScript and Tailwind
2. Create UI components library
3. Build Overview dashboard page
4. Build SKU detail page
5. Build Transfers page
6. Build Admin page

### Phase 3: Integration & Polish (4-6 hours)
1. Connect frontend to backend API
2. Add error handling and loading states
3. Implement mock authentication
4. Create Docker Compose configuration
5. Write comprehensive README
6. Test end-to-end workflows

### Phase 4: Demo Preparation (2-4 hours)
1. Generate polished demo data
2. Create demo script for judges
3. Record demo video (optional)
4. Prepare presentation slides
5. Practice demo walkthrough

**Total Estimated Time**: 18-26 hours (well within 48-hour constraint)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Docker issues | Provide local dev setup instructions |
| Complex ML slows development | Use simple heuristics (weighted avg, greedy matching) |
| Frontend complexity | Use Tailwind for rapid styling, Recharts for simple charts |
| Data generation takes too long | Pre-generate and commit demo data as fallback |
| Arduino integration delays core features | Make Arduino completely optional, focus on core dashboard |
| Database performance issues | Use SQLite with proper indexing, limit demo data size |

---

## Judging Strategy

### Innovation (35%)
**Highlight:**
- Anomaly detection with explainability (unique approach)
- Cross-store transfer optimizer (novel value proposition)
- Optional Arduino integration (IoT differentiator)

**Demo:**
- Show anomaly explanation: "Expected +20, got +12, possible receiving error"
- Show transfer ROI: "Transfer costs $45 vs $500 for new PO, arrives 2 days faster"

### Feasibility (30%)
**Highlight:**
- Straightforward data model (standard retail concepts)
- Explainable heuristics (not black-box ML)
- Deployable architecture (Docker Compose, cloud-ready)

**Demo:**
- One-command startup: `docker-compose up --build`
- Show OpenAPI docs: Auto-generated, interactive
- Explain algorithms: Weighted average, greedy matching (simple, effective)

### Customer Impact (35%)
**Highlight:**
- Fewer stockouts (50% reduction target)
- Less phantom inventory (95% accuracy target)
- Less manual guesswork (2-3 hours saved per week)

**Demo:**
- Show stockout prevented by transfer
- Show confidence score prioritizing cycle counts
- Show time savings: Automated recommendations vs manual analysis

---

## Post-Hackathon Roadmap

### Week 1-2: Production Hardening
- Migrate to PostgreSQL
- Add real authentication (JWT, OAuth)
- Implement RBAC (role-based access control)
- Add comprehensive error handling
- Set up monitoring and logging

### Week 3-4: Enhanced Features
- LSTM demand forecasting
- Isolation Forest anomaly detection
- Multi-SKU transfer bundling
- Email/SMS alerts
- Mobile app (React Native)

### Month 2-3: Arduino Integration
- Smart bin scales (load cells + ESP32)
- Cold-chain temperature monitoring
- Real-time telemetry dashboard
- Phantom inventory detection

### Month 4-6: Enterprise Features
- Multi-warehouse support
- Supplier integration (EDI, API)
- Automated PO generation
- Advanced analytics (BI dashboards)
- NCR POS integration

---

## Key Metrics to Track

### Development Metrics
- Lines of code: ~6,500
- Files: ~65
- Test coverage: >80% for core logic
- Build time: <2 minutes
- Startup time: <60 seconds

### Demo Metrics
- Stores: 5
- SKUs: 200
- Days of history: 60
- Anomalies detected: 15-20
- Transfer opportunities: 5-8
- Confidence scores: Range 45-100

### Business Metrics (Post-Deployment)
- Stockout rate reduction: 50%
- Inventory accuracy improvement: 10%
- Transfer utilization: 30%
- Shrink reduction: 1%
- Manager time savings: 2-3 hrs/week
- ROI: 300% in year 1

---

## Resources & References

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Recharts Docs](https://recharts.org/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

### Tutorials
- [FastAPI + SQLAlchemy Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [Next.js App Router Tutorial](https://nextjs.org/docs/app)
- [Docker Compose Tutorial](https://docs.docker.com/compose/gettingstarted/)

### Inspiration
- Retail inventory management best practices
- Demand forecasting techniques
- Anomaly detection algorithms
- Transfer optimization strategies

---

## Contact & Support

**Team:** [Your Team Name]  
**Email:** [your-email@example.com]  
**GitHub:** [repo-url]  
**Demo:** [demo-url]

---

## Next Steps

1. ✅ Review all planning documents
2. ✅ Confirm architecture and approach
3. ⏭️ Switch to Code mode to begin implementation
4. ⏭️ Start with backend database schema and models
5. ⏭️ Build core business logic services
6. ⏭️ Create API endpoints
7. ⏭️ Build frontend components
8. ⏭️ Integrate and test
9. ⏭️ Polish and prepare demo

**Ready to build? Let's switch to Code mode and start implementing! 🚀**
