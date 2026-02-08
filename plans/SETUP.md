# Setup Guide - Windows with Docker Desktop

## Prerequisites

✅ Docker Desktop installed and running
✅ Git installed (to clone the repository)

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd inventory-health-dashboard
```

### 2. Verify Docker is Running

Open Docker Desktop and make sure it's running (you should see the Docker icon in your system tray).

### 3. Start the Application

Open PowerShell or Command Prompt in the project directory and run:

```bash
docker-compose up --build
```

**What this does:**
- Builds the backend (FastAPI) container
- Builds the frontend (Next.js) container
- Starts both services
- Creates a SQLite database
- Automatically generates demo data on first run

**Wait for these messages:**
```
backend-1   | ✅ Database initialized
backend-1   | 📊 Generating demo data...
backend-1   | ✅ Demo data generated successfully
backend-1   | INFO: Uvicorn running on http://0.0.0.0:8000
frontend-1  | ▲ Next.js 14.1.0
frontend-1  | - Local: http://localhost:3000
```

### 4. Access the Application

**Frontend (Dashboard):** http://localhost:3000
**Backend API Docs:** http://localhost:8000/docs
**Health Check:** http://localhost:8000/api/health

### 5. Verify Data Was Generated

Go to: http://localhost:8000/api/demo/stats

You should see:
```json
{
  "stores": 5,
  "skus": 200,
  "inventory_snapshots": 60000,
  "sales_records": 30000+,
  "anomalies": 15+
}
```

If all zeros, see "Troubleshooting" below.

## Common Windows Issues

### Issue: "Docker daemon is not running"
**Solution:** Start Docker Desktop from the Start menu

### Issue: "Port 3000 or 8000 already in use"
**Solution:** 
```bash
# Stop other services using these ports
# Or change ports in docker-compose.yml
```

### Issue: "Drive sharing" or "File sharing" error
**Solution:** 
1. Open Docker Desktop
2. Go to Settings → Resources → File Sharing
3. Add your project directory
4. Click "Apply & Restart"

### Issue: Line ending errors (CRLF vs LF)
**Solution:**
```bash
git config core.autocrlf false
git rm --cached -r .
git reset --hard
```

## If Data Generation Fails

### Method 1: Use the Admin Page
1. Go to http://localhost:3000/admin
2. Click "Regenerate Demo Data"
3. Wait 30-60 seconds

### Method 2: Run Manually in Container
```bash
docker-compose exec backend python -m app.utils.demo_data
```

### Method 3: Check Logs for Errors
```bash
docker-compose logs backend
```

Look for error messages and share them if you need help.

## Stopping the Application

```bash
# Stop containers (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## Restarting Fresh

```bash
# Stop everything
docker-compose down -v

# Remove database
rm -rf backend/data/*.db  # PowerShell: Remove-Item backend/data/*.db

# Rebuild and start
docker-compose up --build
```

## Development Mode (Optional)

If you want to make changes and see them live:

### Backend Changes
The backend auto-reloads when you change Python files.

### Frontend Changes
The frontend auto-reloads when you change TypeScript/React files.

## Verifying Everything Works

### 1. Check Backend Health
```bash
curl http://localhost:8000/api/health
```

Expected: `{"status":"ok","version":"1.0.0"}`

### 2. Check Data Exists
```bash
curl http://localhost:8000/api/demo/stats
```

Expected: Non-zero counts for stores, skus, etc.

### 3. Check Frontend
Open http://localhost:3000

Expected: Dashboard with inventory table and alert cards

### 4. Test API Endpoints
Go to http://localhost:8000/docs

Try these endpoints:
- GET /api/overview
- GET /api/demo/stats
- GET /api/transfers/recommendations

## Project Structure

```
inventory-health-dashboard/
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   ├── api/         # API endpoints
│   │   └── utils/       # Demo data generator
│   └── data/            # SQLite database (created automatically)
├── frontend/            # Next.js React frontend
│   └── src/
│       ├── app/         # Pages
│       └── lib/         # API client & utilities
└── docker-compose.yml   # Docker configuration
```

## Environment Variables (Optional)

If you need to customize:

### Backend (.env in backend/)
```bash
DATABASE_URL=sqlite:///data/inventory.db
CORS_ORIGINS=http://localhost:3000
SECRET_KEY=your-secret-key
```

### Frontend (.env.local in frontend/)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Quick Commands Reference

```bash
# Start
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up --build

# Run command in backend
docker-compose exec backend python -m app.utils.demo_data

# Run command in frontend
docker-compose exec frontend npm run build
```

## Success Checklist

- [ ] Docker Desktop is running
- [ ] `docker-compose up --build` completes without errors
- [ ] Backend shows "✅ Demo data generated successfully"
- [ ] http://localhost:8000/api/health returns OK
- [ ] http://localhost:8000/api/demo/stats shows non-zero counts
- [ ] http://localhost:3000 shows dashboard with data
- [ ] http://localhost:3000/transfers shows transfer recommendations
- [ ] http://localhost:3000/admin shows statistics

## Getting Help

If you encounter issues:

1. Check Docker Desktop is running
2. Check logs: `docker-compose logs backend`
3. Try regenerating data: http://localhost:3000/admin
4. Try manual generation: `docker-compose exec backend python -m app.utils.demo_data`
5. Check TROUBLESHOOTING.md for common issues

## For Hackathon Demo

Once everything is running:

1. **Overview** (/) - Show inventory health dashboard
2. **Click a SKU** - Show detailed analysis with anomalies
3. **Transfers** (/transfers) - Show transfer recommendations
4. **Create Transfer** - Demonstrate the workflow
5. **Admin** (/admin) - Show system statistics

The system is fully functional and ready to demo!
