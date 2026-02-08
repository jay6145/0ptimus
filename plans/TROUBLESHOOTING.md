# Troubleshooting Guide

## Issue: "No inventory items found" on homepage

### Quick Checks

1. **Check if backend is running**
   ```bash
   curl http://localhost:8000/api/health
   ```
   Should return: `{"status":"ok","version":"1.0.0","service":"inventory-health-dashboard"}`

2. **Check if data exists**
   ```bash
   curl http://localhost:8000/api/demo/stats
   ```
   Should show stores, skus, inventory_snapshots counts

3. **Check backend logs**
   Look for:
   - ✅ Database initialized
   - ✅ Demo data generated successfully
   - OR: ✅ Found existing data (X stores)

### Solutions

#### If backend has no data:
```bash
# Regenerate demo data via API
curl -X POST http://localhost:8000/api/demo/regenerate \
  -H "Content-Type: application/json" \
  -d '{"num_stores": 5, "num_skus": 200, "days_history": 60}'
```

OR use the Admin page:
1. Go to http://localhost:3000/admin
2. Click "Regenerate Demo Data"

#### If backend is not responding:
```bash
# Restart containers
docker-compose down
docker-compose up --build
```

#### If frontend can't connect to backend:
Check that `NEXT_PUBLIC_API_URL` is set correctly:
```bash
# In frontend/.env.local (create if doesn't exist)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Manual Data Generation

If automatic generation failed, run manually:

```bash
# Enter backend container
docker-compose exec backend bash

# Run data generator
python -m app.utils.demo_data

# Exit container
exit
```

### Check API Directly

Visit http://localhost:8000/docs and try:
1. GET /api/demo/stats - Check data exists
2. GET /api/overview - Should return inventory items
3. POST /api/demo/regenerate - Generate new data

### Common Issues

**Issue**: Frontend shows loading forever
- **Cause**: Backend not running or wrong API URL
- **Fix**: Check `docker-compose ps` shows both services running

**Issue**: CORS errors in browser console
- **Cause**: Frontend URL not in CORS_ORIGINS
- **Fix**: Backend should have `CORS_ORIGINS=http://localhost:3000`

**Issue**: Database locked errors
- **Cause**: Multiple processes accessing SQLite
- **Fix**: Restart containers: `docker-compose restart`

**Issue**: Import errors in backend
- **Cause**: Missing dependencies
- **Fix**: Rebuild: `docker-compose up --build`

### Verify Everything Works

```bash
# 1. Check backend health
curl http://localhost:8000/api/health

# 2. Check data stats
curl http://localhost:8000/api/demo/stats

# 3. Check overview endpoint
curl http://localhost:8000/api/overview?limit=5

# 4. Open frontend
open http://localhost:3000
```

### Reset Everything

If all else fails:

```bash
# Stop and remove everything
docker-compose down -v

# Remove database
rm -rf backend/data/*.db

# Rebuild and start
docker-compose up --build

# Wait 60 seconds for data generation
# Then refresh http://localhost:3000
```

## Success Indicators

When everything is working:

1. **Backend logs show**:
   ```
   ✅ Database initialized
   📊 Generating demo data...
   ✅ Demo data generated successfully
   INFO: Uvicorn running on http://0.0.0.0:8000
   ```

2. **Frontend shows**:
   - Alert cards with numbers (Critical Stockouts, Low Confidence, Transfer Opportunities)
   - Table with inventory items
   - No "No inventory items found" message

3. **API stats show**:
   ```json
   {
     "stores": 5,
     "skus": 200,
     "inventory_snapshots": 60000,
     "sales_records": 30000,
     "anomalies": 15,
     "transfer_recommendations": 8
   }
   ```

## Still Having Issues?

1. Check Docker logs: `docker-compose logs backend`
2. Check browser console for errors (F12)
3. Verify ports 3000 and 8000 are not in use by other apps
4. Try accessing backend directly: http://localhost:8000/docs
