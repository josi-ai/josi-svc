# Astrow API Endpoint Inventory

This document provides a comprehensive inventory of all API endpoints available in the Astrow astrology calculation API. The API supports both REST and GraphQL interfaces.

## Base URL
- REST API: `/api/v1`
- GraphQL: `/graphql`

## Authentication
All endpoints require API key authentication via the `X-API-Key` header.

---

## REST API Endpoints

### 1. Person Management (`/api/v1/persons`)

#### Create Person
- **Method**: `POST`
- **Path**: `/api/v1/persons/`
- **Purpose**: Create a new person record with birth information
- **Required Parameters**:
  - `name` (string): Full name
  - `date_of_birth` (date): Birth date (YYYY-MM-DD)
  - `time_of_birth` (time): Birth time (HH:MM:SS)
  - `place_of_birth` (string): Birth location as "City, State, Country"
- **Optional Parameters**:
  - `email` (string): Email address
  - `phone` (string): Phone number
  - `notes` (string): Additional notes
- **Response**: Person object with auto-generated UUID, geocoded coordinates, and timezone

#### Get Person by ID
- **Method**: `GET`
- **Path**: `/api/v1/persons/{person_id}`
- **Purpose**: Retrieve detailed information about a specific person
- **Required Parameters**:
  - `person_id` (UUID): Person's unique identifier
- **Response**: Complete person object with all fields

#### List All Persons
- **Method**: `GET`
- **Path**: `/api/v1/persons/`
- **Purpose**: Get paginated list of persons in the organization
- **Query Parameters**:
  - `skip` (int): Pagination offset (default: 0)
  - `limit` (int): Max records to return (default: 100, max: 1000)
  - `search` (string): Search by name or email
  - `order_by` (string): Sort fields (comma-separated, prefix with - for descending)
- **Response**: List of person objects

#### Update Person
- **Method**: `PUT`
- **Path**: `/api/v1/persons/{person_id}`
- **Purpose**: Update person's information
- **Required Parameters**:
  - `person_id` (UUID): Person's unique identifier
- **Body**: PersonModel with fields to update (all optional)
- **Response**: Updated person object

#### Delete Person
- **Method**: `DELETE`
- **Path**: `/api/v1/persons/{person_id}`
- **Purpose**: Soft delete a person record
- **Required Parameters**:
  - `person_id` (UUID): Person's unique identifier
- **Response**: Confirmation with deleted person_id

#### Restore Person
- **Method**: `PUT`
- **Path**: `/api/v1/persons/restore/{person_id}`
- **Purpose**: Restore a soft-deleted person
- **Required Parameters**:
  - `person_id` (UUID): Person's unique identifier
- **Response**: Restored person object

#### Get Person's Charts
- **Method**: `GET`
- **Path**: `/api/v1/persons/{person_id}/charts`
- **Purpose**: Get all charts calculated for a person
- **Required Parameters**:
  - `person_id` (UUID): Person's unique identifier
- **Response**: List of charts with person details

#### Bulk Create Persons
- **Method**: `POST`
- **Path**: `/api/v1/persons/bulk`
- **Purpose**: Create multiple persons in one request
- **Body**: Array of PersonEntity objects
- **Response**: List of created persons

#### Bulk Update Persons
- **Method**: `PUT`
- **Path**: `/api/v1/persons/bulk`
- **Purpose**: Update multiple persons in one request
- **Body**: Array of PersonModel objects with id field
- **Response**: List of updated persons

---

### 2. Chart Calculations (`/api/v1/charts`)

#### Calculate Charts
- **Method**: `POST`
- **Path**: `/api/v1/charts/calculate`
- **Purpose**: Calculate astrological charts for a person
- **Query Parameters**:
  - `person_id` (UUID): Person's identifier (required)
  - `systems` (array): Chart systems ["vedic", "western", "chinese", etc.] (default: ["vedic", "western"])
  - `house_system` (string): House division system (default: "placidus")
  - `ayanamsa` (string): For sidereal calculations (default: "lahiri")
  - `include_interpretations` (bool): Generate AI interpretations (default: false)
- **Response**: Person data with calculated charts and metadata

