# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Documentation Location

All project documentation has been organized in the `docs/markdown/` directory. When looking for:
- Implementation plans
- Test strategies
- API documentation
- Verification reports
- Configuration guides

Please check the `docs/markdown/` folder first. Key documents include:
- `VEDICASTROAPI_TEST_CASES.md` - Comprehensive test cases for API validation
- `TEST_DATA_COLLECTION_PLAN.md` - Strategy for collecting astronomical test data
- `IMPLEMENTATION_PLAN_AI_MARKETPLACE.md` - AI and marketplace feature plans
- `CORRECTNESS_VERIFICATION_PLAN.md` - Accuracy verification strategies

## Project Overview

Astrow is a comprehensive astrology calculation API that supports multiple astrological systems (Vedic, Western, Chinese, Hellenistic, Mayan, Celtic) with both REST and GraphQL interfaces. It uses FastAPI, SQLModel, and PostgreSQL with a multi-tenant architecture.

## Development Commands

### Local Development
```bash
# Install dependencies
poetry install

# Start PostgreSQL and Redis services
docker-compose up -d db redis

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn josi.main:app --reload

# Or use the alias if available
poetry start
```

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_person_service.py

# Run with coverage
poetry run pytest --cov=josi
```

### Code Quality
```bash
# Format code
poetry run black src/

# Lint code
poetry run flake8 src/

# Type checking
poetry run mypy src/
```

### Database Operations
```bash
# Create new migration
poetry run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
poetry run alembic upgrade head

# Downgrade one revision
poetry run alembic downgrade -1

# Show migration history
poetry run alembic history
```

### CRUD Generation
```bash
# Generate CRUD operations for a model
poetry run generate-crud josi.models.{model_file}.{ModelClass} --module {module_name}

# Example
poetry run generate-crud josi.models.person_model.Person --module person

# Overwrite existing files
poetry run generate-crud josi.models.chart_model.AstrologyChart --module chart --overwrite
```

## Architecture

### Project Structure
The codebase follows a layered architecture with clear separation of concerns:

1. **Models Layer** (`src/josi/models/`)
   - SQLModel entities with `{table}_id` primary key naming convention
   - Base models: `SQLBaseModel` (timestamps, soft delete) and `TenantBaseModel` (adds organization_id)
   - Strawberry GraphQL schemas integrated directly in model files
   - All models use UUID primary keys with server-side generation

2. **API Layer** (`src/josi/api/`)
   - REST endpoints organized by version (v1 consolidated)
   - Controllers handle HTTP requests/responses
   - Dependency injection for organization context and database sessions
   - ResponseModel wrapper for consistent API responses

3. **GraphQL Layer** (`src/josi/graphql/`)
   - Strawberry GraphQL integration
   - Schema files mirror REST functionality
   - Uses same service layer as REST API (no direct SQL)
   - Context injection for services

4. **Service Layer** (`src/josi/services/`)
   - Business logic implementation
   - Handles complex operations like geocoding, chart calculations
   - Integrates with external libraries (Swiss Ephemeris, Skyfield)
   - No direct database access

5. **Repository Layer** (`src/josi/repositories/`)
   - Database operations using SQLModel/AsyncSession
   - BaseRepository and TenantRepository base classes
   - Automatic organization filtering for multi-tenancy
   - Soft delete support

6. **Core Layer** (`src/josi/core/`)
   - Centralized configuration in `config.py`
   - All environment variables accessed through `settings` singleton
   - Security, database, and service configurations

### Key Design Patterns

1. **Multi-tenancy**: All entities (except Organization) include organization_id for data isolation
2. **Soft Delete**: All entities have is_deleted/deleted_at fields
3. **UUID Primary Keys**: Named as `{table}_id` (e.g., person_id, chart_id)
4. **Async/Await**: Throughout the application with asyncpg
5. **Dependency Injection**: FastAPI's Depends for database sessions and auth
6. **Repository Pattern**: Clear separation between business logic and data access

### Caching Strategy

- Redis integration with automatic cache invalidation
- Cache decorator for controllers: `@cache(expire=3600, prefix="module_name")`
- Model-specific invalidation patterns in `CacheInvalidator`
- Cache key generation from request parameters

### Authentication

- API key-based authentication via X-API-Key header
- Organization context derived from API key
- All endpoints require valid organization context

## Important Configuration

### Environment Variables (via src/josi/core/config.py)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `AUTO_DB_MIGRATION`: Run migrations on startup (default: False)
- `SECRET_KEY`: JWT secret key
- `API_KEY_HEADER`: Header name for API key (default: X-API-Key)
- `EPHEMERIS_PATH`: Path to Swiss Ephemeris data files
- `GZIP_MINIMUM_SIZE`: Minimum response size for compression (default: 1000)

### Database Schema Conventions
- Primary keys: `{table}_id` format (UUID type)
- Foreign keys: Reference the full primary key name
- Timestamps: created_at, updated_at (auto-managed)
- Soft delete: is_deleted (bool), deleted_at (timestamp)
- Multi-tenant: organization_id on all tables except organization

### API Response Format
All REST endpoints return ResponseModel:
```python
{
    "success": bool,
    "message": str,
    "data": Any,
    "errors": Optional[List[str]]
}
```

## Common Tasks

### Adding a New Model
1. Create model in `src/josi/models/` inheriting from TenantBaseModel
2. Use `{table}_id` as primary key name
3. Run CRUD generator: `poetry run generate-crud josi.models.{file}.{Model} --module {name}`
4. Add router to `src/josi/api/v1/__init__.py`
5. Update GraphQL schema in `src/josi/graphql/router.py`
6. Generate and run migration

### Implementing Astronomical Calculations
- Use pyswisseph for Vedic/Western calculations
- Use skyfield for modern astronomical data
- Store results in chart_data JSON field
- Cache calculations with person_id + chart_type key

### Error Handling
- Raise HTTPException in controllers
- Use ValueError for business logic errors in services
- Log errors with appropriate context
- Return structured error responses via ResponseModel

## Dependencies and Compatibility

- Python 3.12+
- Pydantic 2.9.x (compatibility with Strawberry GraphQL)
- SQLModel 0.0.22
- FastAPI 0.115.x
- Strawberry GraphQL 0.243.x
- PostgreSQL 16 with UUID extension
- Redis 7 for caching

## Deployment Notes

- Use Docker Compose for local development
- PostgreSQL requires uuid-ossp extension
- Redis requires at least 512MB memory
- Swiss Ephemeris data files must be available at EPHEMERIS_PATH
- Run with multiple workers in production (see WORKERS env var)