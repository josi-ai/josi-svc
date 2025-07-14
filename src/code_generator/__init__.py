"""
Code generator for automatic CRUD operations.

This module provides tools to generate controllers, services, repositories,
and GraphQL schemas from SQLModel definitions.
"""
from .generator import CRUDGenerator
from .cli import generate_crud

__all__ = ["CRUDGenerator", "generate_crud"]