# Implementation Guide - NCR Voyix Inventory Health Dashboard

## Quick Start (For Judges)

```bash
# Clone and start the application
git clone <repo-url>
cd inventory-health-dashboard

# One-command startup
docker-compose up --build

# Wait ~60 seconds for initialization
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

---

## Demo Script for Judges

### 1. Overview Dashboard (Main Page)

**What to Show:**
1. **Top Alerts Bar** - Highlights critical issues:
   - "5 SKUs at risk of stockout in next 3 days"
   - "3 stores with low inventory confidence (<70)"
   - "8 transfer opportunities available"

2. **Inventory Health Table**:
   - Point out color coding: Red (critical), Yellow (warning), Green (healthy)
   - Show filter by store: "Let's look at Atlanta Store only"
   - Show filter by risk: "Show only high-risk items"
   - Sort by "Days of Cover" ascending to see most urgent items

3. **Key Metrics to Highlight**:
   - SKU "Coca-Cola 12pk" at Atlanta: 15 units on-hand, 8/day demand = 1.9 days cover
   - Confidence score: 65% (yellow) due to recent anomaly
   - Suggested action: "Transfer from Boston (45 units available)"

**Talking Points:**
- "Our system predicts this SKU will stock out in less than 2 days"
- "The confidence score is lower because we detected unexplained inventory drops"
- "Instead of ordering new stock, we can transfer from a nearby store"

---

### 2. SKU Detail Page

**Navigation:** Click on "Coca-Cola 12pk" at Atlanta Store

**What to Show:**

1. **Header Card**:
   - Current on-hand: 15 units
   - Confidence score: 65% with explanation
   - Category: Beverages

2. **Forecast Chart** (Interactive):
   - Line showing on-hand inventory declining
   - Bars showing daily sales (higher on weekends)
   - Forecast line predicting stockout on [date]
   - Point out weekday vs weekend pattern

3. **Anomaly Timeline**:
   - Show residual chart with flagged events
   - Click on anomaly event from 3 days ago
   - **Explanation Card**: "Expected +20 units after receiving shipment, but inventory only increased by 12 units. Possible receiving error or damage. Residual: -8 units."

4. **Recommendation Cards**:
   - **Transfer Recommendation**: "Transfer 25 units from Boston Store (2.5 days excess inventory). Prevents stockout, saves ordering costs."
   - **Reorder Recommendation**: "If transfer not feasible, reorder 84 units (case pack) from Coca-Cola Distributor. Lead time: 3 days."
   - **Cycle Count Recommendation**: "Schedule physical count to verify accuracy (last count: 18 days ago)."

**Talking Points:**
- "The anomaly detector caught a receiving discrepancy automatically"
- "Our weighted forecast accounts for weekend spikes in beverage sales"
- "The system prioritizes transfers over new orders to reduce waste"

---

### 3. Transfers Page

**Navigation:** Click "Transfers" in navigation

**What to Show:**

1. **Recommendations Tab**:
   - List grouped by receiver store
   - **Atlanta Store** section shows 3 recommended transfers:
     - Coca-Cola 12pk from Boston (25 units) - Urgency: High
     - Milk 1gal from Chicago (12 units) - Urgency: Medium
     - Bread Wheat from Denver (8 units) - Urgency: Low

2. **Transfer Card Details**:
   - From: Boston Store (45 units on-hand, 3.2 units/day = 14 days cover)
   - To: Atlanta Store (15 units on-hand, 8 units/day = 1.9 days cover)
   - Quantity: 25 units
   - Distance: 1,080 km
   - Estimated cost: $45
   - **Rationale**: "Receiver will stock out in 1.9 days. Donor has 11 excess days of cover. Transfer prevents stockout and reduces donor's overstock."

3. **Action**: Click "Create Draft Transfer"
   - Shows confirmation modal
   - Click "Confirm"
   - Transfer moves to "Drafts" tab with status "Pending Approval"

4. **Drafts Tab**:
   - Show workflow: Draft → Approved → In Transit → Received
   - Click "Approve" on the draft
   - Status updates to "Approved"

**Talking Points:**
- "The optimizer considers both urgency and distance to minimize costs"
- "Boston has excess inventory that would otherwise sit idle or expire"
- "This transfer prevents a stockout without placing a new purchase order"
- "The workflow supports multi-step approval for larger organizations"

---

### 4. Data Admin Page

**Navigation:** Click "Admin" in navigation

**What to Show:**

1. **Database Statistics**:
   - 5 stores, 200 SKUs, 60 days of history
   - 12,000 inventory snapshots
   - 19 anomalies detected
   - 8 transfer recommendations generated

2. **Demo Data Generator**:
   - Show form with configurable parameters
   - Click "Regenerate Demo Data"
   - Progress bar shows: "Generating stores... SKUs... Sales history... Injecting anomalies..."
   - Success message: "Demo data regenerated successfully"

3. **Mock Users** (if time permits):
   - Show list of demo users:
     - admin@ncr.com / admin123 (Full access)
     - manager.atlanta@ncr.com / manager123 (Atlanta store only)
     - viewer@ncr.com / viewer123 (Read-only)

**Talking Points:**
- "The demo data generator creates realistic patterns with guaranteed edge cases"
- "We inject anomalies to demonstrate the detection system"
- "The system can be reset instantly for multiple demo runs"

---

### 5. Innovation Highlights (Judging Criteria)

**A. Anomaly Detection + Confidence Scoring**

**Innovation:**
- Explainable AI: Every anomaly has a plain-English explanation
- Confidence scoring helps prioritize which SKUs need attention
- Detects multiple anomaly types: shrink, receiving errors, systematic patterns

**Demo:**
- Navigate to SKU with low confidence (e.g., 55%)
- Show anomaly timeline with multiple flagged events
- Read explanation: "Expected -15 units after 15 sales, but inventory dropped by 23 units. Possible shrink or unrecorded sales."
- Show confidence breakdown: "Score reduced by: 15 points (3 anomalies), 12 points (magnitude), 10 points (18 days since count)"

**B. Cross-Store Transfer Optimizer**

**Innovation:**
- Prevents stockouts without new purchase orders
- Reduces waste from overstocked locations
- Distance-weighted algorithm minimizes transfer costs
- Clear rationale for every recommendation

**Demo:**
- Show transfer recommendation with high urgency
- Explain: "Traditional systems would trigger a new PO, costing $500 and taking 3 days"
- "Our system found excess inventory 1,080 km away, transfer cost $45, arrives in 1 day"
- "This saves $455 and prevents stockout faster"

**C. Optional Arduino Integration (Future)**

**Innovation:**
- Real-time bin weight monitoring detects phantom inventory
- Cold-chain temperature monitoring prevents spoilage
- IoT signals improve confidence scoring

**Demo (if implemented):**
- Show telemetry dashboard with live sensor data
- Explain: "System shows 50 units on-hand, but bin scale reads only 20 units weight"
- "Confidence score drops to 40%, triggers immediate cycle count"

---

## Technical Deep Dive (For Technical Judges)

### Architecture Decisions

**1. Why FastAPI + Next.js?**
- FastAPI: Fast, async, auto-generated OpenAPI docs, Python ML ecosystem
- Next.js: Server-side rendering, API routes, TypeScript, excellent DX
- Separation allows independent scaling and deployment

**2. Why SQLite?**
- Fast setup for hackathon demo
- No external dependencies
- Easy to reset/regenerate data
- Production-ready alternative: PostgreSQL (just change connection string)

**3. Why Weighted Moving Average vs ML?**
- Explainable: Judges can understand the logic
- Fast: No training required, instant predictions
- Accurate enough: Captures weekday/weekend patterns
- Hackathon-friendly: Delivers working demo in <48 hours

**4. Why Greedy Matching for Transfers?**
- Optimal for single-SKU scenarios
- Fast computation (O(n log n))
- Explainable recommendations
- Future enhancement: Multi-SKU bundling with linear programming

---

### Code Quality Highlights

**1. Type Safety**:
- Backend: Pydantic models for all API requests/responses
- Frontend: TypeScript interfaces for all data structures
- Database: SQLAlchemy ORM with type hints

**2. Error Handling**:
- API: Proper HTTP status codes, detailed error messages
- Frontend: Error boundaries, loading states, fallbacks
- Database: Transaction rollbacks, constraint validation

**3. Testing**:
- Backend: pytest with fixtures for database setup
- Frontend: Jest + React Testing Library
- Coverage: Core business logic (forecasting, anomaly detection, transfers)

**4. Documentation**:
- OpenAPI/Swagger auto-generated from FastAPI
- README with setup instructions and demo script
- Inline code comments for complex algorithms

---

### Performance Considerations

**1. Database Indexing**:
```sql
CREATE INDEX idx_inventory_store_sku_date ON inventory_snapshots(store_id, sku_id, ts_date);
CREATE INDEX idx_sales_store_sku_date ON sales_daily(store_id, sku_id, ts_date);
CREATE INDEX idx_anomalies_store_sku ON anomaly_events(store_id, sku_id);
```

**2. Caching Strategy**:
- Forecast calculations cached for 1 hour
- Transfer recommendations regenerated on-demand
- Demo data loaded once at startup

**3. Query Optimization**:
- Batch queries for overview page (single query per store)
- Lazy loading for SKU detail page
- Pagination for large result sets

---

## Deployment Options

### Option 1: Docker Compose (Recommended for Demo)
```bash
docker-compose up --build
```
- Pros: One command, consistent environment, easy reset
- Cons: Requires Docker installed

### Option 2: Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
python -m app.utils.demo_data  # Generate data
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```
- Pros: Faster iteration, easier debugging
- Cons: Requires Python 3.11+, Node 18+

