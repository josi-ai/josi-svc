# GraphQL API Examples

## Overview

The Josi API now supports GraphQL at the `/graphql` endpoint. You can use the interactive GraphQL playground by visiting `/graphql` in your browser.

## Authentication

Include your API key in the headers:

```json
{
  "Authorization": "Bearer YOUR_API_KEY"
}
```

## Query Examples

### 1. Get a Person by ID

```graphql
query GetPerson($personId: UUID!) {
  person(personId: $personId) {
    personId
    name
    email
    dateOfBirth
    timeOfBirth
    placeOfBirth
    latitude
    longitude
    timezone
    charts {
      chartId
      chartType
      calculatedAt
    }
  }
}
```

Variables:
```json
{
  "personId": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 2. Search Persons

```graphql
query SearchPersons($query: String!, $organizationId: UUID) {
  searchPersons(query: $query, organizationId: $organizationId) {
    personId
    name
    email
    dateOfBirth
    placeOfBirth
  }
}
```

### 3. Get Person Charts

```graphql
query GetPersonCharts($personId: UUID!, $chartType: String) {
  personCharts(personId: $personId, chartType: $chartType) {
    chartId
    chartType
    houseSystem
    ayanamsa
    calculatedAt
    planetPositions
    aspects
    interpretations {
      interpretationId
      interpretationType
      title
      summary
    }
  }
}
```

### 4. Get Chart with Full Details

```graphql
query GetChart($chartId: UUID!) {
  chart(chartId: $chartId) {
    chartId
    chartType
    calculatedAt
    person {
      name
      dateOfBirth
      placeOfBirth
    }
    planetPositions
    houseCusps
    aspects
    interpretations {
      interpretationType
      title
      summary
      detailedText
    }
  }
}
```

## Mutation Examples

### 1. Create Organization

```graphql
mutation CreateOrganization($input: OrganizationCreateInput!) {
  createOrganization(input: $input) {
    organizationId
    name
    slug
    apiKey
    isActive
  }
}
```

Variables:
```json
{
  "input": {
    "name": "My Astrology Service",
    "slug": "my-astrology",
    "contactEmail": "contact@example.com"
  }
}
```

### 2. Create Person

```graphql
mutation CreatePerson($input: PersonCreateInput!, $organizationId: UUID!) {
  createPerson(input: $input, organizationId: $organizationId) {
    personId
    name
    email
    dateOfBirth
    timeOfBirth
    placeOfBirth
    latitude
    longitude
    timezone
  }
}
```

Variables:
```json
{
  "input": {
    "name": "John Doe",
    "email": "john@example.com",
    "dateOfBirth": "1990-01-15",
    "timeOfBirth": "1990-01-15T14:30:00",
    "placeOfBirth": "New York, NY, USA"
  },
  "organizationId": "your-org-id"
}
```

### 3. Calculate Charts

```graphql
mutation CalculateCharts(
  $personId: UUID!,
  $chartTypes: [String!]!,
  $houseSystem: String,
  $ayanamsa: String,
  $includeInterpretations: Boolean
) {
  calculateChart(
    personId: $personId,
    chartTypes: $chartTypes,
    houseSystem: $houseSystem,
    ayanamsa: $ayanamsa,
    includeInterpretations: $includeInterpretations
  ) {
    chartId
    chartType
    calculatedAt
    planetPositions
    aspects
    interpretations {
      interpretationType
      title
      summary
    }
  }
}
```

Variables:
```json
{
  "personId": "person-uuid",
  "chartTypes": ["vedic", "western", "chinese"],
  "houseSystem": "placidus",
  "ayanamsa": "lahiri",
  "includeInterpretations": true
}
```

### 4. Update Person

```graphql
mutation UpdatePerson($personId: UUID!, $input: PersonUpdateInput!) {
  updatePerson(personId: $personId, input: $input) {
    personId
    name
    email
    phone
  }
}
```

### 5. Delete Person

```graphql
mutation DeletePerson($personId: UUID!) {
  deletePerson(personId: $personId)
}
```

## Subscription Support (Future)

GraphQL subscriptions can be added for real-time updates:

```graphql
subscription OnChartCalculated($personId: UUID!) {
  chartCalculated(personId: $personId) {
    chartId
    chartType
    calculatedAt
  }
}
```

## Schema Introspection

You can query the schema to discover available types and fields:

```graphql
query IntrospectionQuery {
  __schema {
    types {
      name
      fields {
        name
        type {
          name
        }
      }
    }
  }
}
```

## Error Handling

GraphQL errors are returned in a standard format:

```json
{
  "errors": [
    {
      "message": "Person not found",
      "path": ["person"],
      "extensions": {
        "code": "NOT_FOUND"
      }
    }
  ]
}
```

## Rate Limiting

The GraphQL endpoint respects the same rate limits as the REST API based on your organization's plan.

## Best Practices

1. **Use fragments** for reusable field selections:
   ```graphql
   fragment PersonBasic on PersonSchema {
     personId
     name
     email
     dateOfBirth
   }
   ```

2. **Request only needed fields** to minimize response size and improve performance

3. **Use variables** instead of string interpolation for dynamic values

4. **Batch related queries** in a single request when possible

5. **Handle errors gracefully** - check for both data and errors in responses