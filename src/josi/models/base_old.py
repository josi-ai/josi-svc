from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields for all tables."""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class TenantModel(BaseModel):
    """Base model for multi-tenant tables."""
    __abstract__ = True
    
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)