### Option 3: Cloud Deployment (Post-Hackathon)
- Frontend: Vercel (auto-deploy from GitHub)
- Backend: Railway, Render, or AWS Lambda
- Database: PostgreSQL on Supabase or AWS RDS
- Estimated cost: $0-20/month for demo traffic

---

## Future Enhancements (Post-Hackathon)

### Phase 1: Enhanced ML
- [ ] LSTM for demand forecasting (capture seasonal trends)
- [ ] Isolation Forest for anomaly detection (unsupervised)
- [ ] Multi-SKU transfer optimization (linear programming)

### Phase 2: Arduino Integration
- [ ] Smart bin scales (load cells + ESP32)
- [ ] Cold-chain temperature monitoring (DHT22 sensors)
- [ ] Real-time telemetry dashboard
- [ ] Phantom inventory detection

### Phase 3: Advanced Features
- [ ] Multi-warehouse support
- [ ] Supplier integration (EDI, API)
- [ ] Automated PO generation
- [ ] Mobile app for store managers
- [ ] Email/SMS alerts for critical stockouts

### Phase 4: Enterprise Features
- [ ] Role-based access control (RBAC)
- [ ] Audit logs
- [ ] Multi-tenant architecture
- [ ] Advanced analytics (BI dashboards)
- [ ] Integration with NCR POS systems

