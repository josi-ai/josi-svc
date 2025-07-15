# Astrow - Professional Astrology Calculation API

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](https://github.com/yourusername/josi/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Astrow (formerly Josi) is a production-ready, multi-tenant astrology calculation API that supports multiple astrological systems with enterprise-grade security, performance, and scalability. Built with FastAPI, it provides both REST and GraphQL interfaces for comprehensive astrological calculations with AI-powered interpretations.

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
- Docker & Docker Compose (optional)

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/josi.git
cd josi
```

2. **Install dependencies**
```bash
pip install poetry
poetry install
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start services with Docker Compose**
```bash
# Start core services (PostgreSQL, Redis)
docker-compose up -d

# Start vector database for AI features (optional)
docker-compose -f docker-compose.vector.yml up -d
```

5. **Run database migrations**
```bash
poetry run alembic upgrade head
```

6. **Start the development server**
```bash
poetry run uvicorn josi.main:app --reload
```

The API will be available at `http://localhost:8000`

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
    "time_of_birth": "14:30:00",
    "place_of_birth": "New York, NY, USA",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York"
  }'
```

#### Calculate a Vedic Chart
```bash
curl -X POST "http://localhost:8000/api/v1/persons/{person_id}/charts" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "chart_type": "vedic",
    "house_system": "whole_sign",
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

#### Generate Neural Pathway Questions
```bash
curl -X POST "http://localhost:8000/api/v1/ai/neural-pathway" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "chart_id": "chart-uuid-here",
    "focus_area": "relationships"
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

## 🔐 Authentication

### OAuth2 Integration
Josi supports OAuth2 authentication with:
- Google
- GitHub

To enable OAuth:
1. Set up OAuth apps with providers
2. Add credentials to environment variables:
```bash
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-secret
```

### API Key Authentication
For programmatic access, use API keys:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/persons
```

## 🏗 Architecture

```
josi/
├── src/
│   └── josi/
│       ├── api/           # REST API endpoints
│       ├── graphql/       # GraphQL schema and resolvers
│       ├── models/        # SQLModel database models
│       ├── services/      # Business logic and calculations
│       │   ├── ai/       # AI interpretation services
│       │   ├── vedic/    # Vedic astrology calculations
│       │   ├── western/  # Western astrology calculations
│       │   └── chinese/  # Chinese astrology calculations
│       ├── repositories/  # Data access layer
│       ├── core/          # Core utilities and config
│       └── main.py        # FastAPI application
├── tests/                 # Comprehensive test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── real_world/       # Real-world scenario tests
│   └── verification/     # Astronomical accuracy tests
├── scripts/              # Utility scripts
│   ├── collect_vedicastro_test_data.py
│   ├── validate_our_endpoints.py
│   └── validate_against_vedicastro.py
├── test_data/            # Test data with real astronomical values
├── docs/                 # Additional documentation
│   └── markdown/         # All project documentation
├── k8s/                  # Kubernetes manifests
└── gcp/                  # Google Cloud deployment scripts
```

### Key Design Patterns
- **Repository Pattern**: Clean separation of data access
- **Service Layer**: Business logic isolation
- **Dependency Injection**: FastAPI's dependency system
- **Multi-tenancy**: Organization-based data isolation
- **Soft Deletes**: Data recovery capability

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

See [DEPLOYMENT_GCP.md](DEPLOYMENT_GCP.md) for detailed instructions.

### Docker
```bash
docker build -t josi-api .
docker run -p 8000:8000 --env-file .env josi-api
```

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
poetry run python scripts/validate_our_endpoints.py

# Generate coverage report
poetry run python generate_coverage_report.py
```

## 🔧 Configuration

Key environment variables:
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/josi

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
API_KEY_HEADER=X-API-Key

# OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret

# Features
AUTO_DB_MIGRATION=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 🧪 Testing & Validation

Astrow uses a comprehensive testing strategy with real astronomical data:

### Test Coverage
- **90%+ code coverage** with 500+ tests
- **Real astronomical data** from VedicAstroAPI for validation
- **Accuracy verification** against multiple astronomical sources
- **Performance benchmarks** for calculation speed

### Validation Framework
```bash
# Run validation against reference data
poetry run python scripts/validate_our_endpoints.py

# Collect test data from VedicAstroAPI
poetry run python scripts/collect_vedicastro_test_data.py

