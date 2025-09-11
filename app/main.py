from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import auth, ingest, metrics
from app.core.config import settings
from app.core.database import init_db
from app.core.auth_dependency import set_auth_service
from app.core.rate_limiting import limiter, rate_limit_exceeded_handler
import logging
import os
import sys

# Configure application logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Set specific loggers to appropriate levels
logging.getLogger('uvicorn.error').setLevel(logging.INFO)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    
    # Startup
    logger.info("Starting Malti application...")

    # Check required environment variables
    required_env_vars = ['MALTI_CONFIG_PATH', 'DATABASE_URL']
    missing_vars = []

    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set the required environment variables and restart the application")
        sys.exit(1)

    await init_db()
    logger.info("Database connection established successfully")
    
    # Initialize auth service to load users and services into RAM
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    set_auth_service(auth_service)
    logger.info(f"Auth service initialized with {len(auth_service.services)} services and {len(auth_service.users)} users")
    
    logger.info("Malti application startup completed")
    yield
    
    # Shutdown
    logger.info("Shutting down Malti application...")


app = FastAPI(
    title="Malti",
    description="Monitoring and Latency Tracking Interface",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(429, rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(ingest.router, prefix="/api/v1", tags=["ingest"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])

# Mount static files for dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    """Serve the dashboard application"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_file = os.path.join(static_dir, "index.html")
    
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        return {"message": "Malti - Telemetry Insights API", "version": "1.0.0", "dashboard": "not built"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}