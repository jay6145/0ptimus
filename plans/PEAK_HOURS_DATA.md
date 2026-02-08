# How to Add Data for the Peak-Hours Page (Hourly Forecast)

The Peak Hours page shows **hourly demand forecasts** and **prep schedules**. If those sections are empty, it’s because the backend has no **hourly sales history** (or no matching SKUs). Here’s how to fix it.

---

## 1. Regenerate Demo Data (recommended)

The demo data generator creates **SalesHourly** records (last 14 days, by hour) for SKUs in **Proteins**, **Salsas & Sauces**, and **Produce**. Regenerating demo data repopulates that table.

### Option A: From the UI

1. Open **http://localhost:3000/admin**
2. Click **“Regenerate Demo Data”** (or equivalent button)
3. Wait for the request to finish
4. Go back to **http://localhost:3000/peak-hours** and refresh

### Option B: From the API

```bash
curl -X POST http://localhost:8000/api/demo/regenerate \
  -H "Content-Type: application/json" \
  -d '{"num_stores": 5, "num_skus": 200, "days_history": 60}'
```

Then refresh the Peak Hours page.

---

## 2. What Gets Created

When you regenerate demo data, the backend:

- Creates **5 stores**, **200 SKUs** (including **Proteins** and **Salsas & Sauces**)
- Creates **60 days** of daily inventory and sales
- Creates **14 days** of **hourly sales** (`SalesHourly`) for Proteins, Salsas & Sauces, and Produce
- Uses that hourly history to compute **hourly demand forecasts** and **prep schedules**

The Peak Hours page only shows **critical items** from **Proteins** and **Salsas & Sauces** (up to 5 SKUs). If those categories exist and have **SalesHourly** data, the “Critical Items - Hourly Forecast” section and the bar charts will fill in.

---

## 3. If You Use a Fresh Database

If you start with an empty DB (e.g. after `docker-compose down -v` and `docker-compose up`):

- The backend **startup** logic will run the demo data generator when it finds **no stores**.
- So the first run after a clean DB should already create hourly data.

If you had an older DB from before **SalesHourly** existed, or the generator failed partway, run **Regenerate Demo Data** once (UI or API above) so that **SalesHourly** is populated.

---

## 4. Verify Hourly Data Exists

Check that the backend has hourly sales and that the peak-hours endpoint returns data:

```bash
# Health
curl -s http://localhost:8000/api/health

# Demo stats (should show total_sales_hourly > 0 after regenerate)
curl -s http://localhost:8000/api/demo/stats

# Peak-hours dashboard for store 1 (should include critical_items with hourly_forecast)
curl -s http://localhost:8000/api/peak-hours/1 | python3 -m json.tool
```

If `total_sales_hourly` is 0, regenerate demo data. If `/api/peak-hours/1` returns `critical_items` with non-empty `hourly_forecast` arrays, the Peak Hours page should show the hourly forecast bars.

---

## 5. Summary

| Problem | What to do |
|--------|------------|
| Hourly forecast / prep schedule empty | **Regenerate demo data** (Admin UI or `POST /api/demo/regenerate`). |
| “No critical items or hourly data yet” on Peak Hours | Same: regenerate demo data so **SalesHourly** and matching SKUs exist. |
| Bar chart shows “No hourly data yet” per item | Same: backend has no hourly history for that store/SKU; regenerate demo data. |

After regenerating, give the backend a few seconds to finish, then refresh **http://localhost:3000/peak-hours**. You should see critical items and hourly forecast bars (e.g. 6am–10pm) with higher bars at lunch (11–2) and dinner (5–8).
