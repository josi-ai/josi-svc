"""
Production-ready middleware for security, monitoring, and performance
"""
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
import structlog
from typing import Callable

from josi.core.config import settings
from josi.core.security import rate_limiter, security_middleware

logger = structlog.get_logger()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await security_middleware.add_security_headers(request, call_next)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks and auth endpoints
        path = str(request.url.path) if hasattr(request.url, 'path') else request.url.path
        if path in ["/health", "/health/detailed", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Determine endpoint type for rate limiting
        endpoint_type = "general"
        if "/charts/" in path and request.method == "POST":
            endpoint_type = "calculation"
        
        # Check rate limit
        if not await self.rate_limiter.check_rate_limit(request, endpoint_type):
            return Response(
                content='{"detail": "Rate limit exceeded. Please upgrade your plan for higher limits."}',
                status_code=429,
                headers={"Content-Type": "application/json", "Retry-After": "60"}
            )
        
        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging with correlation IDs"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Log request start
        start_time = time.time()
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            correlation_id=correlation_id,
            user_agent=request.headers.get("user-agent", "unknown"),
            client_ip=self._get_client_ip(request)
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Add correlation ID to response
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log successful response
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time_ms=round(process_time * 1000, 2),
                correlation_id=correlation_id
            )
            
            # Record metrics
            metrics_collector.record_request(
                endpoint=f"{request.method} {request.url.path}",
                status_code=response.status_code,
                response_time=process_time
            )
            
            return response
            
        except Exception as e:
            # Calculate response time for failed requests
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                process_time_ms=round(process_time * 1000, 2),
                correlation_id=correlation_id,
                exc_info=True
            )
            
            # Record error metrics
            metrics_collector.record_request(
                endpoint=f"{request.method} {request.url.path}",
                status_code=500,
                response_time=process_time
            )
            
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Enhanced global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            # Let FastAPI handle HTTP exceptions
            raise
        except Exception as e:
            # Enhanced error handling with structured responses
            from josi.core.exceptions import (
                JosiException, ValidationException, exception_handler, log_exception
            )
            
            correlation_id = getattr(request.state, 'correlation_id', 'unknown')
            
            # Log the exception with context
            context = {
                "path": request.url.path,
                "method": request.method,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "client_ip": self._get_client_ip(request)
            }
            log_exception(e, context=context, correlation_id=correlation_id)
            
            # Handle different exception types
            if isinstance(e, JosiException):
                http_exc = await exception_handler.handle_josi_exception(e, correlation_id)
                return Response(
                    content=f'{{"detail": {http_exc.detail}}}',
                    status_code=http_exc.status_code,
                    headers={"Content-Type": "application/json", "X-Correlation-ID": correlation_id}
                )
            elif "validation" in str(type(e)).lower() or isinstance(e, ValueError):
                http_exc = await exception_handler.handle_validation_exception(e, correlation_id)
                return Response(
                    content=f'{{"detail": {http_exc.detail}}}',
                    status_code=http_exc.status_code,
                    headers={"Content-Type": "application/json", "X-Correlation-ID": correlation_id}
                )
            else:
                http_exc = await exception_handler.handle_generic_exception(e, correlation_id)
                return Response(
                    content=f'{{"detail": {http_exc.detail}}}',
                    status_code=http_exc.status_code,
                    headers={"Content-Type": "application/json", "X-Correlation-ID": correlation_id}
                )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the FastAPI app"""
    
    # CORS Configuration (must be first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID", "X-Process-Time", "X-Request-ID"]
    )
    
    # Trusted Host Middleware (second)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=getattr(settings, 'ALLOWED_HOSTS', ["*"])
    )
    
    # Compression (third)
    app.add_middleware(
        GZipMiddleware,
        minimum_size=getattr(settings, 'GZIP_MINIMUM_SIZE', 1000)
    )
    
    # Custom middleware (in order of execution)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    
    logger.info("Middleware configuration completed", 
                cors_origins=getattr(settings, 'ALLOWED_ORIGINS', ["*"]),
                trusted_hosts=getattr(settings, 'ALLOWED_HOSTS', ["*"]))


class MetricsCollector:
    """Simple metrics collector (in production, use Prometheus)"""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "avg_response_time": 0.0,
            "endpoints": {}
        }
    
    def record_request(self, endpoint: str, status_code: int, response_time: float):
        """Record request metrics"""
        self.metrics["requests_total"] += 1
        
        if status_code < 400:
            self.metrics["requests_success"] += 1
        else:
            self.metrics["requests_error"] += 1
        
        # Update average response time
        current_avg = self.metrics["avg_response_time"]
        total_requests = self.metrics["requests_total"]
        self.metrics["avg_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
        
        # Record endpoint-specific metrics
        if endpoint not in self.metrics["endpoints"]:
            self.metrics["endpoints"][endpoint] = {
                "count": 0,
                "avg_time": 0.0,
                "errors": 0
            }
        
        endpoint_data = self.metrics["endpoints"][endpoint]
        endpoint_data["count"] += 1
        endpoint_data["avg_time"] = (
            (endpoint_data["avg_time"] * (endpoint_data["count"] - 1) + response_time) 
            / endpoint_data["count"]
        )
        
        if status_code >= 400:
            endpoint_data["errors"] += 1
    
    def get_metrics(self) -> dict:
        """Get current metrics"""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "avg_response_time": 0.0,
            "endpoints": {}
        }


# Global metrics collector
metrics_collector = MetricsCollector()