---

## Troubleshooting

### Issue: Docker containers won't start
**Solution:**
```bash
docker-compose down -v  # Remove volumes
docker-compose up --build --force-recreate
```

### Issue: Frontend can't connect to backend
**Solution:**
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check CORS settings in `backend/app/main.py`

### Issue: No demo data visible
**Solution:**
```bash
# Regenerate demo data
curl -X POST http://localhost:8000/api/demo/regenerate
```

### Issue: Slow performance
**Solution:**
- Reduce demo data size (50 SKUs instead of 200)
- Check database indexes are created
- Enable query logging to identify slow queries

---

## Judging Criteria Alignment

### 1. Innovation (35%)
✅ **Anomaly Detection with Explainability**
- Novel approach: Residual-based detection with plain-English explanations
- Confidence scoring helps prioritize actions
- Detects multiple anomaly types automatically

✅ **Cross-Store Transfer Optimizer**
- Unique value: Prevents stockouts without new POs
- Distance-weighted algorithm minimizes costs
- Clear ROI: Saves money, reduces waste, faster fulfillment

✅ **Optional Arduino Integration**
- IoT sensors provide real-time validation
- Detects phantom inventory and spoilage risk
- Differentiates from pure software solutions

### 2. Feasibility (30%)
✅ **Straightforward Data Model**
- Standard retail concepts (stores, SKUs, sales, inventory)
- No complex dependencies or external APIs
- SQLite for easy setup, PostgreSQL-ready for production

✅ **Explainable Heuristics**
- Weighted moving average (not black-box ML)
- Greedy matching (not complex optimization)
- Judges can understand and validate the logic

✅ **Deployable Architecture**
- Docker Compose for one-command startup
- Cloud-ready (Vercel + Railway)
- Scales to 100+ stores without redesign

### 3. Customer Impact (35%)
✅ **Fewer Stockouts**
- Predictive alerts 3-7 days in advance
- Transfer recommendations prevent stockouts faster than new POs
- Measurable KPI: Stockout rate reduction

✅ **Less Phantom Inventory**
- Anomaly detection catches shrink, theft, errors
- Confidence scoring prioritizes cycle counts
- Measurable KPI: Inventory accuracy improvement

✅ **Less Manual Guesswork**
- Automated demand forecasting
- Automated transfer recommendations
- Clear explanations build trust in the system

---

## Success Metrics (Post-Deployment)

### Operational Metrics
- **Stockout Rate**: Target 50% reduction in first 3 months
- **Inventory Accuracy**: Target 95%+ confidence score average
- **Transfer Utilization**: Target 30% of stockouts prevented via transfers
- **Cycle Count Efficiency**: Target 40% reduction in unnecessary counts

### Financial Metrics
- **Cost Savings**: $500-1000 per prevented stockout (vs emergency orders)
- **Transfer Savings**: $200-500 per transfer (vs new PO)
- **Shrink Reduction**: 1-2% improvement in shrink rate
- **ROI**: Target 300% in first year

### User Adoption Metrics
- **Daily Active Users**: Store managers check dashboard daily
- **Action Rate**: 70%+ of recommendations acted upon
- **Time Savings**: 2-3 hours/week per store manager

