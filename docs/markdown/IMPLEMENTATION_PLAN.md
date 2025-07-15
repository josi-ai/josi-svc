# Astrow API Implementation Plan

## Phase 1: Database & Architecture Refactoring

### 1.1 UUID Migration
- Add UUID extension to PostgreSQL
- Create new models with UUID primary keys
- Add organization_id to all tables for multi-tenancy
- Create migration scripts

### 1.2 Async Database Layer
- Replace SQLAlchemy with SQLModel + asyncpg
- Implement async repository pattern
- Create async session management

### 1.3 Architecture Pattern
- **Controllers**: FastAPI endpoints (thin layer)
- **Services**: Business logic (calculations, validations)
- **Repositories**: Database access layer
- **Models**: Domain models
- **DTOs**: Data transfer objects

## Phase 2: Multi-tenancy Implementation

### 2.1 Organization Model
```python
- id: UUID
- name: str
- slug: str (unique)
- api_key: str
- settings: JSON
- created_at: datetime
- updated_at: datetime
```

### 2.2 Update All Models
- Add organization_id: UUID to all tables
- Add composite indexes for performance
- Implement row-level security

## Phase 3: Complete Astrology Implementations

### 3.1 Vedic Astrology
- **Panchang**: Calculate tithi, nakshatra, yoga, karana using Swiss Ephemeris
- **Ashtakoota**: Implement full guna matching algorithm
- **Vimshottari Dasha**: Calculate based on Moon nakshatra at birth
- **Muhurta**: Find auspicious times based on panchang elements
- **Divisional Charts**: D1-D60 calculations

### 3.2 Chinese Astrology
- **Four Pillars**: Accurate calculation using Chinese solar calendar
- **Day Master**: Calculate day stem/branch using 60-year cycle
- **Luck Pillars**: 10-year cycles based on birth chart
- **Flying Stars**: Time-based feng shui calculations

### 3.3 Western Astrology
- **Progressions**: Secondary, solar arc, primary directions
- **Returns**: Solar, lunar, planetary returns
- **Composite Charts**: Relationship midpoint calculations
- **Harmonic Charts**: Divisional harmonics

### 3.4 Other Systems
- **Hellenistic**: Zodiacal releasing, annual profections, time lords
- **Mayan**: Accurate Tzolkin/Haab calculations with Long Count
- **Celtic**: Full Ogham system with lunar months

## Phase 4: Calculation Services

### 4.1 Core Calculations
- Transit engine for real-time positions
- Aspect calculator with orbs
- House system implementations (10+ systems)
- Ayanamsa calculations (15+ systems)

### 4.2 Prediction Engine
- Rule-based prediction system
- Transit interpretation database
- Dasha/bhukti interpretation rules
- Multi-language support

### 4.3 Compatibility Engine
- Synastry aspect scoring
- Composite chart generation
- Vedic guna matching with exceptions
- Chinese BaZi compatibility

## Phase 5: Research & Algorithms

### 5.1 Astronomical Calculations
- Implement JPL ephemeris integration
- Add Delta T corrections
- Implement nutation and aberration
- Add topocentric corrections

### 5.2 Traditional Algorithms
- Research authentic Vedic texts (BPHS, Jataka Parijata)
- Implement KP system rules
- Add Jaimini astrology
- Research Chinese BaZi authentic calculations

## Implementation Order

1. **Week 1**: Database refactoring to UUID + async
2. **Week 2**: Multi-tenancy + repository pattern
3. **Week 3**: Complete Vedic calculations
4. **Week 4**: Complete Chinese & Western calculations
5. **Week 5**: Prediction & compatibility engines
6. **Week 6**: Testing & optimization

## Key Libraries & Resources

### Python Libraries
- `skyfield`: For astronomical calculations
- `pyswisseph`: Swiss Ephemeris (already using)
- `lunarcalendar`: Chinese calendar conversions
- `vedic-astrology`: Additional Vedic calculations
- `asyncpg`: Async PostgreSQL driver
- `sqlmodel`: Async ORM

### Research Resources
- NASA JPL Horizons for validation
- Swiss Ephemeris documentation
- Vedic texts translations
- Chinese calendar algorithms
- IERS bulletins for Delta T

## Testing Strategy

1. **Unit Tests**: Each calculation method
2. **Integration Tests**: Full chart calculations
3. **Validation Tests**: Against known ephemeris data
4. **Performance Tests**: Async vs sync comparison
5. **Multi-tenant Tests**: Data isolation verification