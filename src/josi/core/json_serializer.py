"""
Custom JSON serializer for handling datetime and other non-serializable objects.
"""
import json
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Any


def custom_json_serializer(obj: Any) -> str:
    """
    Custom JSON serializer that handles datetime, Decimal, UUID, and other objects.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON string representation
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, UUID):
        return str(obj)
    elif hasattr(obj, 'isoformat'):  # date objects
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):  # Custom objects
        return obj.__dict__
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def dumps(obj: Any, **kwargs) -> str:
    """
    JSON dumps with custom serializer.
    
    Args:
        obj: Object to serialize
        **kwargs: Additional arguments for json.dumps
        
    Returns:
        JSON string
    """
    return json.dumps(obj, default=custom_json_serializer, **kwargs)


def loads(s: str, **kwargs) -> Any:
    """
    JSON loads wrapper for consistency.
    
    Args:
        s: JSON string to parse
        **kwargs: Additional arguments for json.loads
        
    Returns:
        Parsed object
    """
    return json.loads(s, **kwargs)