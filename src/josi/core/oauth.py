"""
OAuth2 integration using Authlib for social login.
"""
from typing import Optional, Dict, Any
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import uuid4
import logging

from josi.core.config import settings
from josi.core.security import create_access_token, hash_password
from josi.db.async_db import get_async_db
from josi.models.organization_model import Organization

logger = logging.getLogger(__name__)

# Initialize OAuth
oauth = OAuth()

# Configure OAuth providers
if hasattr(settings, 'google_client_id') and settings.google_client_id:
    oauth.register(
        name='google',
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

if hasattr(settings, 'github_client_id') and settings.github_client_id:
    oauth.register(
        name='github',
        client_id=settings.github_client_id,
        client_secret=settings.github_client_secret,
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )


class OAuthService:
    """Service for handling OAuth operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_oauth_redirect_url(self, provider: str, request: Request) -> str:
        """Get OAuth provider redirect URL."""
        if provider not in ['google', 'github']:
            raise HTTPException(status_code=400, detail=f"Provider {provider} not supported")
        
        client = getattr(oauth, provider)
        redirect_uri = str(request.url_for('oauth_callback', provider=provider))
        
        return await client.authorize_redirect(request, redirect_uri)
    
    async def handle_oauth_callback(
        self, 
        provider: str, 
        request: Request
    ) -> Dict[str, Any]:
        """Handle OAuth callback and create/update user."""
        try:
            client = getattr(oauth, provider)
            token = await client.authorize_access_token(request)
            
            # Extract user info based on provider
            user_info = await self._extract_user_info(provider, client, token)
            
            # Find or create user
            user = await self._find_or_create_user(user_info, provider)
            
            # Create JWT token
            access_token = create_access_token(
                data={
                    "sub": str(user.get("user_id")),
                    "email": user.get("email"),
                    "organization_id": str(user.get("organization_id")),
                    "permissions": user.get("permissions", []),
                }
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user
            }
            
        except OAuthError as e:
            logger.error(f"OAuth error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")
    
    async def _extract_user_info(
        self, 
        provider: str, 
        client: Any, 
        token: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract user information from OAuth provider response."""
        if provider == 'google':
            user_info = token.get('userinfo', {})
            return {
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'provider_id': user_info.get('sub'),
                'avatar_url': user_info.get('picture'),
                'email_verified': user_info.get('email_verified', False)
            }
        
        elif provider == 'github':
            # Get user info from GitHub API
            resp = await client.get('user', token=token)
            user_info = resp.json()
            
            # Get primary email if not public
            if not user_info.get('email'):
                email_resp = await client.get('user/emails', token=token)
                emails = email_resp.json()
                primary_email = next(
                    (e['email'] for e in emails if e['primary'] and e['verified']), 
                    None
                )
                user_info['email'] = primary_email
            
            return {
                'email': user_info.get('email'),
                'name': user_info.get('name') or user_info.get('login'),
                'provider_id': str(user_info.get('id')),
                'avatar_url': user_info.get('avatar_url'),
                'email_verified': True  # GitHub requires email verification
            }
        
        raise ValueError(f"Unknown provider: {provider}")
    
    async def _find_or_create_user(
        self, 
        user_info: Dict[str, Any], 
        provider: str
    ) -> Dict[str, Any]:
        """Find existing user or create new one."""
        # For now, return mock user data
        # In production, this would query/create in the database
        
        # Check if user exists by email
        # user = self.db.exec(
        #     select(User).where(User.email == user_info['email'])
        # ).first()
        
        # if not user:
        #     # Get or create default organization
        #     org = self.db.exec(
        #         select(Organization).where(Organization.slug == "default")
        #     ).first()
        #     
        #     if not org:
        #         org = Organization(
        #             name="Default Organization",
        #             slug="default",
        #             api_key=f"sk_default_{uuid4().hex}",
        #             is_active=True,
        #             plan_type="free",
        #             monthly_api_limit=1000,
        #             current_month_usage=0
        #         )
        #         self.db.add(org)
        #         self.db.commit()
        #     
        #     # Create new user
        #     user = User(
        #         email=user_info['email'],
        #         name=user_info['name'],
        #         organization_id=org.organization_id,
        #         oauth_provider=provider,
        #         oauth_provider_id=user_info['provider_id'],
        #         avatar_url=user_info.get('avatar_url'),
        #         is_active=True,
        #         email_verified=user_info.get('email_verified', False)
        #     )
        #     self.db.add(user)
        #     self.db.commit()
        #     self.db.refresh(user)
        
        # Return mock user for now
        return {
            "user_id": str(uuid4()),
            "email": user_info['email'],
            "name": user_info['name'],
            "organization_id": str(uuid4()),
            "permissions": ["read", "write"],
            "oauth_provider": provider,
            "avatar_url": user_info.get('avatar_url')
        }


async def get_oauth_service(db: AsyncSession = Depends(get_async_db)) -> OAuthService:
    """Dependency to get OAuth service."""
    return OAuthService(db)