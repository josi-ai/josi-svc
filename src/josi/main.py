from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
import subprocess
import logging
from uuid import UUID
from strawberry.fastapi import GraphQLRouter
import structlog

from josi.api.v1 import v1_router
from josi.api.v1.auth import router as auth_router
from josi.core.config import settings
from josi.core.middleware import setup_middleware
from josi.core.json_response import CustomJSONResponse
from josi.graphql.router import graphql_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup initiated")
    
    # Initialize Redis connection
    try:
        from josi.core.cache import redis_client
        await redis_client.initialize()
        logger.info("Redis connection initialized")
    except Exception as e:
        logger.warning("Redis initialization failed, continuing without cache", error=str(e))
    
    # Run migrations on startup if AUTO_DB_MIGRATION is True
    if getattr(settings, 'auto_db_migration', False):
        logger.info("Running database migrations...")
        try:
            # Use sys.executable to run alembic in the same Python environment
            import sys
            import os
            # Get the project root directory (parent of src)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                check=True,
                cwd=project_root  # Run from project root where alembic.ini is located
            )
            logger.info("Database migrations completed successfully")
        except subprocess.CalledProcessError as e:
            logger.error("Database migration failed", error=e.stderr)
            raise
    
    logger.info("Application startup completed")
    yield
    
    # Cleanup
    logger.info("Application shutdown initiated")
    try:
        await redis_client.close()
        logger.info("Redis connection closed")
    except:
        pass
    logger.info("Application shutdown completed")


app = FastAPI(
    title="Josi - Professional Astrology API",
    version="2.0.0",
    description="Production-ready astrological calculation API with enterprise security and performance",
    debug=getattr(settings, 'debug', False),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    default_response_class=CustomJSONResponse
)

# Setup all middleware (security, CORS, logging, rate limiting, etc.)
setup_middleware(app)

# Include authentication routes
app.include_router(auth_router, prefix="/api/v1")

# Include API routes
app.include_router(v1_router)

# Add GraphQL router
app.include_router(graphql_router, prefix="/graphql")


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}", 
        "version": settings.app_version,
        "environment": settings.environment,
        "endpoints": {
            "rest_api": "/api/v1/* (Consolidated REST API)",
            "graphql": "/graphql (GraphQL endpoint)",
            "graphql_playground": "/graphql (Interactive GraphQL IDE)",
            "docs": "/docs (Interactive API documentation)",
            "redoc": "/redoc (Alternative API documentation)"
        },
        "supported_systems": [
            "Vedic (Indian/Hindu)",
            "Western (Tropical)",
            "Chinese (Four Pillars)",
            "Hellenistic (Ancient Greek)",
            "Mayan (Tzolkin/Haab)",
            "Celtic (Tree/Ogham)",
            "Sidereal",
            "Tropical"
        ],
        "features": [
            "Multi-system chart calculations",
            "Cross-system compatibility analysis",
            "Unified prediction engine",
            "Calendar systems (Panchang, Chinese, Mayan)",
            "Transit tracking across systems",
            "Remedial measures by tradition",
            "Astronomical validation",
            "High-precision calculations"
        ],
        "v1_endpoints": {
            "persons": "/api/v1/persons - Person management",
            "charts": "/api/v1/charts - Chart calculations",
            "panchang": "/api/v1/panchang - Hindu calendar",
            "compatibility": "/api/v1/compatibility - Matching & synastry",
            "transits": "/api/v1/transits - Current & forecast",
            "dasha": "/api/v1/dasha - Planetary periods",
            "predictions": "/api/v1/predictions - Daily/monthly/yearly",
            "remedies": "/api/v1/remedies - Recommendations",
            "location": "/api/v1/location - Geocoding services"
        }
    }