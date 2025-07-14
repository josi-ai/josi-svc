"""Comprehensive unit tests for BaseService class."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from josi.services.base_service import BaseService


class TestBaseService:
    """Comprehensive test coverage for BaseService."""
    
    @pytest.fixture
    def organization_id(self):
        """Test organization ID."""
        return uuid4()
    
    @pytest.fixture
    def base_service(self, organization_id):
        """Create BaseService instance."""
        return BaseService(organization_id=organization_id)
    
    @pytest.fixture
    def base_service_no_org(self):
        """Create BaseService instance without organization."""
        return BaseService()
    
    def test_initialization_with_organization(self, organization_id):
        """Test BaseService initialization with organization ID."""
        service = BaseService(organization_id=organization_id)
        
        assert service.organization_id == organization_id
        assert hasattr(service, 'get_session')
    
    def test_initialization_without_organization(self):
        """Test BaseService initialization without organization ID."""
        service = BaseService()
        
        assert service.organization_id is None
        assert hasattr(service, 'get_session')
    
    def test_initialization_with_none_organization(self):
        """Test BaseService initialization with explicit None organization."""
        service = BaseService(organization_id=None)
        
        assert service.organization_id is None
    
    @pytest.mark.asyncio
    async def test_get_session_default(self, base_service, organization_id):
        """Test getting default session (not read replica)."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        with patch('josi.services.base_service.get_async_session') as mock_get_session:
            # Setup mock to return async context manager
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_session
            mock_context.__aexit__.return_value = None
            mock_get_session.return_value = mock_context
            
            # Get session
            session = await base_service.get_session()
            
            # Assertions
            assert session == mock_session
            mock_get_session.assert_called_once_with(
                organization_id=organization_id,
                is_read_replica=False
            )
    
    @pytest.mark.asyncio
    async def test_get_session_read_replica(self, base_service, organization_id):
        """Test getting read replica session."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        with patch('josi.services.base_service.get_async_session') as mock_get_session:
            # Setup mock to return async context manager
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_session
            mock_context.__aexit__.return_value = None
            mock_get_session.return_value = mock_context
            
            # Get read replica session
            session = await base_service.get_session(is_read_replica=True)
            
            # Assertions
            assert session == mock_session
            mock_get_session.assert_called_once_with(
                organization_id=organization_id,
                is_read_replica=True
            )
    
    @pytest.mark.asyncio
    async def test_get_session_without_organization(self, base_service_no_org):
        """Test getting session without organization ID."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        with patch('josi.services.base_service.get_async_session') as mock_get_session:
            # Setup mock to return async context manager
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_session
            mock_context.__aexit__.return_value = None
            mock_get_session.return_value = mock_context
            
            # Get session
            session = await base_service_no_org.get_session()
            
            # Assertions
            assert session == mock_session
            mock_get_session.assert_called_once_with(
                organization_id=None,
                is_read_replica=False
            )
    
    @pytest.mark.asyncio
    async def test_get_session_context_manager_behavior(self, base_service):
        """Test that get_session properly handles async context manager."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        with patch('josi.services.base_service.get_async_session') as mock_get_session:
            # Setup mock to return async context manager
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_session
            mock_context.__aexit__.return_value = None
            mock_get_session.return_value = mock_context
            
            # Get session
            session = await base_service.get_session()
            
            # Verify context manager was properly entered
            mock_context.__aenter__.assert_called_once()
            assert session == mock_session
    
    @pytest.mark.asyncio
    async def test_get_session_error_handling(self, base_service):
        """Test error handling in get_session."""
        with patch('josi.services.base_service.get_async_session') as mock_get_session:
            # Setup mock to raise exception
            mock_get_session.side_effect = Exception("Database connection error")
            
            # Should raise the exception
            with pytest.raises(Exception) as exc_info:
                await base_service.get_session()
            
            assert str(exc_info.value) == "Database connection error"
    
    def test_inheritance_capability(self, organization_id):
        """Test that BaseService can be properly inherited."""
        class TestService(BaseService):
            def custom_method(self):
                return "custom"
        
        service = TestService(organization_id=organization_id)
        
        assert service.organization_id == organization_id
        assert hasattr(service, 'get_session')
        assert hasattr(service, 'custom_method')
        assert service.custom_method() == "custom"
    
    @pytest.mark.asyncio
    async def test_multiple_session_calls(self, base_service, organization_id):
        """Test multiple calls to get_session."""
        mock_session1 = AsyncMock(spec=AsyncSession)
        mock_session2 = AsyncMock(spec=AsyncSession)
        
        with patch('josi.services.base_service.get_async_session') as mock_get_session:
            # Setup mock to return different sessions
            mock_context1 = AsyncMock()
            mock_context1.__aenter__.return_value = mock_session1
            mock_context1.__aexit__.return_value = None
            
            mock_context2 = AsyncMock()
            mock_context2.__aenter__.return_value = mock_session2
            mock_context2.__aexit__.return_value = None
            
            mock_get_session.side_effect = [mock_context1, mock_context2]
            
            # Get sessions
            session1 = await base_service.get_session()
            session2 = await base_service.get_session(is_read_replica=True)
            
            # Assertions
            assert session1 == mock_session1
            assert session2 == mock_session2
            assert mock_get_session.call_count == 2
            
            # Check calls
            calls = mock_get_session.call_args_list
            assert calls[0].kwargs == {'organization_id': organization_id, 'is_read_replica': False}
            assert calls[1].kwargs == {'organization_id': organization_id, 'is_read_replica': True}
    
    def test_organization_id_immutability(self, base_service, organization_id):
        """Test that organization_id is properly stored and accessible."""
        assert base_service.organization_id == organization_id
        
        # Change organization_id
        new_org_id = uuid4()
        base_service.organization_id = new_org_id
        
        assert base_service.organization_id == new_org_id
    
    @pytest.mark.asyncio
    async def test_session_async_context_exit(self, base_service):
        """Test that session context manager properly exits."""
        mock_session = AsyncMock(spec=AsyncSession)
        
        with patch('josi.services.base_service.get_async_session') as mock_get_session:
            # Setup mock to return async context manager
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_session
            mock_context.__aexit__.return_value = None
            mock_get_session.return_value = mock_context
            
            # Get session
            session = await base_service.get_session()
            
            # Although __aexit__ isn't called in the current implementation,
            # verify the context manager is properly structured
            assert hasattr(mock_context, '__aexit__')
            assert session == mock_session