"""
OAuth2 authentication routes.
"""
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import RedirectResponse
from typing import Optional

from josi.core.oauth import OAuthService, get_oauth_service
from josi.core.config import settings
from josi.api.response import ResponseModel

router = APIRouter(prefix="/oauth", tags=["OAuth Authentication"])


@router.get("/providers")
async def get_available_providers():
    """Get list of available OAuth providers."""
    providers = []
    
    if hasattr(settings, 'google_client_id') and settings.google_client_id:
        providers.append({
            "name": "google",
            "display_name": "Google",
            "icon": "https://www.google.com/favicon.ico"
        })
    
    if hasattr(settings, 'github_client_id') and settings.github_client_id:
        providers.append({
            "name": "github", 
            "display_name": "GitHub",
            "icon": "https://github.com/favicon.ico"
        })
    
    return ResponseModel(
        success=True,
        message="Available OAuth providers",
        data=providers
    )


@router.get("/login/{provider}")
async def oauth_login(
    provider: str,
    request: Request,
    oauth_service: OAuthService = Depends(get_oauth_service),
    redirect_url: Optional[str] = Query(None, description="URL to redirect after login")
):
    """Initiate OAuth login flow."""
    # Store redirect URL in session/state parameter
    if redirect_url:
        request.session["redirect_url"] = redirect_url
    
    redirect_uri = await oauth_service.get_oauth_redirect_url(provider, request)
    return RedirectResponse(url=redirect_uri)


@router.get("/callback/{provider}", name="oauth_callback")
async def oauth_callback(
    provider: str,
    request: Request,
    oauth_service: OAuthService = Depends(get_oauth_service),
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: Optional[str] = Query(None, description="State parameter")
):
    """Handle OAuth callback from provider."""
    result = await oauth_service.handle_oauth_callback(provider, request)
    
    # Get redirect URL from session or use default
    frontend_url = getattr(settings, 'frontend_url', 'http://localhost:3000')
    redirect_url = request.session.get("redirect_url", f"{frontend_url}/dashboard")
    
    # Clear session
    if "redirect_url" in request.session:
        del request.session["redirect_url"]
    
    # Redirect to frontend with token
    # In production, consider using a more secure method like:
    # 1. Server-side session with httpOnly cookie
    # 2. Temporary authorization code that frontend exchanges for token
    # 3. PostMessage API for popup-based flow
    
    redirect_params = f"?token={result['access_token']}&token_type={result['token_type']}"
    return RedirectResponse(url=f"{redirect_url}{redirect_params}")


@router.post("/link/{provider}")
async def link_oauth_provider(
    provider: str,
    request: Request,
    oauth_service: OAuthService = Depends(get_oauth_service),
    # current_user = Depends(get_current_user)  # Require authenticated user
):
    """Link an OAuth provider to existing account."""
    # This would allow users to link multiple OAuth providers
    # to their existing account
    return ResponseModel(
        success=True,
        message=f"Please implement linking {provider} to existing account",
        data=None
    )


@router.delete("/unlink/{provider}")
async def unlink_oauth_provider(
    provider: str,
    # current_user = Depends(get_current_user)
):
    """Unlink an OAuth provider from account."""
    # This would allow users to remove OAuth providers
    # from their account (if they have password or other providers)
    return ResponseModel(
        success=True,
        message=f"Please implement unlinking {provider} from account",
        data=None
    )