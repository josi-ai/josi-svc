# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Product Vision

Josi is a **full-stack, multi-tradition astrology platform** — both a direct-to-consumer product and a B2B API. It rests on three pillars:

1. **Calculation Engine**: High-precision astronomical calculations across six traditions (Vedic, Western, Chinese, Hellenistic, Mayan, Celtic) — all treated as equally important. Built on Swiss Ephemeris (pyswisseph) and Skyfield. The goal is to be the most comprehensive multi-tradition calculation engine available.

2. **AI-Powered Guidance** (central differentiator): LLM-powered interpretations (GPT-4/Claude) that transform chart data into personalized guidance. Five interpretation styles. "Neural Pathway Questions" use chart placements to generate psychological self-reflection prompts that build on previous responses. Vector similarity (Qdrant) finds charts with similar patterns.

3. **Astrologer Marketplace** (near-term priority): Connects users with verified professional astrologers for video/chat/email/voice consultations. Includes booking, payments (Stripe), multi-dimensional reviews, and AI-generated post-consultation summaries.

**Business model**: B2B API-as-a-Service (multi-tenant, API key auth) + B2C subscription tiers (Free/Explorer/Mystic/Master) with chart, AI interpretation, and consultation quotas.

**Target audience**: Global users across all traditions, Indian diaspora and Tamil-speaking communities, professional astrologers, and developers needing a calculation API.

For full detail see `docs/markdown/PRODUCT_VISION.md`.

## IMPORTANT: Always Use Docker

**ALWAYS run the application using Docker Compose with the `redock` alias.** Never run the server directly with uvicorn or python commands.

```bash
redock                    # Start all services (db, redis, api) with rebuild
docker-compose up -d      # Start without rebuild
docker-compose down        # Stop all services
```

The API runs at `http://localhost:8000`. Docs at `/docs`, GraphQL at `/graphql`.

## Development Commands

```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest

# Run a single test file
poetry run pytest tests/unit/services/test_astrology_service.py

# Run a specific test by name
poetry run pytest -k "test_vedic_chart" -v

# Format / lint / type-check
poetry run black src/
poetry run flake8 src/
poetry run mypy src/

# Database migrations (NEVER hand-write migrations - always autogenerate)
poetry run alembic revision --autogenerate -m "description"
poetry run alembic upgrade head
poetry run alembic downgrade -1

# CRUD scaffolding for a new model
poetry run generate-crud josi.models.{file}.{Model} --module {name}
# Example: poetry run generate-crud josi.models.person_model.Person --module person
```

## Keep the Root Directory Clean

Generated files go in their proper directories:
- `logs/` for `.log` files
- `reports/` for JSON reports and analysis results
- `scripts/` for utility/debug scripts
- `docs/markdown/` for project documentation
- `test_data/` for test data and validation results

Do NOT place log files, temp files, generated reports, or debug outputs in the project root.

## Architecture

Josi is an astrology calculation API (Vedic, Western, Chinese, Hellenistic, Mayan, Celtic) built with FastAPI, SQLModel, and PostgreSQL. Multi-tenant with REST + GraphQL interfaces.

### Request Flow

```
HTTP Request → Middleware (CORS, GZip, RateLimit, Security, Logging)
  → Controller (src/josi/api/v1/controllers/)
    → Service (src/josi/services/)
      → Repository (src/josi/repositories/)
        → AsyncSession (src/josi/db/async_db.py)
          → PostgreSQL
```

### Layer Responsibilities

- **Controllers** (`api/v1/controllers/`): HTTP handling, request validation, `ResponseModel` wrapping. Use dependency-injected services via `Annotated` type aliases (e.g., `PersonServiceDep`, `ChartServiceDep`) defined in `api/v1/dependencies.py`.
- **Services** (`services/`): Business logic. No direct DB access. Key services: `AstrologyCalculator` (Swiss Ephemeris engine), `ChartService` (orchestrates calculations), `PersonService`, `GeocodingService`.
- **Repositories** (`repositories/`): DB operations via `BaseRepository[T]`. Auto-applies tenant filtering (`organization_id`) and soft-delete filtering (`is_deleted == False`).
- **Models** (`models/`): SQLModel entities + Strawberry GraphQL schemas in the same file. Inherit from `TenantBaseModel` (adds `organization_id`) or `SQLBaseModel` (timestamps + soft delete).

### Key Architectural Details

**Database**: The real async DB module is `src/josi/db/async_db.py` (NOT `src/josi/core/database.py` which is a test stub yielding `None`). Uses `EngineManager` with `asyncpg` driver. Session via `get_async_db()` dependency.

**Authentication**: API key via `X-API-Key` header → `get_current_organization()` dependency resolves organization context. All tenant data is isolated by `organization_id`.

**Caching**: Redis with `@cache(expire=3600, prefix="module_name")` decorator. `CacheInvalidator` handles model-specific cache busting. Falls back gracefully if Redis is unavailable.

**Astrology Engine** (`services/astrology_service.py`): Core calculation engine using `pyswisseph`. Computes sidereal houses, planet positions (including Ketu as Rahu + 180°), nakshatras, and delegates to sub-calculators: `PanchangCalculator`, `DasaCalculator`, `DivisionalChartsCalculator`, `StrengthCalculator`, `BhavaCalculator`.

**CRUD Generator** (`src/code_generator/`): Jinja2-based scaffolding that generates controller, service, repository, and GraphQL schema from a SQLModel class.

### Database Conventions

