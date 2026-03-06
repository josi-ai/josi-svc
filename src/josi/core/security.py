"""Security utilities — rate limiting, headers, input validation."""
import time
from typing import List, Dict, Any
from functools import wraps
from fastapi import HTTPException, status, Request
import structlog

logger = structlog.get_logger()


class RateLimiter:
    """Rate limiting with subscription-tier-based limits."""

    def __init__(self):
        self.storage = {}
        self.rate_limits = {
            "free": {"requests_per_minute": 60, "calculations_per_hour": 100},
            "explorer": {"requests_per_minute": 300, "calculations_per_hour": 1000},
            "mystic": {"requests_per_minute": 600, "calculations_per_hour": 5000},
            "master": {"requests_per_minute": 1000, "calculations_per_hour": 10000},
        }

    async def check_rate_limit(self, request: Request, endpoint_type: str = "general") -> bool:
        client_id = request.headers.get("x-user-id", request.client.host)
        tier = request.headers.get("x-subscription-tier", "free")
        current_minute = int(time.time() // 60)

        limits = self.rate_limits.get(tier, self.rate_limits["free"])
        key = f"{client_id}:{endpoint_type}:{current_minute}"

        if key not in self.storage:
            self.storage[key] = 0
        self.storage[key] += 1

        if len(self.storage) > 10000:
            old_keys = [k for k in self.storage if int(k.split(':')[-1]) < current_minute - 5]
            for old_key in old_keys:
                del self.storage[old_key]

        limit_key = "calculations_per_hour" if endpoint_type == "calculation" else "requests_per_minute"
        return self.storage[key] <= limits[limit_key]


class SecurityMiddleware:
    """Security headers middleware."""

    def __init__(self):
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

    DOCS_CSP = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "font-src 'self' https://cdn.jsdelivr.net"
    )
    DOCS_PATHS = {"/docs", "/redoc", "/openapi.json"}

    async def add_security_headers(self, request: Request, call_next):
        response = await call_next(request)
        for header, value in self.security_headers.items():
            response.headers[header] = value
        if request.url.path in self.DOCS_PATHS:
            response.headers["Content-Security-Policy"] = self.DOCS_CSP
        import uuid
        response.headers["X-Request-ID"] = str(uuid.uuid4())
        return response


# Global instances
rate_limiter = RateLimiter()
security_middleware = SecurityMiddleware()


# Input validation utilities
def sanitize_string(value: str, max_length: int = 255) -> str:
    if not isinstance(value, str):
        raise ValueError("Value must be a string")
    import re
    cleaned = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', '', value.strip())
    if len(cleaned) > max_length:
        raise ValueError(f"String too long (max {max_length} characters)")
    return cleaned


def validate_uuid(value: str) -> str:
    import uuid
    try:
        uuid.UUID(value)
        return value
    except ValueError:
        raise ValueError("Invalid UUID format")


def validate_coordinates(latitude: float, longitude: float) -> tuple:
    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90")
    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180")
    return latitude, longitude
