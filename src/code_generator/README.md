# CRUD Generator

Automatically generate controllers, services, repositories, and GraphQL schemas from SQLModel definitions.

## Usage

### Command Line

```bash
# Generate CRUD for a model
poetry run generate-crud josi.models.person_model.Person --module person

# Overwrite existing files
poetry run generate-crud josi.models.chart_model.AstrologyChart --module chart --overwrite

# Skip GraphQL generation
poetry run generate-crud josi.models.organization.Organization --module organization --no-graphql
```

### Programmatic Usage

```python
from code_generator import create_crud_for_model
from josi.models.person_model import Person

# Generate CRUD files
generated_files = create_crud_for_model(
    model_class=Person,
    module_name="person",
    skip_existing=True,
    include_graphql=True
)
```

## Generated Files

For each model, the generator creates:

1. **Controller** (`api/v1/controllers/{module}_controller.py`)
   - REST API endpoints with proper validation
   - Automatic caching with Redis
   - Comprehensive error handling
   - OpenAPI documentation

2. **Service** (`services/{module}_service.py`)
   - Business logic layer
   - Input validation
   - Data transformation

3. **Repository** (`repositories/{module}_repository.py`)
   - Database operations
   - Automatic cache invalidation
   - Bulk operations support
   - Soft delete handling

4. **GraphQL Schema** (`graphql/schema/{module}_schema.py`)
   - Query and Mutation types
   - Pagination support
   - Input validation

## Features

- **Multi-tenancy Support**: Automatically handles organization filtering
- **Soft Delete**: Respects `is_deleted` field if present
- **Caching**: Redis caching with automatic invalidation
- **Type Safety**: Full type hints for all generated code
- **Documentation**: Comprehensive docstrings
- **Customizable**: Jinja2 templates can be modified

## Integration Steps

After generating files:

1. **Add Router to API**:
   ```python
   # In api/v1/__init__.py
   from .controllers.{module}_controller import router as {module}_router
   v1_router.include_router({module}_router)
   ```

2. **Update GraphQL Schema**:
   ```python
   # In graphql/router.py
   from .schema.{module}_schema import {Model}Query, {Model}Mutation
   
   Query = merge_types("Query", (
       # ... existing queries
       {Model}Query,
   ))
   
   Mutation = merge_types("Mutation", (
       # ... existing mutations
       {Model}Mutation,
   ))
   ```

3. **Run Migrations**:
   ```bash
   poetry run alembic revision --autogenerate -m "Add {model} table"
   poetry run alembic upgrade head
   ```

## Customization

Templates are located in `src/code_generator/templates/`. You can modify them to match your coding style or add custom functionality.

### Available Template Variables

- `model_name`: The model class name
- `module_name`: The module name (lowercase)
- `table_name`: Database table name
- `fields`: Dictionary of field information
- `relationships`: List of relationship fields
- `primary_key`: Primary key field name
- `has_organization`: Whether model has organization_id
- `has_soft_delete`: Whether model has is_deleted field

### Template Filters

- `snake_case`: Convert to snake_case
- `camel_case`: Convert to camelCase
- `plural`: Pluralize word
- `singular`: Singularize word
- `title_case`: Convert to Title Case

## Examples

### Basic Model

```python
from sqlmodel import SQLModel, Field
from uuid import UUID

class Product(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    name: str
    price: float
    description: Optional[str] = None
```

Generate with:
```bash
poetry run generate-crud josi.models.product.Product --module product
```

### Multi-tenant Model

```python
class Task(TenantBaseModel, table=True):
    task_id: UUID = Field(primary_key=True)
    title: str
    completed: bool = False
    user_id: UUID = Field(foreign_key="user.id")
```

The generator will automatically detect `organization_id` from `TenantBaseModel` and add proper filtering.