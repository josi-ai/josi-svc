"""
Custom JSON response for FastAPI with Decimal serialization support.
"""
from decimal import Decimal
from typing import Any
import json
from datetime import datetime, date
from uuid import UUID

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class CustomJSONResponse(JSONResponse):
    """Custom JSON response that handles Decimal and other special types."""
    
    def render(self, content: Any) -> bytes:
        """Render content with custom JSON encoder."""
        # Use FastAPI's jsonable_encoder which handles Pydantic models
        # and common types, then apply our custom serializer for any remaining types
        encoded_content = jsonable_encoder(content, custom_encoder=self.custom_encoder)
        return json.dumps(
            encoded_content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")
    
    @staticmethod
    def custom_encoder(obj: Any) -> Any:
        """Custom encoder for special types."""
        if isinstance(obj, Decimal):
            # Convert Decimal to float for JSON serialization
            return float(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, UUID):
            return str(obj)
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            # Let FastAPI's default encoder handle other types
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")