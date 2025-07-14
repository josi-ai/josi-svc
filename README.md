# Josi API

A comprehensive astrology calculation API supporting multiple astrological systems with both REST and GraphQL interfaces.

## Features

### Astrology Systems
- Vedic (Indian/Hindu) Astrology
- Western (Tropical) Astrology  
- Chinese Astrology (Four Pillars/BaZi)
- Hellenistic Astrology
- Mayan Astrology
- Celtic Astrology

### Technical Features
- **REST API** with multiple versions (v1, v2, v3)
- **GraphQL API** with full query/mutation support
- **Multi-tenant** architecture with organization-based isolation
- **Async/await** throughout with SQLModel and asyncpg
- **UUID primary keys** for all entities
- **Soft delete** support
- **API key** authentication
- **Docker** support with auto-migrations
- **Swiss Ephemeris** for accurate calculations

### Calculation Features
- Multiple house systems (Placidus, Equal, Whole Sign, etc.)
- Ayanamsa calculations (Lahiri, Raman, etc.)
- Transit tracking and predictions
- Compatibility analysis (Ashtakoota, Synastry)
- Divisional charts (D1-D60)
- Dasha systems (Vimshottari, etc.)
- Progressions and directions
- Real astronomical calculations (no hardcoded data)

## Quick Start

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/yourusername/astrow.git
cd astrow

# Start the services
docker-compose up -d

# The API will be available at http://localhost:8000
```

### Manual Installation

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Set up environment variables
export DATABASE_URL=postgresql://user:pass@localhost/astrow
export AUTO_DB_MIGRATION=True

# Run migrations
poetry run alembic upgrade head

# Start the server
poetry run uvicorn josi.main:app --reload
```

## API Documentation

Once running, visit:
- REST API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- GraphQL Playground: http://localhost:8000/graphql

## API Endpoints

### REST API
- `/api/v1/*` - Original endpoints
- `/api/v2/*` - Unified multi-system API
- `/api/v3/*` - Latest REST API with full features
- `/api/vedic/*` - Vedic-specific endpoints

### GraphQL API
- `/graphql` - GraphQL endpoint with interactive playground

See [graphql_examples.md](graphql_examples.md) for GraphQL usage examples.

## Usage Example

### REST API

```python
import requests

# Create a person
person_data = {
    "name": "John Doe",
    "date_of_birth": "1990-01-15",
    "time_of_birth": "14:30:00",
    "place_of_birth": "New York, NY, USA"
}

response = requests.post(
    "http://localhost:8000/api/v3/charts/calculate",
    json={
        **person_data,
        "systems": ["vedic", "western"],
        "include_interpretations": True
    },
    headers={"X-API-Key": "your-api-key"}
)

chart_data = response.json()
```

### GraphQL API

```graphql
mutation CalculateChart {
  calculateChart(
    personId: "person-uuid",
    chartTypes: ["vedic", "western"],
    includeInterpretations: true
  ) {
    chartId
    chartType
    planetPositions
    interpretations {
      title
      summary
    }
  }
}
```

## Architecture

```
src/
├── josi/
│   ├── models/          # SQLModel entities
│   ├── graphql/         # GraphQL schema and resolvers
│   ├── api/            # REST API endpoints
│   ├── services/       # Business logic
│   ├── repositories/   # Data access layer
│   └── core/          # Core utilities
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Quality

```bash
# Linting
poetry run flake8

# Type checking
poetry run mypy src/
```

### Database Migrations

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head
```

## Configuration

Environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `AUTO_DB_MIGRATION` - Run migrations on startup (default: False)
- `DEBUG` - Enable debug mode (default: False)
- `API_KEY_HEADER` - Header name for API key (default: X-API-Key)

## License

MIT License - see LICENSE file for details.
