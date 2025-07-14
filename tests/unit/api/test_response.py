"""Unit tests for API response utilities."""
import pytest
from typing import List, Optional

from josi.api.response import ResponseModel


class TestResponseModel:
    """Test ResponseModel functionality."""
    
    def test_success_response_creation(self):
        """Test creating a successful response."""
        data = {"id": 1, "name": "test"}
        response = ResponseModel(
            success=True,
            message="Success",
            data=data
        )
        
        assert response.success is True
        assert response.data == data
        assert response.message == "Success"
        assert response.error is None
    
    def test_success_response_without_data(self):
        """Test creating a successful response without data."""
        response = ResponseModel(
            success=True,
            message="Deleted successfully"
        )
        
        assert response.success is True
        assert response.data is None
        assert response.message == "Deleted successfully"
        assert response.error is None
    
    def test_error_response_creation(self):
        """Test creating an error response."""
        response = ResponseModel(
            success=False,
            message="Validation failed",
            error="Field is required"
        )
        
        assert response.success is False
        assert response.data is None
        assert response.message == "Validation failed"
        assert response.error == "Field is required"
    
    def test_response_model_serialization(self):
        """Test ResponseModel can be serialized properly."""
        response = ResponseModel(
            success=True,
            message="Created successfully",
            data={"id": 1, "name": "test"}
        )
        
        # Convert to dict (simulating JSON serialization)
        response_dict = response.model_dump()
        
        assert response_dict["success"] is True
        assert response_dict["data"] == {"id": 1, "name": "test"}
        assert response_dict["message"] == "Created successfully"
        assert response_dict["error"] is None
    
    def test_response_model_with_list_data(self):
        """Test ResponseModel with list data."""
        data = [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]
        response = ResponseModel(
            success=True,
            message="Items retrieved",
            data=data
        )
        
        assert response.success is True
        assert response.data == data
        assert len(response.data) == 2
        assert response.message == "Items retrieved"
    
    def test_response_model_with_empty_list(self):
        """Test ResponseModel with empty list."""
        data = []
        response = ResponseModel(
            success=True,
            message="No items found",
            data=data
        )
        
        assert response.success is True
        assert response.data == []
        assert len(response.data) == 0
        assert response.message == "No items found"
    
    def test_response_model_fields_validation(self):
        """Test ResponseModel field types."""
        response = ResponseModel(
            success=True,
            message="Test message",
            data={"test": "value"}
        )
        
        assert isinstance(response.success, bool)
        assert isinstance(response.message, str)
        assert isinstance(response.data, dict)
        assert response.error is None
    
    def test_response_model_defaults(self):
        """Test ResponseModel default values."""
        response = ResponseModel(message="Test")
        
        assert response.success is True  # Default value
        assert response.message == "Test"
        assert response.data is None  # Default value
        assert response.error is None  # Default value
    
    def test_response_model_error_with_data(self):
        """Test ResponseModel error response with data."""
        response = ResponseModel(
            success=False,
            message="Partial success",
            data={"processed": 5, "failed": 2},
            error="Some items failed"
        )
        
        assert response.success is False
        assert response.data["processed"] == 5
        assert response.error == "Some items failed"