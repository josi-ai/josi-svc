"""
Standard API response model.
"""
from typing import Any, Optional, List, Union
from pydantic import BaseModel


class ResponseModel(BaseModel):
    """Standard response wrapper for all API endpoints."""
    success: bool = True
    message: str
    data: Optional[Union[Any, List[Any]]] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": "123", "name": "Example"},
                "error": None
            }
        }