#### Get Chart by ID
- **Method**: `GET`
- **Path**: `/api/v1/charts/{chart_id}`
- **Purpose**: Retrieve a specific chart's details
- **Required Parameters**:
  - `chart_id` (UUID): Chart's unique identifier
- **Response**: Complete chart data with positions and aspects

#### Get Person's Charts
- **Method**: `GET`
- **Path**: `/api/v1/charts/person/{person_id}`
- **Purpose**: Get all charts for a specific person
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
- **Query Parameters**:
  - `chart_type` (string): Filter by chart type
- **Response**: List of charts for the person

#### Generate Interpretations
- **Method**: `POST`
- **Path**: `/api/v1/charts/{chart_id}/interpret`
- **Purpose**: Generate AI-powered interpretations for a chart
- **Required Parameters**:
  - `chart_id` (UUID): Chart's identifier
  - `interpretation_types` (array): Types ["general", "personality", "career", etc.]
- **Query Parameters**:
  - `language` (string): Language code (default: "en")
- **Response**: List of interpretations with confidence scores

#### Get Divisional Charts
- **Method**: `GET`
- **Path**: `/api/v1/charts/divisional/{person_id}`
- **Purpose**: Calculate Vedic divisional charts (D1-D60)
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
  - `division` (int): Division number (1-60)
- **Response**: Divisional chart data with interpretation

#### Delete Chart
- **Method**: `DELETE`
- **Path**: `/api/v1/charts/{chart_id}`
- **Purpose**: Soft delete a chart
- **Required Parameters**:
  - `chart_id` (UUID): Chart's identifier
- **Response**: Confirmation with deleted chart_id

#### Restore Chart
- **Method**: `PUT`
- **Path**: `/api/v1/charts/restore/{chart_id}`
- **Purpose**: Restore a deleted chart
- **Required Parameters**:
  - `chart_id` (UUID): Chart's identifier
- **Response**: Restored chart object

---

### 3. Compatibility Analysis (`/api/v1/compatibility`)

#### Calculate Vedic Compatibility
- **Method**: `POST`
- **Path**: `/api/v1/compatibility/calculate`
- **Purpose**: Calculate Ashtakoota compatibility between two people
- **Body**:
  - `person1_id` (UUID): First person's identifier
  - `person2_id` (UUID): Second person's identifier
- **Response**: 
  - Total score (out of 36)
  - Individual guna scores
  - Manglik dosha status
  - Recommendations

#### Calculate Western Synastry
- **Method**: `POST`
- **Path**: `/api/v1/compatibility/synastry`
- **Purpose**: Western synastry analysis between two charts
- **Body**:
  - `person1_id` (UUID): First person's identifier
  - `person2_id` (UUID): Second person's identifier
- **Response**:
  - Inter-chart aspects
  - House overlays
  - Composite points
  - Relationship dynamics

---

### 4. Transit Analysis (`/api/v1/transits`)

#### Get Current Transits
- **Method**: `GET`
- **Path**: `/api/v1/transits/current/{person_id}`
- **Purpose**: Current planetary transits affecting natal chart
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
- **Response**:
  - Major transits with aspects
  - Current planetary positions
  - Transit interpretations

#### Get Transit Forecast
- **Method**: `GET`
- **Path**: `/api/v1/transits/forecast/{person_id}`
- **Purpose**: Forecast significant transits for upcoming period
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
- **Query Parameters**:
  - `days` (int): Forecast period (default: 30, max: 365)
- **Response**:
  - Exact transit timings
  - Sign changes
  - Retrograde periods

---

### 5. Dasha Periods (`/api/v1/dasha`)

#### Get Vimshottari Dasha
- **Method**: `GET`
- **Path**: `/api/v1/dasha/vimshottari/{person_id}`
- **Purpose**: Calculate 120-year Vimshottari Dasha cycle
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
- **Response**:
  - Birth nakshatra
  - Current dasha/antardasha/pratyantardasha
  - Complete dasha sequence
  - Upcoming changes

#### Get Yogini Dasha
- **Method**: `GET`
- **Path**: `/api/v1/dasha/yogini/{person_id}`
- **Purpose**: Calculate 36-year Yogini Dasha cycle
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
- **Response**:
  - Current yogini period
  - Complete yogini sequence

