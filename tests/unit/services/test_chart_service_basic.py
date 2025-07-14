"""Basic unit tests for Chart service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import uuid4
import json

from josi.models.chart_model import AstrologyChart, AstrologySystem, HouseSystem
from josi.models.person_model import Person


class TestChartServiceBasic:
    """Basic test coverage for ChartService."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def organization_id(self):
        """Test organization ID."""
        return uuid4()
    
    @pytest.fixture
    def test_person(self, organization_id):
        """Test person instance."""
        return Person(
            person_id=uuid4(),
            name="John Doe",
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="New York, NY",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
            organization_id=organization_id
        )
    
    @pytest.fixture
    def test_chart(self, test_person, organization_id):
        """Test chart instance."""
        return AstrologyChart(
            chart_id=uuid4(),
            person_id=test_person.person_id,
            chart_type="natal",
            calculation_time=datetime.utcnow(),
            astrology_system=AstrologySystem.WESTERN,
            house_system=HouseSystem.PLACIDUS,
            chart_data={"test": "data"},
            organization_id=organization_id
        )
    
    @pytest.mark.asyncio
    async def test_chart_service_initialization(self, mock_db_session, organization_id):
        """Test ChartService initialization."""
        from josi.services.chart_service import ChartService
        
        service = ChartService(db=mock_db_session, organization_id=organization_id)
        
        assert service.db == mock_db_session
        assert service.organization_id == organization_id
        assert hasattr(service, 'chart_repo')
        assert hasattr(service, 'astrology_calculator')
        assert hasattr(service, 'panchang_calculator')
        assert hasattr(service, 'interpretation_engine')
    
    @pytest.mark.asyncio
    async def test_calculate_charts_western(self, mock_db_session, organization_id, test_person):
        """Test Western chart calculation."""
        from josi.services.chart_service import ChartService
        
        service = ChartService(db=mock_db_session, organization_id=organization_id)
        
        # Mock the calculator
        with patch.object(service.astrology_calculator, 'calculate_western_chart') as mock_calc:
            mock_calc.return_value = {
                'chart_type': 'western',
                'planets': {'Sun': {'longitude': 280.0}},
                'houses': [0.0] * 12,
                'ascendant': {'longitude': 0.0}
            }
            
            # Mock repository save
            with patch.object(service.chart_repo, 'create') as mock_create:
                mock_create.return_value = MagicMock(chart_id=uuid4())
                
                # Calculate chart
                charts = await service.calculate_charts(
                    person=test_person,
                    systems=[AstrologySystem.WESTERN],
                    house_system=HouseSystem.PLACIDUS,
                    include_interpretations=False
                )
                
                # Assertions
                assert len(charts) == 1
                assert charts[0].astrology_system == AstrologySystem.WESTERN
                mock_calc.assert_called_once()
                mock_create.assert_called()
    
    @pytest.mark.asyncio
    async def test_calculate_charts_vedic(self, mock_db_session, organization_id, test_person):
        """Test Vedic chart calculation."""
        from josi.services.chart_service import ChartService
        
        service = ChartService(db=mock_db_session, organization_id=organization_id)
        
        # Mock the calculator
        with patch.object(service.astrology_calculator, 'calculate_vedic_chart') as mock_calc:
            mock_calc.return_value = {
                'chart_type': 'vedic',
                'ayanamsa': 24.0,
                'planets': {'Sun': {'longitude': 256.0}},
                'houses': [0.0] * 12,
                'ascendant': {'longitude': 0.0}
            }
            
            # Mock repository save
            with patch.object(service.chart_repo, 'create') as mock_create:
                mock_create.return_value = MagicMock(chart_id=uuid4())
                
                # Calculate chart
                charts = await service.calculate_charts(
                    person=test_person,
                    systems=[AstrologySystem.VEDIC],
                    house_system=HouseSystem.WHOLE_SIGN,
                    include_interpretations=False
                )
                
                # Assertions
                assert len(charts) == 1
                assert charts[0].astrology_system == AstrologySystem.VEDIC
                mock_calc.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_chart_by_id(self, mock_db_session, organization_id, test_chart):
        """Test getting chart by ID."""
        from josi.services.chart_service import ChartService
        
        service = ChartService(db=mock_db_session, organization_id=organization_id)
        
        # Mock repository
        with patch.object(service.chart_repo, 'get') as mock_get:
            mock_get.return_value = test_chart
            
            # Get chart
            chart = await service.get_chart_by_id(test_chart.chart_id)
            
            # Assertions
            assert chart == test_chart
            mock_get.assert_called_once_with(test_chart.chart_id)
    
    @pytest.mark.asyncio
    async def test_get_person_charts(self, mock_db_session, organization_id, test_person, test_chart):
        """Test getting person's charts."""
        from josi.services.chart_service import ChartService
        
        service = ChartService(db=mock_db_session, organization_id=organization_id)
        
        # Mock repository
        with patch.object(service.chart_repo, 'get_multi') as mock_get_multi:
            mock_get_multi.return_value = [test_chart]
            
            # Get charts
            charts = await service.get_person_charts(test_person.person_id)
            
            # Assertions
            assert len(charts) == 1
            assert charts[0] == test_chart
            mock_get_multi.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_chart(self, mock_db_session, organization_id, test_chart):
        """Test chart deletion."""
        from josi.services.chart_service import ChartService
        
        service = ChartService(db=mock_db_session, organization_id=organization_id)
        
        # Mock repository
        with patch.object(service.chart_repo, 'get') as mock_get:
            with patch.object(service.chart_repo, 'delete') as mock_delete:
                mock_get.return_value = test_chart
                mock_delete.return_value = True
                
                # Delete chart
                result = await service.delete_chart(test_chart.chart_id)
                
                # Assertions
                assert result is True
                mock_get.assert_called_once_with(test_chart.chart_id)
                mock_delete.assert_called_once()