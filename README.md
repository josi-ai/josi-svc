# Josi - Professional Astrology Calculation API

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](https://github.com/yourusername/josi/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Josi is a production-ready, multi-tenant astrology calculation API that supports multiple astrological systems with enterprise-grade security, performance, and scalability. Built with FastAPI, it provides both REST and GraphQL interfaces for comprehensive astrological calculations with AI-powered interpretations.

## 🌟 Features

### Astrological Systems
- **Vedic (Sidereal)**: Complete Vedic astrology with Vimshottari Dasha, Panchang, divisional charts
- **Western (Tropical)**: Natal charts, progressions, solar returns, transits
- **Chinese**: BaZi Four Pillars, Chinese zodiac
- **Hellenistic**: Time lords, zodiacal releasing, lots
- **Mayan**: Tzolkin calendar, day signs
- **Celtic**: Tree astrology, lunar zodiac

### Technical Features
- **Multi-tenant Architecture**: Complete data isolation per organization
- **AI-Powered Interpretations**: GPT-4 and Claude integration for personalized insights
- **Astrologer Marketplace**: Platform for professional astrologers to offer consultations
- **Real-time Consultations**: WebSocket support for live astrology sessions
- **User Authentication**: JWT tokens with subscription tiers (Free, Explorer, Mystic, Master)
- **OAuth2 Authentication**: Support for Google and GitHub login
- **API Key Authentication**: For programmatic access
- **Vector Database**: Qdrant integration for similarity search and knowledge storage
- **Neural Pathway Questions**: AI-generated psychological self-awareness prompts
- **GraphQL & REST APIs**: Flexible data querying
- **Redis Caching**: High-performance response caching
- **Comprehensive Testing**: 90%+ test coverage with real astronomical data validation
- **Google Cloud Ready**: Deployment configurations for GKE and Cloud Run
- **Production Security**: Rate limiting, CORS, security headers, input validation
- **Remedy Recommendations**: AI-powered personalized astrological remedies
- **Transit Monitoring**: Real-time planetary transit tracking and notifications

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 16
- Redis 7
- Docker & Docker Compose
- Poetry (Python package manager)

### Local Development Setup

#### 1. Clone the repository
```bash
git clone https://github.com/josi-ai/josi-svc.git
cd josi-svc
```

#### 2. Install the Josi CLI (recommended)

The Josi CLI automates your entire development workflow — Docker, migrations, testing, linting, and more. It requires Node.js 18+.

```bash
# Install Node.js if needed (macOS)
brew install node

# Build and link the CLI globally
cd cli && npm install && npm run build && npm link && cd ..

# Bootstrap your machine (installs Python, Poetry, Docker, etc.)
josi init

# Verify everything is set up
josi doctor
```

Once installed, the `josi` command is available globally. See the [CLI Reference](#-josi-cli-reference) below for all commands.

#### 3. Start all services
```bash
# Start db, redis, and api with one command
josi redock up

# Or without the CLI:
docker-compose up -d --build
```

#### 4. Access the API
The API will be available at:
- REST API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`
- GraphQL Playground: `http://localhost:8000/graphql`

```bash
# Or use the CLI to open docs in your browser
josi open docs
josi open graphql
```

#### Manual Setup (without CLI)

<details>
<summary>Click to expand manual setup steps</summary>

**Install Poetry:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

**Install Python dependencies:**
```bash
poetry install
poetry shell
```

**Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

**Start services:**
```bash
docker-compose up -d
```

**Database migrations:**
```bash
# Migrations run automatically on startup if AUTO_DB_MIGRATION=True
# Or run manually:
poetry run alembic upgrade head
```

**Download astronomical data files:**
```bash
mkdir -p /usr/share/swisseph
cd /usr/share/swisseph
wget https://www.astro.com/ftp/swisseph/ephe/sweph_18.tar.gz
tar -xzf sweph_18.tar.gz
cd -
```

</details>

### Verifying Installation

#### 1. Check API health
```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status": "ok", "version": "..."}
```

#### 2. Create a test API key (for development)
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U josi -d josi

# Insert a test organization and API key
INSERT INTO organization (organization_id, name, api_key) 
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'Test Org', 'test-api-key');
```

#### 3. Test API with a simple request
```bash
# Create a person
curl -X POST "http://localhost:8000/api/v1/persons" \
  -H "X-API-Key: test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "date_of_birth": "1990-01-01",
    "time_of_birth": "14:30",
    "place_of_birth": "New York, NY",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
  }'
```

### Troubleshooting

#### Port already in use
```bash
# Find and kill the process using port 8000
lsof -i :8000
kill -9 <PID>
```

#### Database connection issues
```bash
# Check if PostgreSQL is running
docker-compose ps db

# View PostgreSQL logs
docker-compose logs db

# Restart PostgreSQL
docker-compose restart db
```

#### Redis connection issues
```bash
# Check if Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Expected: PONG
```

#### Module import errors
```bash
# Ensure you're in the poetry shell
poetry shell

