"""
Production-ready exception handling with structured error responses
"""
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from fastapi import HTTPException, status
import structlog

logger = structlog.get_logger()


class ErrorCode(str, Enum):
    """Standardized error codes for API responses"""
    
    # Authentication & Authorization
    INVALID_API_KEY = "INVALID_API_KEY"
    EXPIRED_TOKEN = "EXPIRED_TOKEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Validation Errors
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_DATE_FORMAT = "INVALID_DATE_FORMAT"
    INVALID_COORDINATES = "INVALID_COORDINATES"
    
    # Business Logic Errors
    PERSON_NOT_FOUND = "PERSON_NOT_FOUND"
    CHART_CALCULATION_FAILED = "CHART_CALCULATION_FAILED"
    EPHEMERIS_ERROR = "EPHEMERIS_ERROR"
    GEOCODING_FAILED = "GEOCODING_FAILED"
    
    # System Errors
    DATABASE_ERROR = "DATABASE_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    
    # Rate Limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"


class JosiException(Exception):
    """Base exception for Josi application"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(JosiException):
    """Validation-related exceptions"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["invalid_value"] = str(value)
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_INPUT,
            details=error_details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class AuthenticationException(JosiException):
    """Authentication-related exceptions"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_API_KEY,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(JosiException):
    """Authorization-related exceptions"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            status_code=status.HTTP_403_FORBIDDEN
        )


class ResourceNotFoundException(JosiException):
    """Resource not found exceptions"""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found",
            error_code=ErrorCode.PERSON_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id},
            status_code=status.HTTP_404_NOT_FOUND
        )


class CalculationException(JosiException):
    """Astrological calculation exceptions"""
    
    def __init__(self, message: str, calculation_type: str, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        error_details["calculation_type"] = calculation_type
        
        super().__init__(
            message=message,
            error_code=ErrorCode.CHART_CALCULATION_FAILED,
            details=error_details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class EphemerisException(JosiException):
    """Swiss Ephemeris related exceptions"""
    
    def __init__(self, message: str, ephemeris_function: Optional[str] = None):
        details = {}
        if ephemeris_function:
            details["function"] = ephemeris_function
        
        super().__init__(
            message=message,
            error_code=ErrorCode.EPHEMERIS_ERROR,
            details=details,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class DatabaseException(JosiException):
    """Database-related exceptions"""
    
    def __init__(self, message: str = "Database operation failed", operation: Optional[str] = None):
        details = {}
        if operation:
            details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            details=details,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class RateLimitException(JosiException):
    """Rate limiting exceptions"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        current_plan: Optional[str] = None
    ):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
        if current_plan:
            details["current_plan"] = current_plan
            details["upgrade_message"] = "Upgrade your plan for higher limits"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            details=details,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class ErrorResponse:
    """Standardized error response structure"""
    
    @staticmethod
    def format_error(
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Format error response"""
        response = {
            "success": False,
            "error": {
                "code": error_code.value,
                "message": message,
                "timestamp": "2024-01-01T00:00:00Z"  # Would be actual timestamp
            }
        }
        
        if details:
            response["error"]["details"] = details
        
        if correlation_id:
            response["error"]["correlation_id"] = correlation_id
        
        return response
    
    @staticmethod
    def format_validation_error(
        validation_errors: List[Dict[str, Any]],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Format validation error response"""
        return {
            "success": False,
            "error": {
                "code": ErrorCode.INVALID_INPUT.value,
                "message": "Input validation failed",
                "validation_errors": validation_errors,
                "timestamp": "2024-01-01T00:00:00Z",
                "correlation_id": correlation_id
            }
        }


def handle_pydantic_validation_error(exc: Exception) -> Dict[str, Any]:
    """Convert Pydantic validation errors to standardized format"""
    validation_errors = []
    
    if hasattr(exc, 'errors'):
        for error in exc.errors():
            validation_errors.append({
                "field": ".".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg", "Invalid value"),
                "type": error.get("type", "value_error"),
                "input": error.get("input")
            })
    
    return ErrorResponse.format_validation_error(validation_errors)


def log_exception(
    exc: Exception,
    context: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None
) -> None:
    """Log exception with structured context"""
    log_data = {
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "correlation_id": correlation_id
    }
    
    if context:
        log_data.update(context)
    
    if isinstance(exc, JosiException):
        log_data.update({
            "error_code": exc.error_code.value,
            "status_code": exc.status_code,
            "details": exc.details
        })
        logger.warning("Business logic error", **log_data)
    else:
        # Debug the error
        import traceback
        print(f"DEBUG: Exception type: {type(exc).__name__}")
        print(f"DEBUG: Exception message: {str(exc)}")
        print(f"DEBUG: Traceback:")
        traceback.print_exc()
        logger.error("Unexpected error", **log_data, exc_info=True)


class ExceptionHandler:
    """Central exception handler for consistent error responses"""
    
    @staticmethod
    async def handle_josi_exception(exc: JosiException, correlation_id: Optional[str] = None) -> HTTPException:
        """Handle custom Josi exceptions"""
        log_exception(exc, correlation_id=correlation_id)
        
        error_response = ErrorResponse.format_error(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            correlation_id=correlation_id
        )
        
        return HTTPException(
            status_code=exc.status_code,
            detail=error_response
        )
    
    @staticmethod
    async def handle_validation_exception(exc: Exception, correlation_id: Optional[str] = None) -> HTTPException:
        """Handle validation exceptions"""
        log_exception(exc, correlation_id=correlation_id)
        
        error_response = handle_pydantic_validation_error(exc)
        if correlation_id:
            error_response["error"]["correlation_id"] = correlation_id
        
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_response
        )
    
    @staticmethod
    async def handle_generic_exception(exc: Exception, correlation_id: Optional[str] = None) -> HTTPException:
        """Handle unexpected exceptions"""
        log_exception(exc, correlation_id=correlation_id)
        
        error_response = ErrorResponse.format_error(
            error_code=ErrorCode.DATABASE_ERROR,
            message="Internal server error",
            correlation_id=correlation_id
        )
        
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response
        )


# Global exception handler instance
exception_handler = ExceptionHandler()