---

## Demo Data Scenarios

The demo data generator creates these guaranteed scenarios:

### Scenario 1: Imminent Stockout with Transfer Opportunity
- **SKU**: Coca-Cola 12pk
- **Store**: Atlanta (15 units, 8/day demand = 1.9 days)
- **Donor**: Boston (45 units, 3/day demand = 15 days)
- **Action**: Transfer 25 units, prevents stockout in 2 days

### Scenario 2: Low Confidence Due to Anomalies
- **SKU**: Milk 1gal
- **Store**: Chicago (30 units, confidence 55%)
- **Anomalies**: 3 unexplained drops in last 2 weeks
- **Action**: Schedule cycle count, investigate shrink

### Scenario 3: Systematic Shrink Pattern
- **SKU**: Premium Steak
- **Store**: Denver (confidence 45%)
- **Pattern**: Consistent negative residuals (5 of last 7 days)
- **Action**: Immediate investigation, possible theft

### Scenario 4: Receiving Error
- **SKU**: Bread Wheat
- **Store**: Seattle (expected +50, actual +35)
- **Anomaly**: "Expected 50 units from shipment, only 35 arrived"
- **Action**: Contact supplier, file claim

### Scenario 5: Perishable Risk
- **SKU**: Organic Lettuce
- **Store**: Boston (is_perishable=true, last count 21 days ago)
- **Confidence**: 60% (deducted for perishable + no recent count)
- **Action**: Immediate cycle count, check for spoilage

---

## API Examples

### Get Overview with Filters
```bash
curl "http://localhost:8000/api/overview?store_id=1&risk_only=true&min_confidence=70"
```

**Response:**
```json
{
  "items": [
    {
      "store_id": 1,
      "store_name": "Atlanta Store",
      "sku_id": 42,
      "sku_name": "Coca-Cola 12pk",
      "on_hand": 15,
      "daily_demand": 8.2,
      "days_of_cover": 1.83,
      "stockout_date": "2026-02-09",
      "confidence_score": 65,
      "suggested_action": "Transfer from Boston Store",
      "risk_level": "critical"
    }
  ],
  "total": 1,
  "alerts": {
    "critical_stockouts": 5,
    "low_confidence": 3,
    "transfer_opportunities": 8
  }
}
```

### Get SKU Detail
```bash
curl "http://localhost:8000/api/sku/1/42"
```

**Response:**
```json
{
  "store": {"id": 1, "name": "Atlanta Store"},
  "sku": {"id": 42, "name": "Coca-Cola 12pk", "category": "Beverages"},
  "current_state": {
    "on_hand": 15,
    "daily_demand": 8.2,
    "days_of_cover": 1.83,
    "confidence_score": 65
  },
  "forecast": {
    "method": "weighted_moving_average",
    "window_days": 28,
    "weekday_avg": 7.5,
    "weekend_avg": 10.8,
    "next_7_days": [8, 8, 11, 11, 8, 8, 8]
  },
  "anomalies": [
    {
      "date": "2026-02-04",
      "residual": -8,
      "severity": "medium",
      "explanation": "Expected +20 units after receiving shipment, but inventory only increased by 12 units. Possible receiving error or damage."
    }
  ],
  "recommendations": {
    "transfer": {
      "from_store": "Boston Store",
      "qty": 25,
      "rationale": "Prevents stockout in 1.9 days. Donor has 11 excess days of cover."
    },
    "reorder": {
      "qty": 84,
      "supplier": "Coca-Cola Distributor",
      "lead_time_days": 3
    },
    "cycle_count": {
      "priority": "medium",
      "reason": "Last count 18 days ago, recent anomaly detected"
    }
  }
}
```

### Create Transfer Draft
```bash
curl -X POST "http://localhost:8000/api/transfers/draft" \
  -H "Content-Type: application/json" \
  -d '{
    "from_store_id": 2,
    "to_store_id": 1,
    "sku_id": 42,
    "qty": 25
  }'
```

**Response:**
```json
{
  "id": 123,
  "from_store_id": 2,
  "to_store_id": 1,
  "sku_id": 42,
  "qty": 25,
  "status": "draft",
  "created_at": "2026-02-07T05:30:00Z"
}
```

---

## Conclusion

This Inventory Health Dashboard delivers a working prototype that demonstrates:

1. **Innovation**: Explainable anomaly detection + transfer optimization
2. **Feasibility**: Simple architecture, realistic data model, deployable in <48 hours
3. **Customer Impact**: Measurable reduction in stockouts, shrink, and manual work

The system is designed for hackathon success while being production-ready with minimal changes (swap SQLite for PostgreSQL, add authentication, deploy to cloud).

**Next Steps**: Review this plan, then switch to Code mode to begin implementation.
