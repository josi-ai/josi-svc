# Descope Authentication Integration Design

Date: 2026-03-06

## Context

Josi needs authentication that works for B2C (individual users) and B2B (API consumers), supports a future microservices architecture, and keeps authorization under our control. Descope handles identity. We handle everything else.

## Decision: Descope for AuthN, Internal AuthZ

- **Descope** owns authentication: email, SMS, MFA, OAuth, SSO
- **Josi backend** owns authorization: roles, permissions, subscription tiers, rate limits
- **No organizations model** for now. Users are individuals. B2B customers are users with API keys.

## Auth Paths

### Path 1: B2C (Humans) - Descope JWT

```
Browser/App → Descope Auth (email/SMS/OAuth/MFA) → Descope JWT
  → Descope Connector calls POST /api/v1/webhooks/descope/login
    → Backend upserts User, returns claims
  → Descope injects custom claims into JWT
  → Client receives enriched JWT
  → Client sends: Authorization: Bearer <session-jwt>
```

### Path 2: B2B (Machines) - Self-Managed API Keys

```
Developer → Dashboard (authenticated via Descope)
  → POST /api/v1/api-keys → generates API key, stored in DB
  → Developer uses: X-API-Key: <api-key>
```

Users can create, rotate, and revoke their own API keys via authenticated endpoints.

## Gateway Architecture

### Now: Auth Middleware in josi-svc

While josi-svc is a monolith, auth resolution is middleware within the service. Two paths, same resolved user context:

```
Client Request (JWT or API Key)
  → josi-svc Auth Middleware
    ├─ Has JWT? → Validate via Descope JWKS → extract claims
    ├─ Has API Key? → DB lookup → resolve user
    └─ Neither? → 401
  → Sets CurrentUser in request state
  → Controller reads CurrentUser, proceeds
```

### Future: GCP API Gateway + Microservices

When josi-svc splits, auth moves to GCP API Gateway. Services are auth-dumb — they read headers.

```
                              ┌─→ josi-svc (astrology, users, API keys)
Client → GCP API Gateway ─────├─→ ai-svc (agents, interpretations)
                              └─→ future-svc
```

GCP API Gateway handles:
- JWT validation natively (configured with Descope JWKS endpoint, zero code)
- Route-based forwarding to Cloud Run services
- Rate limiting at the edge

For API Key requests, the gateway routes to josi-svc which resolves the user and injects X-* headers before forwarding internally.

All services receive standardized headers:
```
X-User-Id: <uuid>
X-Email: <email>
X-Subscription-Tier: <tier>
X-Roles: <comma-separated>
```

### Future: josi-core Package

When the second service is created, shared code is extracted into `josi-core`:

| Module | Contents |
|---|---|
| `josi_core.auth` | Auth middleware, JWT validation, user context from headers |
| `josi_core.schemas` | `CurrentUser`, `ResponseModel`, error schemas |
| `josi_core.logging` | Structured logging, correlation ID propagation |
| `josi_core.config` | Base config loading (GCP secrets, env vars) |

Not created until genuinely needed. No speculative abstractions. The auth module in josi-svc (`src/josi/auth/`) is structured to be liftable into josi-core with minimal refactoring.

## JWT Custom Claims

Descope JWT will include these custom claims (set via Connector):

```json
{
  "sub": "U3AXkLL5ULmyFWqbfyRwVpL2WjCi",
  "email": "govind@josiam.com",
  "amr": ["email", "sms", "mfa"],
  "aud": ["P3AXgK6L8OgCfFSKcrNaA99vVChw"],

  "josi_user_id": "internal-uuid",
  "josi_subscription_tier": "EXPLORER",
  "josi_roles": ["user", "astrologer"]
}
```

Prefixed with `josi_` to avoid claim collisions.

## Webhook Endpoint

`POST /api/v1/webhooks/descope/login`

Called by Descope Connector during auth flow. Secured with a shared secret (`descope-josiam-enrich-secret`).

**Request** (from Descope):
```json
{
  "sub": "U3AXkLL5ULmyFWqbfyRwVpL2WjCi",
  "email": "govind@josiam.com"
}
```

**Backend logic:**
1. Look up User by `descope_id`
2. If not found: call Descope Management API to get phone, name. Create User record.
3. If found: return existing data (no Management API call).
4. Return enrichment claims.

**Response:**
```json
{
  "josi_user_id": "uuid",
  "josi_subscription_tier": "FREE",
  "josi_roles": ["user"]
}
```

## API Key Management

Endpoints (all require Descope JWT auth):

- `POST /api/v1/api-keys` - Create a new API key
- `GET /api/v1/api-keys` - List user's API keys (masked)
- `DELETE /api/v1/api-keys/{key_id}` - Revoke a key
- `POST /api/v1/api-keys/{key_id}/rotate` - Rotate (revoke old, issue new)

API keys are stored hashed (bcrypt or SHA-256). The plaintext is shown once at creation.

## User Model Changes

Add to existing User model:
- `descope_id` (string, unique, indexed) - Descope user ID (`sub` claim)
- `phone` already exists
- Remove: `hashed_password`, `google_id`, `github_id` (Descope handles these)
- Remove: `oauth_providers` (Descope handles this)

New model: `ApiKey`
- `api_key_id` (UUID, primary key)
- `user_id` (FK to User)
- `key_hash` (string) - hashed API key
- `key_prefix` (string) - first 8 chars for identification
- `name` (string) - user-given label
- `last_used_at` (timestamp)
- `expires_at` (optional timestamp)
- `is_active` (boolean)
- `created_at`, `updated_at`

## What Gets Removed

- `src/josi/services/auth_service.py` - JWT creation, password auth, OAuth token exchange
- `src/josi/api/v1/auth.py` - Mock auth endpoints
- `src/josi/api/v1/oauth.py` - OAuth routes (Descope handles OAuth)
- `src/josi/core/oauth.py` - OAuth provider config
- `SecurityManager.create_access_token()` / `verify_token()` / `hash_password()` / `verify_password()`
- Password-related fields on User model

## What Stays

- `User` model (with modifications above)
- Rate limiting middleware (reads tier from resolved user context)
- All authorization logic
- All business logic services

## GCP Secrets

| Secret | Purpose |
|---|---|
| `descope-josiam-web-app-project-id` | Descope Project ID for JWT validation |
| `descope-josiam-management-key` | Descope Management API (fetch user details) |
| `descope-josiam-enrich-secret` | Shared secret securing the webhook endpoint |

## Descope Console Configuration Required

1. Create a **Generic HTTP Connector** pointing to `POST /api/v1/webhooks/descope/login`
2. Configure the connector with the enrich secret as an auth header
3. Add the connector to the **Sign Up** and **Sign In** flows
4. Map the response fields to custom JWT claims (`josi_user_id`, `josi_subscription_tier`, `josi_roles`)

## Dependencies

- `descope` Python SDK (for JWT validation and Management API)
- Remove: `python-jose`, `passlib`, `authlib` (no longer needed)
