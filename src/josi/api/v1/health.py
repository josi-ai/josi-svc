"""
Health checks and monitoring endpoints for production deployment
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import asyncio
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

import platform
from typing import Dict, Any

from josi.db.async_db import get_async_db
from josi.api.response import ResponseModel
from josi.core.cache import cache_manager
from josi.core.middleware import metrics_collector

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def basic_health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    
    Returns basic application status without external dependencies.
    Used by load balancers for simple up/down status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "josi-api",
        "version": "2.0.0"
    }


@router.get("/detailed", response_model=ResponseModel)
async def detailed_health_check(db: AsyncSession = Depends(get_async_db)) -> ResponseModel:
    """
    Comprehensive health check with dependency validation
    
    Checks all critical services and returns detailed status information.
    Used for monitoring and alerting systems.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "josi-api",
        "version": "2.0.0",
        "environment": "production",
        "services": {},
        "system": {}
    }
    
    # Database health check
    db_status = await _check_database_health(db)
    health_status["services"]["database"] = db_status
    
    # Cache health check
    cache_status = await _check_cache_health()
    health_status["services"]["cache"] = cache_status
    
    # Swiss Ephemeris health check
    ephemeris_status = await _check_ephemeris_health()
    health_status["services"]["swiss_ephemeris"] = ephemeris_status
    
    # System metrics
    system_status = _get_system_metrics()
    health_status["system"] = system_status
    
    # Determine overall health
    service_statuses = [service["status"] for service in health_status["services"].values()]
    if "unhealthy" in service_statuses:
        health_status["status"] = "unhealthy"
    elif "degraded" in service_statuses:
        health_status["status"] = "degraded"
    
    return ResponseModel(
        success=health_status["status"] in ["healthy", "degraded"],
        message=f"Health check completed - {health_status['status']}",
        data=health_status
    )


@router.get("/readiness")
async def readiness_check(db: AsyncSession = Depends(get_async_db)) -> Dict[str, Any]:
    """
    Kubernetes readiness probe
    
    Checks if the application is ready to receive traffic.
    Returns 200 if ready, 503 if not ready.
    """
    checks = {
        "database": await _check_database_health(db),
        "cache": await _check_cache_health()
    }
    
    # Application is ready if database is healthy
    if checks["database"]["status"] == "healthy":
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }
    else:
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/liveness")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes liveness probe
    
    Checks if the application is alive and should continue running.
    Returns 200 if alive, 500+ if should be restarted.
    """
    # Simple check - if we can respond, we're alive
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": _get_uptime_seconds()
    }


@router.get("/metrics", response_model=ResponseModel)
async def get_metrics() -> ResponseModel:
    """
    Application metrics endpoint
    
    Returns performance metrics for monitoring and alerting.
    In production, this would typically be consumed by Prometheus.
    """
    app_metrics = metrics_collector.get_metrics()
    cache_stats = await cache_manager.get_stats()
    system_metrics = _get_system_metrics()
    
    return ResponseModel(
        success=True,
        message="Metrics retrieved successfully",
        data={
            "application": app_metrics,
            "cache": cache_stats,
            "system": system_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def _check_database_health(db: AsyncSession) -> Dict[str, Any]:
    """Check database connectivity and performance"""
    try:
        start_time = datetime.utcnow()
        
        # Simple query to test connectivity
        result = await db.execute("SELECT 1 as test")
        row = result.fetchone()
        
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if row and row.test == 1:
            status = "healthy" if response_time < 100 else "degraded"
            return {
                "status": status,
                "response_time_ms": round(response_time, 2),
                "message": "Database connection successful"
            }
        else:
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time, 2),
                "message": "Database query failed"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Database connection failed"
        }


async def _check_cache_health() -> Dict[str, Any]:
    """Check cache (Redis) connectivity and performance"""
    try:
        start_time = datetime.utcnow()
        
        # Test cache operations
        test_key = "health_check_test"
        test_value = "ok"
        
        await cache_manager.set(test_key, test_value, ttl=10)
        retrieved_value = await cache_manager.get(test_key)
        
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if retrieved_value == test_value:
            status = "healthy" if response_time < 50 else "degraded"
            cache_stats = await cache_manager.get_stats()
            
            return {
                "status": status,
                "response_time_ms": round(response_time, 2),
                "hit_rate_percent": cache_stats.get("hit_rate_percent", 0),
                "message": "Cache operations successful"
            }
        else:
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time, 2),
                "message": "Cache test failed"
            }
            
    except Exception as e:
        return {
            "status": "degraded",  # Cache failure is not critical
            "error": str(e),
            "message": "Cache connection failed - using fallback"
        }


async def _check_ephemeris_health() -> Dict[str, Any]:
    """Check Swiss Ephemeris functionality"""
    try:
        import swisseph as swe
        from datetime import datetime
        
        start_time = datetime.utcnow()
        
        # Test ephemeris calculation
        jd = swe.julday(2024, 1, 1, 12.0)
        result = swe.calc_ut(jd, swe.SUN)
        
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if result and len(result) >= 2:
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "ephemeris_path": swe.get_library_path(),
                "message": "Swiss Ephemeris calculations working"
            }
        else:
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time, 2),
                "message": "Swiss Ephemeris calculation failed"
            }
            
    except ImportError:
        return {
            "status": "unhealthy",
            "error": "Swiss Ephemeris not installed",
            "message": "Swiss Ephemeris library not available"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Swiss Ephemeris error"
        }


def _get_system_metrics() -> Dict[str, Any]:
    """Get system performance metrics"""
    if not PSUTIL_AVAILABLE:
        return {
            "platform": {
                "system": platform.system(),
                "python_version": platform.python_version()
            },
            "message": "psutil not available - limited metrics"
        }
    
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        disk_available_gb = disk.free / (1024**3)
        
        return {
            "cpu": {
                "percent": round(cpu_percent, 2),
                "count": cpu_count
            },
            "memory": {
                "percent": round(memory_percent, 2),
                "available_gb": round(memory_available_gb, 2),
                "total_gb": round(memory.total / (1024**3), 2)
            },
            "disk": {
                "percent": round(disk_percent, 2),
                "available_gb": round(disk_available_gb, 2),
                "total_gb": round(disk.total / (1024**3), 2)
            },
            "platform": {
                "system": platform.system(),
                "python_version": platform.python_version()
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to retrieve system metrics"
        }


def _get_uptime_seconds() -> float:
    """Get application uptime in seconds"""
    try:
        import time
        if PSUTIL_AVAILABLE:
            return time.time() - psutil.boot_time()
        else:
            return 0.0  # Fallback when psutil not available
    except:
        return 0.0