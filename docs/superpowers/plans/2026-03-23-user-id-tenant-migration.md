# User-ID Tenant Migration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `organization_id`-based multi-tenancy with `user_id`-based filtering. Add `user_id` column to all tenant models, make `organization_id` nullable, filter all queries by `user_id`, remove the `resolve_organization_id` dependency, and migrate existing data.

**Architecture:** The `TenantBaseModel` currently requires `organization_id` (NOT NULL FK). We add a `user_id` column (nullable FK to `users.user_id`) alongside it, make `organization_id` nullable, then update `BaseRepository` to filter by `user_id` instead. Services receive `user_id` from `CurrentUser` directly — no org lookup needed. The `Organization` model and table remain in the DB but are no longer used for tenant isolation.

**Tech Stack:** Python 3.12, FastAPI, SQLModel, Alembic (autogenerate), PostgreSQL 16, asyncpg.

**Important:**
- NEVER hand-write Alembic migrations — always use `alembic revision --autogenerate`
- Run Alembic inside the Docker container: `docker-compose exec web alembic revision --autogenerate -m "message"`
- The `users` table may be empty if Clerk metadata fast-path is used. The migration must handle this.
- `CurrentUser.user_id` comes from Clerk JWT claims (`josi_user_id`), NOT from the `users` DB table directly.

---

## File Structure

### Files to modify:
| File | Change |
|------|--------|
| `src/josi/models/base.py` | Add `user_id` to `TenantBaseModel`, make `organization_id` nullable |
| `src/josi/repositories/base_repository.py` | Filter by `user_id` instead of `organization_id`; fix `get()` PK resolution |
| `src/josi/api/v1/dependencies.py` | Remove `resolve_organization_id`, pass `user_id` to services |
| `src/josi/services/person_service.py` | Change constructor from `organization_id` to `user_id` |
| `src/josi/services/chart_service.py` | Change constructor from `organization_id` to `user_id` |
| `src/josi/repositories/person_repository.py` | Update any custom queries that reference `organization_id` |

### Files to NOT modify:
- Stateless calculator services (AstrologyCalculator, PanchangCalculator, etc.) — no tenant context
- `src/josi/models/organization_model.py` — keep Organization model as-is
- `src/josi/auth/` — CurrentUser already has `user_id`

---

## Task 1: Update TenantBaseModel — add `user_id`, make `organization_id` nullable

**Files:**
- Modify: `src/josi/models/base.py`

- [ ] **Step 1: Update `TenantBaseModel`**

```python
class TenantBaseModel(SQLBaseModel):
    """Base model for user-scoped entities."""

    user_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        index=True,
        foreign_key="users.user_id"
    )

    organization_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        index=True,
        foreign_key="organization.organization_id"
    )
```

Key changes:
- `organization_id` changes from `UUID` (NOT NULL) to `Optional[UUID]` (nullable)
- New `user_id` field added with FK to `users.user_id`, nullable (for migration), indexed

- [ ] **Step 2: Generate Alembic migration**

Run inside Docker:
```bash
docker-compose exec josi-api alembic revision --autogenerate -m "Add user_id to tenant models, make organization_id nullable"
```

If the API container doesn't have alembic CLI, run from host:
```bash
cd /Users/govind/Developer/josi/josi-svc && poetry run alembic revision --autogenerate -m "Add user_id to tenant models, make organization_id nullable"
```

- [ ] **Step 3: Review the generated migration**

Check `src/alembic/versions/` for the new migration file. Verify it:
- Adds `user_id` column (UUID, nullable, indexed, FK to users.user_id) to: `person`, `astrology_chart`, `planet_position`, `chart_interpretation`, `interpretation_embedding`
- Alters `organization_id` to be nullable on those same tables
- Does NOT drop `organization_id`

- [ ] **Step 4: Apply migration**

```bash
docker-compose exec josi-api alembic upgrade head
```
Or from host: `poetry run alembic upgrade head`

- [ ] **Step 5: Migrate existing data**

The existing rows have `organization_id` set but `user_id` is NULL. We need to resolve the user_id from the organization slug pattern `user-{user_id}`.

