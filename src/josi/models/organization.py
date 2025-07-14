from sqlalchemy import Column, String, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from josi.models.base import BaseModel
import secrets


class Organization(BaseModel):
    __tablename__ = "organizations"
    
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    api_key = Column(String, unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
    
    # Settings
    settings = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    
    # Limits
    max_requests_per_month = Column(Integer, default=10000)
    max_users = Column(Integer, default=10)
    
    # Contact info
    contact_email = Column(String)
    contact_name = Column(String)
    
    # Features
    enabled_systems = Column(JSON, default=["vedic", "western", "chinese"])
    features = Column(JSON, default={
        "pdf_reports": False,
        "api_access": True,
        "bulk_calculations": False,
        "custom_orbs": False
    })