#### Get Chara Dasha
- **Method**: `GET`
- **Path**: `/api/v1/dasha/chara/{person_id}`
- **Purpose**: Calculate Jaimini sign-based dasha
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
- **Response**:
  - Current sign dasha
  - Sign sequence with durations

---

### 6. Predictions (`/api/v1/predictions`)

#### Get Daily Predictions
- **Method**: `GET`
- **Path**: `/api/v1/predictions/daily/{person_id}`
- **Purpose**: Daily forecast based on Moon transits
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
- **Query Parameters**:
  - `date` (datetime): Prediction date (default: today)
- **Response**:
  - General daily theme
  - Career, finance, health, relationship guidance
  - Lucky number and color
  - Favorable times

#### Get Monthly Predictions
- **Method**: `GET`
- **Path**: `/api/v1/predictions/monthly/{person_id}`
- **Purpose**: Monthly forecast with key dates
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
- **Query Parameters**:
  - `month` (int): Month number (1-12)
  - `year` (int): Year
- **Response**:
  - Monthly overview
  - Key dates
  - Favorable periods
  - Challenges and opportunities

#### Get Yearly Predictions
- **Method**: `GET`
- **Path**: `/api/v1/predictions/yearly/{person_id}`
- **Purpose**: Annual forecast with life themes
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
- **Query Parameters**:
  - `year` (int): Prediction year
- **Response**:
  - Yearly theme
  - Career, financial, relationship, health outlook
  - Major periods breakdown
  - Lucky months

---

### 7. Remedies & Recommendations (`/api/v1/remedies`)

#### Get Personalized Remedies
- **Method**: `GET`
- **Path**: `/api/v1/remedies/{person_id}`
- **Purpose**: Comprehensive remedial measures based on chart
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
- **Response**:
  - Gemstones recommendations
  - Mantras with counts
  - Donations and charity
  - Yantras
  - Fasting recommendations
  - General remedies

#### Get Gemstone Recommendations
- **Method**: `GET`
- **Path**: `/api/v1/remedies/gemstones/{person_id}`
- **Purpose**: Detailed gemstone therapy analysis
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
- **Response**:
  - Primary gemstone with specifications
  - Life stone and lucky stone
  - Beneficial stones
  - Stones to avoid
  - Wearing instructions

#### Calculate Numerology
- **Method**: `POST`
- **Path**: `/api/v1/remedies/numerology`
- **Purpose**: Numerological analysis and recommendations
- **Body**:
  - `name` (string): Full name
  - `date_of_birth` (datetime): Birth date
- **Response**:
  - Life path number
  - Destiny number
  - Soul number
  - Personal year
  - Lucky numbers and colors

#### Get Color Therapy
- **Method**: `POST`
- **Path**: `/api/v1/remedies/color-therapy/{person_id}`
- **Purpose**: Color recommendations based on planets
- **Required Parameters**:
  - `person_id` (UUID): Person's identifier
- **Response**:
  - Daily color recommendations
  - Purpose-specific colors
  - Colors to avoid
  - Home and office color suggestions

---

### 8. Panchang & Muhurta (`/api/v1/panchang`)

#### Get Panchang
- **Method**: `GET`
- **Path**: `/api/v1/panchang/`
- **Purpose**: Hindu calendar details for date and location
- **Query Parameters**:
  - `date` (datetime): Date and time
  - `latitude` (float): Location latitude
  - `longitude` (float): Location longitude
  - `timezone` (string): Timezone name
- **Response**:
  - Tithi (lunar day)
  - Nakshatra (lunar mansion)
  - Yoga and Karana
  - Rahu Kaal timing
  - Sunrise/sunset

#### Find Muhurta
- **Method**: `POST`
- **Path**: `/api/v1/panchang/muhurta`
- **Purpose**: Find auspicious times for activities
- **Body**:
  - `purpose` (string): Activity type (marriage, business, travel, etc.)
  - `start_date` (datetime): Search start
  - `end_date` (datetime): Search end
  - `latitude` (float): Location latitude
  - `longitude` (float): Location longitude
  - `timezone` (string): Timezone
