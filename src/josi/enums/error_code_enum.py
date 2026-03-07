from josi.enums.base_enum import BaseEnum


class ErrorCodeEnum(BaseEnum):
    # Authentication & Authorization
    INVALID_API_KEY = (1, "Invalid API Key")
    EXPIRED_TOKEN = (2, "Expired Token")
    INSUFFICIENT_PERMISSIONS = (3, "Insufficient Permissions")

    # Validation Errors
    INVALID_INPUT = (4, "Invalid Input")
    MISSING_REQUIRED_FIELD = (5, "Missing Required Field")
    INVALID_DATE_FORMAT = (6, "Invalid Date Format")
    INVALID_COORDINATES = (7, "Invalid Coordinates")

    # Business Logic Errors
    PERSON_NOT_FOUND = (8, "Person Not Found")
    CHART_CALCULATION_FAILED = (9, "Chart Calculation Failed")
    EPHEMERIS_ERROR = (10, "Ephemeris Error")
    GEOCODING_FAILED = (11, "Geocoding Failed")

    # System Errors
    DATABASE_ERROR = (12, "Database Error")
    CACHE_ERROR = (13, "Cache Error")
    EXTERNAL_SERVICE_ERROR = (14, "External Service Error")

    # Rate Limiting
    RATE_LIMIT_EXCEEDED = (15, "Rate Limit Exceeded")
    QUOTA_EXCEEDED = (16, "Quota Exceeded")
