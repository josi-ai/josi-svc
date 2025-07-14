"""
GraphQL module for Astrow application.
"""
from .router import graphql_router, schema

__all__ = [
    "graphql_router",
    "schema"
]