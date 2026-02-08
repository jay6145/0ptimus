"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db, SessionLocal
from .api import overview, sku, transfers, demo, peak_hours, telemetry

# Create FastAPI app
app = FastAPI(
    title="NCR Voyix Inventory Health Dashboard API",
    description="Predictive inventory management with anomaly detection and transfer optimization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(overview.router, prefix="/api", tags=["overview"])
app.include_router(sku.router, prefix="/api", tags=["sku"])
app.include_router(transfers.router, prefix="/api", tags=["transfers"])
app.include_router(demo.router, prefix="/api", tags=["demo"])
app.include_router(peak_hours.router, prefix="/api", tags=["peak-hours"])
app.include_router(telemetry.router, prefix="/api", tags=["telemetry"])


@app.on_event("startup")
async def startup_event():
    """Initialize database and generate demo data on startup"""
    init_db()
    print("✅ Database initialized")
    
    # Check if demo data exists
    db = SessionLocal()
    try:
        from .models import Store
        store_count = db.query(Store).count()
        
        if store_count == 0:
            print("📊 No data found. Generating demo data...")
            from .utils.demo_data import generate_demo_data
            generate_demo_data()
            print("✅ Demo data generated successfully")
        else:
            print(f"✅ Found existing data ({store_count} stores)")
    except Exception as e:
        print(f"⚠️  Error checking/generating demo data: {e}")
    finally:
        db.close()


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "service": "inventory-health-dashboard"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NCR Voyix Inventory Health Dashboard API",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": {
            "overview": "/api/overview",
            "sku_detail": "/api/sku/{store_id}/{sku_id}",
            "transfers": "/api/transfers/recommendations",
            "demo_stats": "/api/demo/stats"
        }
    }