Run this SQL directly:
```sql
-- Extract user_id from organization.slug (format: 'user-{uuid}')
UPDATE person p
SET user_id = CAST(REPLACE(o.slug, 'user-', '') AS UUID)
FROM organization o
WHERE p.organization_id = o.organization_id
AND o.slug LIKE 'user-%'
AND p.user_id IS NULL;

UPDATE astrology_chart c
SET user_id = CAST(REPLACE(o.slug, 'user-', '') AS UUID)
FROM organization o
WHERE c.organization_id = o.organization_id
AND o.slug LIKE 'user-%'
AND c.user_id IS NULL;

UPDATE planet_position pp
SET user_id = CAST(REPLACE(o.slug, 'user-', '') AS UUID)
FROM organization o
JOIN astrology_chart c ON c.chart_id = pp.chart_id
WHERE pp.organization_id = o.organization_id
AND o.slug LIKE 'user-%'
AND pp.user_id IS NULL;

UPDATE chart_interpretation ci
SET user_id = CAST(REPLACE(o.slug, 'user-', '') AS UUID)
FROM organization o
JOIN astrology_chart c ON c.chart_id = ci.chart_id
WHERE ci.organization_id = o.organization_id
AND o.slug LIKE 'user-%'
AND ci.user_id IS NULL;
```

Run via: `docker exec josi-db psql -U josi -d josi -c "<SQL>"`

- [ ] **Step 6: Verify migration**

```bash
docker exec josi-db psql -U josi -d josi -c "SELECT person_id, user_id, organization_id FROM person;"
docker exec josi-db psql -U josi -d josi -c "SELECT chart_id, user_id, organization_id FROM astrology_chart;"
```

All rows should have `user_id` populated.

- [ ] **Step 7: Commit**

```bash
git add src/josi/models/base.py src/alembic/versions/
git commit -m "feat: add user_id to tenant models, make organization_id nullable"
```

---

## Task 2: Update BaseRepository — filter by `user_id`

**Files:**
- Modify: `src/josi/repositories/base_repository.py`

- [ ] **Step 1: Update constructor to accept `user_id`**

Change `__init__` signature:
```python
def __init__(self, model: Type[ModelType], session: AsyncSession, user_id: Optional[UUID] = None):
    self.model = model
    self.session = session
    self.user_id = user_id
    self.is_user_scoped = hasattr(model, 'user_id')
```

- [ ] **Step 2: Replace `_apply_tenant_filter` with user-based filtering**

```python
def _apply_tenant_filter(self, query):
    """Apply user_id filter if model supports user scoping."""
    if self.is_user_scoped and self.user_id:
        return query.where(self.model.user_id == self.user_id)
    return query
```

- [ ] **Step 3: Fix `get()` method PK resolution**

The current `get()` tries `{tablename}_id` which fails for `astrology_chart` (PK is `chart_id`, not `astrology_chart_id`). Replace the PK resolution with SQLAlchemy's inspect:

```python
async def get(self, id: UUID) -> Optional[ModelType]:
    """Get a single record by ID."""
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(self.model)
    pk_columns = mapper.primary_key
    if not pk_columns:
        raise ValueError(f"No primary key found for {self.model.__name__}")

    id_field = pk_columns[0]

    conditions = [id_field == id]
    if hasattr(self.model, 'is_deleted'):
        conditions.append(self.model.is_deleted == False)

    query = select(self.model).where(and_(*conditions))
    query = self._apply_tenant_filter(query)

    result = await self.session.execute(query)
    return result.scalar_one_or_none()
```

- [ ] **Step 4: Update `create()` to set `user_id` instead of `organization_id`**

```python
async def create(self, obj_in: Dict[str, Any]) -> ModelType:
    """Create a new record."""
    if self.is_user_scoped and self.user_id:
        obj_in["user_id"] = self.user_id

    db_obj = self.model(**obj_in)
    self.session.add(db_obj)
    await self.session.flush()
    await self.session.refresh(db_obj)
    return db_obj
```

- [ ] **Step 5: Update `bulk_create()` similarly**

Replace `organization_id` with `user_id` in the bulk_create loop.

- [ ] **Step 6: Update `update()` — prevent user_id from being changed**

In the update method, add `user_id` to the protected fields:
```python
if hasattr(entity, field) and field not in ['id', 'created_at', 'organization_id', 'user_id']:
```