# Set PYTHONPATH manually if needed
export PYTHONPATH="${PWD}/src"
```

### Development Tips

1. **Docker Usage**: Always use `redock` to start services - it ensures proper setup
2. **Auto-reload**: The API container has hot-reloading enabled
3. **Debugging**: Set `DEBUG=True` in `.env` for detailed error messages
4. **Database GUI**: Use pgAdmin or TablePlus to inspect the database
5. **API Testing**: Use Postman, Insomnia, or the built-in Swagger UI
6. **Logs**: Check `logs/` directory for application logs

## 📚 API Documentation

Once running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative API docs**: http://localhost:8000/redoc
- **GraphQL Playground**: http://localhost:8000/graphql

### Example API Usage

#### Create a Person
```bash
curl -X POST "http://localhost:8000/api/v1/persons" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "date_of_birth": "1990-01-15",
    "time_of_birth": "14:30",
    "place_of_birth": "New York, NY, USA",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
  }'
```

#### Calculate a Vedic Chart
```bash
curl -X POST "http://localhost:8000/api/v1/charts/calculate" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": "person-uuid-here",
    "systems": ["vedic"],
    "house_system": "placidus",
    "ayanamsa": "lahiri"
  }'
```

#### AI-Powered Chart Interpretation
```bash
curl -X POST "http://localhost:8000/api/v1/ai/interpret" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "chart_id": "chart-uuid-here",
    "question": "What does my Mars placement mean for my career?",
    "style": "psychological"
  }'
```

### GraphQL Example

```graphql
query GetPersonWithCharts($personId: UUID!) {
  person(id: $personId) {
    name
    dateOfBirth
    charts {
      chartType
      calculatedAt
      planetPositions
      houses
    }
  }
}
```

## 🏗 Architecture

### Project Structure
```
josi-svc/                      # Project root
├── src/                       # Source code
│   ├── josi/
│   │   ├── api/              # REST API endpoints
│   │   ├── graphql/          # GraphQL schema and resolvers
│   │   ├── models/           # SQLModel database models
│   │   ├── services/         # Business logic and calculations
│   │   │   ├── ai/          # AI interpretation services
│   │   │   ├── vedic/       # Vedic astrology calculations
│   │   │   ├── western/     # Western astrology calculations
│   │   │   └── chinese/     # Chinese astrology calculations
│   │   ├── repositories/     # Data access layer
│   │   ├── core/            # Core utilities and config
│   │   └── main.py          # FastAPI application
│   ├── alembic/             # Database migrations
│   ├── cache/               # Caching utilities
│   └── code_generator/      # CRUD code generation
├── tests/                    # Comprehensive test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   ├── real_world/          # Real-world scenario tests
│   ├── scripts/             # Test scripts
│   ├── validation/          # API validation tests
│   └── verification/        # Astronomical accuracy tests
├── scripts/                  # Utility scripts
│   └── utilities/           # Test coverage tools
├── test_data/               # Test data with real astronomical values
├── docs/                    # Documentation
│   ├── markdown/           # All project documentation
│   ├── conversations/      # Claude chat exports
│   └── external_apis/      # External API docs
├── logs/                    # Application logs
├── reports/                 # Generated reports
├── k8s/                     # Kubernetes manifests
├── gcp/                     # Google Cloud deployment scripts
└── docker-compose.yml       # Docker services configuration
```

### Key Design Patterns
- **Repository Pattern**: Clean separation of data access
- **Service Layer**: Business logic isolation
- **Dependency Injection**: FastAPI's dependency system
- **Multi-tenancy**: Organization-based data isolation
- **Soft Deletes**: Data recovery capability

### Directory Organization Rules
See [CLAUDE.md](CLAUDE.md) for detailed folder structure guidelines.

## 🧪 Testing

Run the comprehensive test suite:
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=josi --cov-report=html

# Run specific test categories
poetry run pytest tests/unit
poetry run pytest tests/integration
poetry run pytest tests/real_world
poetry run pytest tests/verification

# Run validation against reference data
poetry run python tests/validation/validate_our_apis.py

# Generate coverage report
poetry run python scripts/utilities/generate_coverage_report.py
```

## 🔧 Configuration