- Primary keys: `{table}_id` (UUID), e.g., `person_id`, `chart_id`
- All tables (except Organization) have `organization_id` for multi-tenancy
- Soft delete: `is_deleted` (bool) + `deleted_at` (timestamp) on all tables
- Timestamps: `created_at`, `updated_at` (auto-managed)
- Migrations: `src/alembic/` with `alembic.ini` at project root

### API Response Format

All REST endpoints return:
```python
{"success": bool, "message": str, "data": Any, "errors": Optional[List[str]]}
```

### Route Registration

Routes are registered in `src/josi/api/v1/__init__.py` under prefix `/api/v1`. Key endpoints: `/persons`, `/charts`, `/panchang`, `/compatibility`, `/transits`, `/dasha`, `/predictions`, `/remedies`, `/location`, `/auth`, `/ai`, `/astrologers`, `/consultations`, `/muhurta`, `/health`, `/oauth`.

GraphQL is mounted at `/graphql` with merged schema (Organization + Person + Chart).

## Adding a New Model

1. Create model in `src/josi/models/` inheriting from `TenantBaseModel`
2. Use `{table}_id` as primary key name (UUID)
3. Run CRUD generator: `poetry run generate-crud josi.models.{file}.{Model} --module {name}`
4. Add router to `src/josi/api/v1/__init__.py`
5. Update GraphQL schema in `src/josi/graphql/router.py`
6. Generate migration: `poetry run alembic revision --autogenerate -m "Add {model}"`
7. Apply: `poetry run alembic upgrade head`

## Dependencies

- Python 3.12+, FastAPI 0.115.x, SQLModel 0.0.22, Pydantic ~2.9.0
- Strawberry GraphQL 0.243.x (pinned Pydantic 2.9.x for compatibility)
- PostgreSQL 16 (uuid-ossp extension), Redis 7
- pyswisseph for astronomical calculations, skyfield for modern data
- Poetry for dependency management

## Frontend Conventions (MUST FOLLOW)

### File Size & Component Rules
- **Max 300 lines per file.** If a page exceeds this, extract sub-components into the same directory or `components/`.
- **One component per file.** No multiple exported components sharing state.
- **No god components.** If a component has 3+ tabs, each tab is its own file.

### Type Safety
- **NEVER use `<any>` for API responses.** Define typed interfaces in `web/types/` and use them: `apiClient.get<Person[]>(...)`.
- **Centralized types only.** All shared types (Person, Chart, PlanetData, etc.) live in `web/types/`. Do NOT redefine types in page files.
- **Validate API responses in `queryFn`.** Transform and extract the data inside `queryFn` so the component only sees clean, typed data:
  ```typescript
  // GOOD: transform in queryFn
  const { data: astrologers = [] } = useQuery<Astrologer[]>({
    queryFn: async () => {
      const res = await apiClient.get<any>('/api/v1/astrologers/search');
      return Array.isArray(res.data?.astrologers) ? res.data.astrologers : [];
    },
  });

  // BAD: transform after query
  const { data } = useQuery({ queryFn: () => apiClient.get<any>('/api/v1/...') });
  const items = data?.data?.items || data?.data || []; // fragile
  ```

### Styling Rules
- **CSS variables for ALL colors.** No hardcoded hex values like `#3B82F6`. Use `var(--blue)`, `var(--gold)`, etc. from `globals.css`.
- **Tailwind for layout** (flex, grid, padding, margin, responsive).
- **CSS variables for theming** (colors, borders, shadows, typography).
- **Inline styles ONLY for truly dynamic values** (calculated positions, conditional backgrounds based on data).
- **No inline styles for common patterns.** If you write the same `style={{...}}` more than twice, extract it to a component or Tailwind class.

### Widget System
- Widget components live in `web/components/dashboard/widgets/`.
- Each widget gets `{ onRemove: () => void }` as props.
- Data fetching happens inside `queryFn` with proper typing — NOT after the query.
- Use `useDefaultProfile()` for user location/profile data.
- Widget types defined in `web/config/widget-config.ts`.
- **After changing widget config, bump `CURRENT_VERSION` in `web/hooks/use-widget-layout.ts`** to invalidate stale localStorage.

### Dashboard Layout
- The entire `(dashboard)` route group renders client-only via `DashboardShell` (no SSR).
- This prevents hydration mismatches. Do NOT add SSR to dashboard pages.
- Public pages (landing, pricing, chart-calculator) DO use SSR.

### Error Handling
- Widget errors are caught by `WidgetErrorBoundary` in `widget-grid.tsx`.
- API 401 errors only redirect to login if a token was actually sent (not during auth initialization).
- API errors in widgets should show graceful fallback UI, not crash.

### Database Import (Backend)
- **ALWAYS use `from josi.db.async_db import get_async_db as get_db`**.
- **NEVER use `from josi.core.database import get_db`** — that's a test stub that returns `None`.

### Development Workflow
- After changing widget-grid.tsx or widget imports, **restart the dev server** — Turbopack can't HMR class-based error boundaries or module-level dynamic imports.
- The `josi redock up dev --local` CLI auto-kills port 1989 and sets `NODE_OPTIONS=--max-old-space-size=4096`.
- Clear `.next` cache if you see "(stale)" in the Next.js error overlay.

## Deployment

- Docker Compose for local dev (PostgreSQL, Redis, API with hot reload)
- `AUTO_DB_MIGRATION=True` runs Alembic on startup in Docker
- Swiss Ephemeris data files at `EPHEMERIS_PATH` (defaults to `/usr/share/swisseph`)
- See `.env.example` for all environment variables
