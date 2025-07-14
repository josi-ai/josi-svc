# Setting Up OAuth with Google and GitHub

This guide walks through setting up OAuth authentication for Josi API.

## Google OAuth Setup

### 1. Create OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project or create a new one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth client ID**
5. Configure OAuth consent screen if prompted:
   - User Type: External (or Internal for G Suite)
   - Add app name, support email, and domains
   - Add scopes: `email`, `profile`, `openid`
6. For Application type, select **Web application**
7. Add authorized redirect URIs:
   ```
   # Development
   http://localhost:8000/api/v1/oauth/callback/google
   
   # Production
   https://api.josi.example.com/api/v1/oauth/callback/google
   ```
8. Save the Client ID and Client Secret

### 2. Configure Environment Variables

```bash
# .env file
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### 3. Store in Google Secret Manager (for GCP deployment)

```bash
# Create secrets
echo -n "your-client-id.apps.googleusercontent.com" | \
  gcloud secrets create google-oauth-client-id --data-file=-

echo -n "your-client-secret" | \
  gcloud secrets create google-oauth-client-secret --data-file=-

# Update Cloud Run service
gcloud run services update josi-api \
  --set-secrets="GOOGLE_CLIENT_ID=google-oauth-client-id:latest" \
  --set-secrets="GOOGLE_CLIENT_SECRET=google-oauth-client-secret:latest" \
  --region=us-central1
```

## GitHub OAuth Setup

### 1. Create OAuth App

1. Go to GitHub Settings > Developer settings > [OAuth Apps](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in the details:
   - Application name: `Josi API`
   - Homepage URL: `https://josi.example.com`
   - Authorization callback URL:
     ```
     # Development
     http://localhost:8000/api/v1/oauth/callback/github
     
     # Production
     https://api.josi.example.com/api/v1/oauth/callback/github
     ```
4. Save the Client ID and generate a Client Secret

### 2. Configure Environment Variables

```bash
# .env file
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## Frontend Integration

### React Example with TypeScript

```typescript
// src/hooks/useAuth.ts
import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  oauth_provider?: string;
}

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('access_token')
  );

  useEffect(() => {
    // Check for OAuth callback
    const params = new URLSearchParams(window.location.search);
    const callbackToken = params.get('token');
    
    if (callbackToken) {
      localStorage.setItem('access_token', callbackToken);
      setToken(callbackToken);
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
    }

    // Fetch user profile if token exists
    if (token) {
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setUser(response.data.data);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const loginWithOAuth = (provider: 'google' | 'github') => {
    window.location.href = `${API_URL}/api/v1/oauth/login/${provider}`;
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
  };

  return {
    user,
    loading,
    isAuthenticated: !!user,
    loginWithOAuth,
    logout
  };
};
```

```typescript
// src/components/LoginPage.tsx
import React from 'react';
import { useAuth } from '../hooks/useAuth';

export const LoginPage: React.FC = () => {
  const { loginWithOAuth, isAuthenticated } = useAuth();

  if (isAuthenticated) {
    window.location.href = '/dashboard';
    return null;
  }

  return (
    <div className="login-page">
      <h1>Login to Josi</h1>
      
      <div className="oauth-buttons">
        <button 
          onClick={() => loginWithOAuth('google')}
          className="oauth-button google"
        >
          <img src="/google-icon.svg" alt="Google" />
          Continue with Google
        </button>
        
        <button 
          onClick={() => loginWithOAuth('github')}
          className="oauth-button github"
        >
          <img src="/github-icon.svg" alt="GitHub" />
          Continue with GitHub
        </button>
      </div>
      
      <div className="divider">
        <span>or</span>
      </div>
      
      <form className="email-login">
        <input type="email" placeholder="Email" />
        <input type="password" placeholder="Password" />
        <button type="submit">Login</button>
      </form>
    </div>
  );
};
```

## Testing OAuth Locally

### 1. Using ngrok for HTTPS tunnel

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Start your API
poetry run uvicorn josi.main:app --reload

# In another terminal, create tunnel
ngrok http 8000

# Update OAuth redirect URLs to use ngrok URL
# e.g., https://abc123.ngrok.io/api/v1/oauth/callback/google
```

### 2. Update OAuth App Settings

Temporarily add your ngrok URL to the authorized redirect URIs in Google/GitHub OAuth settings.

### 3. Test the Flow

1. Visit `http://localhost:3000/login`
2. Click "Continue with Google" or "Continue with GitHub"
3. Authorize the application
4. You should be redirected back with a token

## Security Considerations

### 1. Token Storage

```typescript
// Secure token storage options

// Option 1: httpOnly cookie (most secure for web)
// Backend sets cookie, frontend can't access via JS

// Option 2: Secure localStorage wrapper
class SecureStorage {
  private static encrypt(data: string): string {
    // Implement encryption if needed
    return btoa(data);
  }
  
  private static decrypt(data: string): string {
    return atob(data);
  }
  
  static setToken(token: string): void {
    const encrypted = this.encrypt(token);
    localStorage.setItem('auth_token', encrypted);
  }
  
  static getToken(): string | null {
    const encrypted = localStorage.getItem('auth_token');
    return encrypted ? this.decrypt(encrypted) : null;
  }
  
  static clear(): void {
    localStorage.removeItem('auth_token');
  }
}
```

### 2. PKCE Flow for SPAs

For production SPAs, implement PKCE (Proof Key for Code Exchange):

```python
# src/josi/core/oauth_pkce.py
import secrets
import hashlib
import base64

def generate_pkce_params():
    """Generate PKCE challenge and verifier."""
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode('utf-8').rstrip('=')
    
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge
```

### 3. State Parameter

Always use state parameter to prevent CSRF:

```python
# In OAuth login endpoint
state = secrets.token_urlsafe(32)
request.session['oauth_state'] = state

# In callback endpoint
if request.session.get('oauth_state') != state_from_provider:
    raise HTTPException(status_code=400, detail="Invalid state parameter")
```

## Troubleshooting

### Common Issues

1. **Redirect URI mismatch**
   - Ensure redirect URI exactly matches (including trailing slashes)
   - Check for http vs https
   - Verify port numbers

2. **CORS errors**
   - Add frontend domain to CORS_ORIGINS
   - Ensure credentials are included in requests

3. **Token not persisting**
   - Check browser console for errors
   - Verify localStorage is not blocked
   - Check token expiration

4. **User profile not loading**
   - Verify JWT token is valid
   - Check API logs for errors
   - Ensure user exists in database

### Debug Mode

Enable debug logging:

```python
# .env
LOG_LEVEL=DEBUG

# See OAuth flow details in logs
```

## Production Checklist

- [ ] Use HTTPS for all OAuth redirects
- [ ] Store OAuth secrets in Secret Manager
- [ ] Implement refresh token rotation
- [ ] Add rate limiting to OAuth endpoints
- [ ] Monitor failed login attempts
- [ ] Implement account linking for multiple providers
- [ ] Add email verification for new accounts
- [ ] Implement proper session management
- [ ] Add CAPTCHA for registration
- [ ] Set up alerting for suspicious activity