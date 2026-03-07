# Descope Console Setup Guide

Step-by-step instructions for configuring the Descope HTTP Connector and auth flows to work with the Josi backend.

**Prerequisites:**
- Backend deployed with the webhook endpoint live at `POST /api/v1/webhooks/descope/login`
- The enrich secret from GCP Secret Manager (`descope-josiam-enrich-secret`)
- Logged into Descope Console at https://app.descope.com

---

## Step 1: Create the HTTP Connector

1. Go to **Descope Console** → **Build** → **Connectors** (left sidebar)
2. Click **+ Connector** (top right)
3. Select **Generic HTTP**
4. Configure:

| Field | Value |
|---|---|
| **Name** | `Josi Login Enrichment` |
| **Description** | `Calls Josi backend to provision user and get JWT claims` |
| **Base URL** | `https://your-api-domain.com` (or `http://localhost:8000` for dev) |

5. Click **Save**

---

## Step 2: Configure the Connector Action

1. After saving, click on the connector to edit it
2. Go to the **Actions** tab
3. Click **+ Action**
4. Configure:

| Field | Value |
|---|---|
| **Name** | `Enrich Login` |
| **HTTP Method** | `POST` |
| **Path** | `/api/v1/webhooks/descope/login` |

5. **Headers** — click **+ Header**:

| Header Name | Header Value |
|---|---|
| `Content-Type` | `application/json` |
| `X-Descope-Webhook-Secret` | `<paste the enrich secret from GCP>` |

6. **Request Body** — set to JSON:

```json
{
  "sub": "{{user.externalIds.[0]}}",
  "email": "{{user.email}}"
}
```

> **Note:** The exact template syntax depends on your Descope flow context. `{{user.externalIds.[0]}}` is the Descope user ID. If that doesn't work, try `{{user.userId}}` or check the Descope template docs.

7. **Response Mapping** — map the response fields to flow context variables:

| Response Field | Map To |
|---|---|
| `josi_user_id` | `josiUserId` |
| `josi_subscription_tier` | `josiSubscriptionTier` |
| `josi_roles` | `josiRoles` |

8. Click **Save**

---

## Step 3: Add Custom Claims to JWT

1. Go to **Build** → **JWT Templates** (left sidebar)
2. Find or create the JWT template used by your project
3. Add these **custom claims**:

| Claim Name | Value (from flow context) |
|---|---|
| `josi_user_id` | `{{josiUserId}}` |
| `josi_subscription_tier` | `{{josiSubscriptionTier}}` |
| `josi_roles` | `{{josiRoles}}` |

4. Click **Save**

---

## Step 4: Add Connector to Sign-Up Flow

1. Go to **Build** → **Flows** (left sidebar)
2. Click on the **Sign Up** flow (or **Sign Up or In** if using combined flow)
3. In the flow editor, find the step **after successful authentication** (after OTP verification, password check, or OAuth callback)
4. Add a new step:
   - Type: **Connector**
   - Select: `Josi Login Enrichment` → `Enrich Login`
5. Connect the step so it runs after authentication succeeds but before the flow completes
6. **Map inputs** if needed:
   - The connector action template (`{{user.email}}`, etc.) should auto-resolve from the flow context
7. **Map outputs** — ensure the response variables (`josiUserId`, etc.) are stored in the flow context so the JWT template can read them
8. Click **Save** and **Publish** the flow

---

## Step 5: Add Connector to Sign-In Flow

1. Repeat Step 4 for the **Sign In** flow
2. The same connector action is used — it handles both new and existing users (upsert logic in the backend)
3. **Save** and **Publish**

> **Tip:** If you're using a **Sign Up or In** combined flow, you only need to add it once.

---

## Step 6: Test the Integration

### Test 1: New User Sign-Up

1. Open your app at `http://localhost:4000/auth/login`
2. Sign up with a new email/phone
3. After authentication, check:
   - Backend logs should show "New user created" with the email
   - The JWT should contain `josi_user_id`, `josi_subscription_tier`, `josi_roles` claims
   - The database should have a new row in the `users` table

### Test 2: Existing User Sign-In

1. Sign in with the same credentials
2. Check:
   - Backend logs should show "Existing user login"
   - `last_login` should be updated in the DB
   - JWT claims should match the existing user data

### Test 3: Verify JWT Claims

1. After login, open browser DevTools → Application → Cookies
2. Find the Descope session cookie
3. Copy the session JWT and decode it at https://jwt.io
4. Verify these claims exist:
   ```json
   {
     "josi_user_id": "some-uuid",
     "josi_subscription_tier": "free",
     "josi_roles": ["user"]
   }
   ```

### Test 4: API Request with JWT

```bash
curl -X GET http://localhost:8000/api/v1/persons \
  -H "Authorization: Bearer <paste-session-jwt>"
```

Expected: 200 response (or empty list), NOT 401.

---

## Troubleshooting

### Connector returns error during login

- Check that the backend is running and the webhook URL is reachable from Descope's servers
- For local development, use a tunnel (ngrok, cloudflared) to expose `localhost:8000`
- Verify the webhook secret matches between Descope header config and your backend env var

### JWT doesn't contain custom claims

- Check that the JWT Template has the custom claims mapped
- Check that the flow outputs are correctly mapped to the context variables the JWT template reads
- In the Descope flow editor, check the connector step's output mapping

### User not created in database

- Check backend logs for errors from the webhook endpoint
- Verify the Descope Management Key is valid (needed to fetch phone/name for new users)
- Check that the database migration has been applied (`alembic upgrade head`)

---

## Environment-Specific URLs

| Environment | Webhook URL |
|---|---|
| Local dev | `https://<ngrok-id>.ngrok.io/api/v1/webhooks/descope/login` |
| Staging | `https://staging-api.josiam.com/api/v1/webhooks/descope/login` |
| Production | `https://api.josiam.com/api/v1/webhooks/descope/login` |

Update the connector Base URL when switching environments.