- **Query Parameters**:
  - `max_results` (int): Maximum results (default: 10, max: 50)
- **Response**:
  - List of auspicious times with quality ratings
  - Special factors and avoid factors

---

### 9. Location Services (`/api/v1/location`)

#### Search Location
- **Method**: `GET`
- **Path**: `/api/v1/location/search`
- **Purpose**: Geocode locations and get coordinates
- **Query Parameters**:
  - `query` (string): Location search string
  - `limit` (int): Max results (default: 5, max: 20)
- **Response**:
  - List of matching locations
  - Coordinates and timezone
  - Formatted addresses

#### Get Coordinates
- **Method**: `POST`
- **Path**: `/api/v1/location/coordinates`
- **Purpose**: Get coordinates for structured location
- **Body**:
  - `city` (string): City name (required)
  - `state` (string): State/province (optional)
  - `country` (string): Country (optional)
- **Response**:
  - Latitude and longitude
  - Timezone information

#### Get Timezone
- **Method**: `GET`
- **Path**: `/api/v1/location/timezone`
- **Purpose**: Get timezone for coordinates
- **Query Parameters**:
  - `latitude` (float): Latitude
  - `longitude` (float): Longitude
- **Response**:
  - IANA timezone identifier
  - UTC offset
  - DST information

---

## GraphQL API Endpoints

### Query Operations

#### Person Queries
- `persons`: Get all persons with pagination
- `searchPersons`: Search persons with pagination
- `person`: Get person by ID
- `personsByIds`: Get multiple persons by IDs

#### Chart Queries
- `charts`: Get all charts with filtering
- `chart`: Get chart by ID
- `personCharts`: Get charts for a person
- `chartInterpretations`: Get interpretations for a chart

#### Organization Queries
- `organizations`: List organizations
- `organization`: Get organization by ID

### Mutation Operations

#### Person Mutations
- `addPerson`: Create new person
- `addPersons`: Create multiple persons
- `updatePerson`: Update person details
- `updatePersons`: Update multiple persons
- `deletePerson`: Soft delete person
- `restorePerson`: Restore deleted person

#### Chart Mutations
- `calculateChart`: Calculate charts for person
- `generateInterpretation`: Generate chart interpretations
- `deleteChart`: Delete chart
- `restoreChart`: Restore deleted chart

#### Organization Mutations
- `addOrganization`: Create organization
- `updateOrganization`: Update organization
- `deleteOrganization`: Delete organization

---

## Response Format

All REST endpoints return a standardized ResponseModel:

```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": { ... },
    "errors": []
}
```

## Error Codes

- `400`: Bad Request - Invalid parameters
- `404`: Not Found - Resource doesn't exist
- `401`: Unauthorized - Invalid API key
- `500`: Internal Server Error

## Rate Limiting

API rate limits are applied per organization:
- Standard: 1000 requests per hour
- Premium: 10000 requests per hour

## Caching

Many GET endpoints implement caching:
- Person data: 2 hours
- Chart data: 24 hours
- Predictions: 1 hour
- Location data: 7 days

## Supported Astrological Systems

1. **Vedic (Jyotish)**: Traditional Indian astrology
2. **Western**: Tropical zodiac astrology
3. **Chinese**: Four Pillars/BaZi
4. **Hellenistic**: Ancient Greek astrology
5. **Mayan**: Tzolkin/Haab calendar
6. **Celtic**: Tree/Ogham astrology
7. **Sidereal**: Fixed star based
8. **Tropical**: Season based

## House Systems

- Placidus (default)
- Koch
- Equal
- Whole Sign
- Regiomontanus
- Campanus
- Porphyry
- Alcabitius

## Ayanamsa Options

- Lahiri (default)
- Krishnamurti
- Raman
- Fagan-Bradley
- True Chitrapaksha

---

## Notes

1. All dates/times in requests should be in ISO 8601 format
2. All coordinates use decimal degrees (negative for South/West)
3. UUID fields use standard UUID v4 format
4. Soft deletes maintain data integrity while hiding records
5. Multi-tenant architecture ensures data isolation between organizations