- [ ] **Step 7: Commit**

```bash
git add src/josi/repositories/base_repository.py
git commit -m "feat: switch BaseRepository from organization_id to user_id filtering"
```

---

## Task 3: Update Dependencies — remove org resolution, pass `user_id`

**Files:**
- Modify: `src/josi/api/v1/dependencies.py`

- [ ] **Step 1: Remove `resolve_organization_id` and `OrgIdDep`**

Delete the entire `resolve_organization_id` function, the `OrgIdDep` type alias, and the `Organization` import.

- [ ] **Step 2: Update service factories to pass `current_user.user_id`**

```python
async def get_person_service(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: CurrentUserDep,
) -> PersonService:
    return PersonService(db, current_user.user_id)


async def get_chart_service(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: CurrentUserDep,
) -> ChartService:
    return ChartService(db, current_user.user_id)
```

- [ ] **Step 3: Clean up imports**

Remove: `from uuid import UUID`, `from sqlalchemy import select`, `from josi.models.organization_model import Organization`

- [ ] **Step 4: Commit**

```bash
git add src/josi/api/v1/dependencies.py
git commit -m "feat: remove org dependency, pass user_id directly to services"
```

---

## Task 4: Update Services — `organization_id` → `user_id`

**Files:**
- Modify: `src/josi/services/person_service.py`
- Modify: `src/josi/services/chart_service.py`
- Modify: `src/josi/repositories/person_repository.py`

- [ ] **Step 1: Update `PersonService.__init__`**

```python
def __init__(self, db: AsyncSession, user_id: UUID):
    self.db = db
    self.user_id = user_id
    self.person_repo = PersonRepository(Person, db, user_id)
    self.geocoding_service = GeocodingService()
```

Also update any method that references `self.organization_id` to use `self.user_id`.

- [ ] **Step 2: Update `PersonService.get_person_charts`**

Change the query filter from `organization_id` to `user_id`:
```python
if self.user_id:
    query = query.where(AstrologyChart.user_id == self.user_id)
```

- [ ] **Step 3: Update `PersonService.list_persons`**

If it references `self.organization_id`, change to `self.user_id`.

- [ ] **Step 4: Update `ChartService.__init__`**

```python
def __init__(self, db: AsyncSession, user_id: UUID):
    self.db = db
    self.user_id = user_id
    self.chart_repo = ChartRepository(AstrologyChart, db, user_id)
    # ... rest of init stays the same
```

Also update any method that references `self.organization_id`.

- [ ] **Step 5: Update `PersonRepository` constructor and custom queries**

Change `__init__` to accept `user_id` instead of `organization_id`, pass to `super().__init__`. Update any custom queries that filter by `organization_id` to filter by `user_id`.

- [ ] **Step 6: Update `ChartRepository` in person_repository.py**

Same changes as PersonRepository.

- [ ] **Step 7: Search for any remaining `organization_id` references in services/repos**

```bash
grep -rn "organization_id" src/josi/services/ src/josi/repositories/ --include="*.py" | grep -v "__pycache__"
```

Fix any remaining references.

- [ ] **Step 8: Commit**

```bash
git add src/josi/services/ src/josi/repositories/
git commit -m "feat: switch services and repositories from organization_id to user_id"
```

---

## Task 5: Restart and verify end-to-end

- [ ] **Step 1: Restart the API**

```bash
docker restart josi-api
```

- [ ] **Step 2: Test person creation via browser**

Navigate to `http://localhost:1989/charts` — should load without errors.

- [ ] **Step 3: Test chart calculation**

Use browser evaluate to create a person + calculate a chart (same flow as E2E test).

- [ ] **Step 4: Verify data in DB**

```bash
docker exec josi-db psql -U josi -d josi -c "SELECT person_id, user_id, organization_id FROM person;"
docker exec josi-db psql -U josi -d josi -c "SELECT chart_id, user_id, organization_id FROM astrology_chart;"
```

New rows should have `user_id` populated, `organization_id` should be NULL.

- [ ] **Step 5: Commit all remaining changes**

```bash
git add -A
git commit -m "feat: complete user_id tenant migration — org_id no longer used for filtering"
```
