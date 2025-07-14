"""
GraphQL router with merged types.
"""
import logging
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.tools import merge_types
from strawberry.extensions import AddValidationRules, QueryDepthLimiter, MaxAliasesLimiter, MaxTokensLimiter
from graphql.validation import NoSchemaIntrospectionCustomRule

from josi.core.config import settings

# Import Schema Types
from josi.graphql.schema.organization_schema import OrganizationQuery, OrganizationMutation
from josi.graphql.schema.person_schema import PersonQuery, PersonMutation
from josi.graphql.schema.chart_schema import ChartQuery, ChartMutation

# Get context
from josi.graphql.context import get_context

# Get Logger
log = logging.getLogger("uvicorn")

# settings already imported from josi.core.config

# Merge all query types
Query = merge_types("Query", (
    OrganizationQuery,
    PersonQuery,
    ChartQuery,
))

# Merge all mutation types
Mutation = merge_types("Mutation", (
    OrganizationMutation,
    PersonMutation,
    ChartMutation,
))

# Configure extensions based on environment
extensions = []
enable_graphiql = True

if settings.environment in ["uat", "prod", "stage"]:
    extensions = [
        AddValidationRules([NoSchemaIntrospectionCustomRule]),
        QueryDepthLimiter(max_depth=10),  # Reasonable default
        MaxAliasesLimiter(max_alias_count=10),  # Reasonable default
        MaxTokensLimiter(max_token_count=1000)  # Reasonable default
    ]
    enable_graphiql = False

if settings.debug:
    extensions = []
    enable_graphiql = True

# Create the schema
schema = strawberry.Schema(query=Query, mutation=Mutation, extensions=extensions)

# Create the GraphQL router
graphql_router = GraphQLRouter(schema, context_getter=get_context, graphiql=enable_graphiql)