# Generate accuracy reports
poetry run python scripts/validate_against_vedicastro.py
```

## 📝 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login with credentials
- `POST /api/v1/auth/token` - OAuth2 token endpoint
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/auth/me` - Get current user info

### AI Features
- `POST /api/v1/ai/interpret` - Generate AI interpretation
- `POST /api/v1/ai/neural-pathway` - Generate psychological questions
- `GET /api/v1/ai/styles` - List interpretation styles
- `GET /api/v1/ai/providers` - List AI providers

### Person Management
- `POST /api/v1/persons` - Create a person
- `GET /api/v1/persons` - List persons
- `GET /api/v1/persons/{id}` - Get person details
- `PATCH /api/v1/persons/{id}` - Update person
- `DELETE /api/v1/persons/{id}` - Delete person

### Chart Calculations
- `POST /api/v1/persons/{id}/charts` - Calculate chart
- `GET /api/v1/persons/{id}/charts` - List person's charts
- `GET /api/v1/charts/{id}` - Get chart details
- `GET /api/v1/charts/{id}/interpretations` - Get interpretations

### Vedic Astrology
- `GET /api/v1/panchang` - Current Panchang
- `POST /api/v1/compatibility` - Ashtakoota compatibility
- `GET /api/v1/dasha/{chart_id}` - Vimshottari Dasha periods
- `POST /api/v1/muhurta` - Auspicious timings

### Western Astrology
- `POST /api/v1/progressions` - Secondary progressions
- `POST /api/v1/transits` - Current transits
- `POST /api/v1/synastry` - Relationship analysis

### Astrologer Marketplace
- `GET /api/v1/astrologers` - List professional astrologers
- `GET /api/v1/astrologers/{id}` - Get astrologer profile
- `POST /api/v1/consultations` - Book consultation
- `GET /api/v1/consultations/{id}` - Get consultation details
- `WS /api/v1/consultations/{id}/chat` - Real-time consultation chat

### Remedies & Recommendations
- `GET /api/v1/remedies/{chart_id}` - Get personalized remedies
- `POST /api/v1/remedies/gemstones` - Gemstone recommendations
- `POST /api/v1/remedies/mantras` - Mantra recommendations
- `POST /api/v1/remedies/rituals` - Ritual suggestions

### Transit Monitoring
- `POST /api/v1/transits/monitor` - Set up transit alerts
- `GET /api/v1/transits/current` - Current planetary transits
- `GET /api/v1/transits/upcoming` - Upcoming significant transits

### OAuth Authentication
- `GET /api/v1/oauth/providers` - List available OAuth providers
- `GET /api/v1/oauth/login/{provider}` - Initiate OAuth flow
- `GET /api/v1/oauth/callback/{provider}` - OAuth callback

### Utilities
- `POST /api/v1/location/geocode` - Geocode location
- `GET /api/v1/location/timezone` - Get timezone
- `GET /api/v1/health` - Health check
- `GET /api/v1/health/ready` - Readiness check
- `GET /api/v1/health/live` - Liveness check

## 🐛 Known Issues

- Swiss Ephemeris data files must be available at `/usr/share/swisseph`
- Timezone detection requires internet connection for geocoding
- Some Vedic calculations may have minor variations from traditional methods

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Recent Updates

### Version 2.0 (January 2025)
- **AI Marketplace Integration**: Added support for professional astrologers
- **Real-time Consultations**: WebSocket support for live sessions
- **Enhanced Testing**: 90% test coverage with real astronomical data validation
- **VedicAstroAPI Integration**: Reference data collection for accuracy verification
- **Remedy Engine**: AI-powered personalized remedy recommendations
- **Transit Monitoring**: Real-time planetary movement tracking
- **Documentation Reorganization**: All docs moved to `docs/markdown/`
- **Performance Improvements**: Optimized calculation algorithms

## 🙏 Acknowledgments

- [Swiss Ephemeris](https://www.astro.com/swisseph/) for astronomical calculations
- [Skyfield](https://rhodesmill.org/skyfield/) for modern astronomical computations
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [VedicAstroAPI](https://vedicastroapi.com/) for reference data validation
- The astrology community for calculation methods and validation

## 📞 Support

- **Documentation**: See `/docs` folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/josi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/josi/discussions)

---

Built with ❤️ by the Josi team