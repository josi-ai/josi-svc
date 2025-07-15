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
    
    # Define custom encoder as a dictionary mapping types to converter functions
    custom_encoder = {
        Decimal: float,
        datetime: lambda dt: dt.isoformat(),
        date: lambda d: d.isoformat(),
        UUID: str,
    }
    
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