Key environment variables:
```bash
# Database
DATABASE_URL=postgresql://josi:josi@localhost:5432/josi

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
API_KEY_HEADER=X-API-Key

# Features
AUTO_DB_MIGRATION=True
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60

# OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret

# AI Features (optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## 🚢 Deployment

### Google Cloud Platform

#### Option 1: Cloud Run (Serverless)
```bash
gcloud builds submit --config=cloudbuild.yaml
```

#### Option 2: Google Kubernetes Engine
```bash
cd gcp
./deploy.sh YOUR_PROJECT_ID
```

See [docs/markdown/DEPLOYMENT_GCP.md](docs/markdown/DEPLOYMENT_GCP.md) for detailed instructions.

### Docker
```bash
docker build -t josi-api .
docker run -p 8000:8000 --env-file .env josi-api
```

## 📊 Performance

- **Caching**: Redis-based caching with automatic invalidation
- **Async**: Full async/await support with asyncpg
- **Connection Pooling**: Optimized database connections
- **Response Compression**: Automatic GZIP compression
- **Horizontal Scaling**: Stateless design for easy scaling

## 🔒 Security

- **Authentication**: JWT tokens and API keys
- **Authorization**: Role-based access control
- **Rate Limiting**: Configurable per-tier limits
- **Input Validation**: Pydantic models with strict validation
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy
- **XSS Prevention**: Automatic output escaping
- **CORS**: Configurable cross-origin policies
- **Security Headers**: HSTS, CSP, X-Frame-Options

## 📝 API Endpoints

### Core Features
- **Authentication**: User registration, login, OAuth2
- **Person Management**: CRUD operations for birth data
- **Chart Calculations**: Multiple astrology systems
- **AI Interpretations**: GPT-4 and Claude powered insights
- **Astrologer Marketplace**: Professional consultations
- **Remedy Engine**: Personalized recommendations
- **Transit Monitoring**: Real-time planetary tracking

For complete API documentation, see the interactive docs at http://localhost:8000/docs

## 🚀 Recent Updates

### Version 2.1 (January 2025)
- **Improved Accuracy**: Enhanced planetary calculations with better timezone handling
- **Time Format Flexibility**: API now accepts AM/PM time formats
- **Better Organization**: Reorganized project structure for clarity
- **Enhanced Testing**: Validation against VedicAstroAPI reference data
- **Auto Migrations**: Database migrations run automatically on startup
- **Documentation Updates**: Comprehensive CLAUDE.md for AI assistants

### Version 2.0 (January 2025)
- **AI Marketplace Integration**: Professional astrologer platform
- **Real-time Consultations**: WebSocket support
- **Enhanced Testing**: 90% test coverage
- **Remedy Engine**: AI-powered recommendations
- **Transit Monitoring**: Real-time tracking

## 🛠 Josi CLI Reference

The Josi CLI (`cli/` directory) is a TypeScript developer toolkit that consolidates all common workflows into a single command.

### Installation
```bash
cd josi-svc/cli
npm install && npm run build && npm link
```

### Commands

| Command | Description |
|---------|-------------|
| `josi init` | Bootstrap your dev machine (installs Python, Poetry, Docker, etc.) |
| `josi doctor` | Health check — verify tools, Docker, ports, project files |
| `josi redock up` | Start all services (db, redis, api) with Docker Compose |
| `josi redock up --no-build` | Start without rebuilding the API image |
| `josi redock up --vector` | Also start Qdrant vector database |
| `josi redock status` | Show running container status |
| `josi redock logs [service]` | Follow container logs (e.g., `josi redock logs api`) |
| `josi redock clean` | Stop containers |
| `josi redock clean -v` | Stop containers and remove volumes (fresh DB) |
| `josi db migrate "<msg>"` | Auto-generate Alembic migration with conflict detection |
| `josi db upgrade` | Apply all pending migrations |
| `josi db downgrade <rev>` | Downgrade to a specific revision |
| `josi db rollback` | Undo the last migration |
| `josi test` | Run all tests |
| `josi test --unit` | Run unit tests only |
| `josi test --coverage` | Run with HTML coverage report |
| `josi test -k "pattern"` | Filter tests by keyword |
| `josi lint` | Check code quality (black, flake8, mypy) |
| `josi lint --fix` | Auto-format with black |
| `josi crud <model> -m <name>` | Generate CRUD scaffolding |
| `josi open [docs\|graphql\|redoc]` | Open API docs in browser |
| `josi status` | Development environment dashboard |
| `josi services` | List all services with ports and status |
| `josi env check` | Validate .env has all required variables |
| `josi env setup` | Create .env from .env.example |
| `josi nuke` | Kill everything — containers, volumes, prune Docker |
| `josi update` | Self-update the CLI (git pull + rebuild) |

### Updating the CLI
```bash
josi update
# Or manually:
cd josi-svc/cli && git pull && npm install && npm run build
```

## 🙏 Acknowledgments

- [Swiss Ephemeris](https://www.astro.com/swisseph/) for astronomical calculations
- [Skyfield](https://rhodesmill.org/skyfield/) for modern astronomical computations
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [VedicAstroAPI](https://vedicastroapi.com/) for reference data validation
- The astrology community for calculation methods and validation

## 📞 Support

- **Documentation**: See `docs/markdown/` folder
- **Issues**: [GitHub Issues](https://github.com/josi-ai/josi-svc/issues)
- **Discussions**: [GitHub Discussions](https://github.com/josi-ai/josi-svc/discussions)

---

Built with ❤️ by the Josi team