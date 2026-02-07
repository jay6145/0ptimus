"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db

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


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")


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
        "health": "/api/health"
    }


# TODO: Include API routers
# from .api import overview, sku, transfers, demo, auth
# app.include_router(overview.router, prefix="/api", tags=["overview"])
# app.include_router(sku.router, prefix="/api", tags=["sku"])
# app.include_router(transfers.router, prefix="/api", tags=["transfers"])
# app.include_router(demo.router, prefix="/api", tags=["demo"])
# app.include_router(auth.router, prefix="/api", tags=["auth"])
