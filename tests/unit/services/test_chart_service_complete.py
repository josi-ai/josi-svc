"""Complete comprehensive unit tests for ChartService."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal

from josi.services.chart_service import ChartService
from josi.models.chart_model import AstrologyChart, AstrologySystem, HouseSystem, Ayanamsa
from josi.models.person_model import Person
from josi.repositories.person_repository import ChartRepository


class TestChartServiceComplete:
    """Complete comprehensive test coverage for ChartService."""
    
    @pytest.fixture
    def mock_chart_repository(self):
        """Create a mock chart repository."""
        repo = AsyncMock(spec=ChartRepository)
        repo.create = AsyncMock()
        repo.get = AsyncMock()
        repo.update = AsyncMock()
        repo.delete = AsyncMock()
        repo.soft_delete = AsyncMock()
        repo.get_multi = AsyncMock()
        repo.get_person_charts = AsyncMock()
        repo.get_latest_chart = AsyncMock()
        return repo
    
    @pytest.fixture
    def mock_astrology_calculator(self):
        """Create a mock astrology calculator."""
        calculator = MagicMock()
        calculator.calculate_planets = MagicMock(return_value={
            "sun": {"longitude": 120.5, "sign": "leo", "house": 5},
            "moon": {"longitude": 45.2, "sign": "taurus", "house": 1}
        })
        calculator.calculate_houses = MagicMock(return_value={
            "1": 0.0, "2": 30.0, "3": 60.0, "4": 90.0,
            "5": 120.0, "6": 150.0, "7": 180.0, "8": 210.0,
            "9": 240.0, "10": 270.0, "11": 300.0, "12": 330.0
        })
        calculator.calculate_aspects = MagicMock(return_value=[
            {"planet1": "sun", "planet2": "moon", "aspect": "trine", "orb": 2.3}
        ])
        return calculator
    
    @pytest.fixture
    def mock_panchang_calculator(self):
        """Create a mock panchang calculator."""
        calculator = MagicMock()
        calculator.calculate_panchang = MagicMock(return_value={
            "tithi": "Shukla Paksha Dwitiya",
            "nakshatra": "Rohini",
            "yoga": "Shobhana",
            "karana": "Balava",
            "vara": "Monday"
        })
        return calculator
    
    @pytest.fixture
    def mock_interpretation_engine(self):
        """Create a mock interpretation engine."""
        engine = MagicMock()
        engine.generate_interpretation = MagicMock(return_value={
            "interpretation_type": "general",
            "text": "This is a test interpretation",
            "confidence": 0.85,
            "language": "en"
        })
        return engine
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session
    
    @pytest.fixture
    def test_organization_id(self):
        """Test organization ID."""
        return uuid4()
    
    @pytest.fixture
    def chart_service(self, mock_db_session, test_organization_id, mock_chart_repository, 
                     mock_astrology_calculator, mock_panchang_calculator, mock_interpretation_engine):
        """Create a ChartService instance with mocked dependencies."""
        with patch('josi.services.chart_service.ChartRepository', return_value=mock_chart_repository):
            with patch('josi.services.chart_service.AstrologyCalculator', return_value=mock_astrology_calculator):
                with patch('josi.services.chart_service.PanchangCalculator', return_value=mock_panchang_calculator):
                    with patch('josi.services.chart_service.InterpretationEngine', return_value=mock_interpretation_engine):
                        service = ChartService(mock_db_session, test_organization_id)
                        # Override instances
                        service.chart_repo = mock_chart_repository
                        service.astrology_calculator = mock_astrology_calculator
                        service.panchang_calculator = mock_panchang_calculator
                        service.interpretation_engine = mock_interpretation_engine
                        return service
    
    @pytest.fixture
    def test_person(self, test_organization_id):
        """Create a test person."""
        return Person(
            person_id=uuid4(),
            organization_id=test_organization_id,
            name="John Doe",
            date_of_birth=date(1990, 1, 1),
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="New York, NY, USA",
            latitude=Decimal("40.7128"),
            longitude=Decimal("-74.0060"),
            timezone="America/New_York"
        )
    
    @pytest.fixture
    def test_chart(self, test_person, test_organization_id):
        """Create a test chart."""
        return AstrologyChart(
            chart_id=uuid4(),
            person_id=test_person.person_id,
            organization_id=test_organization_id,
            chart_type="natal",
            house_system="placidus",
            ayanamsa="lahiri",
            calculated_at=datetime.now(),
            calculation_version="1.0",
            chart_data={"planets": {}, "houses": {}}
        )
    
    @pytest.mark.asyncio
    async def test_calculate_charts_single_system(self, chart_service, test_person, mock_chart_repository):
        """Test calculating charts with single system."""
        systems = [AstrologySystem.VEDIC]
        
        # Mock chart creation
        created_chart = AstrologyChart(
            chart_id=uuid4(),
            person_id=test_person.person_id,
            organization_id=test_person.organization_id,
            chart_type="vedic",
            house_system="placidus",
            ayanamsa="lahiri",
            calculated_at=datetime.now(),
            calculation_version="1.0",
            chart_data={"planets": {}, "houses": {}}
        )
        mock_chart_repository.create.return_value = created_chart
        
        result = await chart_service.calculate_charts(
            person=test_person,
            systems=systems,
            house_system=HouseSystem.PLACIDUS,
            ayanamsa=Ayanamsa.LAHIRI
        )
        
        assert len(result) == 1
        assert result[0].chart_type == "vedic"
        mock_chart_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calculate_charts_multiple_systems(self, chart_service, test_person, mock_chart_repository):
        """Test calculating charts with multiple systems."""
        systems = [AstrologySystem.VEDIC, AstrologySystem.WESTERN, AstrologySystem.CHINESE]
        
        # Create different charts for each system
        created_charts = []
        for system in systems:
            chart = AstrologyChart(
                chart_id=uuid4(),
                person_id=test_person.person_id,
                organization_id=test_person.organization_id,
                chart_type=system.value,
                house_system="placidus",
                ayanamsa="lahiri" if system == AstrologySystem.VEDIC else None,
                calculated_at=datetime.now(),
                calculation_version="1.0",
                chart_data={"planets": {}, "houses": {}}
            )
            created_charts.append(chart)
        
        mock_chart_repository.create.side_effect = created_charts
        
        result = await chart_service.calculate_charts(
            person=test_person,
            systems=systems
        )
        
        assert len(result) == 3
        assert mock_chart_repository.create.call_count == 3
        
        # Verify each system was calculated
        chart_types = [chart.chart_type for chart in result]
        assert "vedic" in chart_types
        assert "western" in chart_types
        assert "chinese" in chart_types
    
    @pytest.mark.asyncio
    async def test_calculate_charts_with_interpretations(self, chart_service, test_person, mock_chart_repository, mock_interpretation_engine):
        """Test calculating charts with interpretations enabled."""
        systems = [AstrologySystem.VEDIC]
        
        created_chart = AstrologyChart(
            chart_id=uuid4(),
            person_id=test_person.person_id,
            organization_id=test_person.organization_id,
            chart_type="vedic",
            house_system="placidus",
            ayanamsa="lahiri",
            calculated_at=datetime.now(),
            calculation_version="1.0",
            chart_data={"planets": {}, "houses": {}}
        )
        mock_chart_repository.create.return_value = created_chart
        
        result = await chart_service.calculate_charts(
            person=test_person,
            systems=systems,
            include_interpretations=True
        )
        
        assert len(result) == 1
        # Verify interpretation was generated
        mock_interpretation_engine.generate_interpretation.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_chart_success(self, chart_service, mock_chart_repository, test_chart):
        """Test getting chart by ID."""
        chart_id = test_chart.chart_id
        
        mock_chart_repository.get.return_value = test_chart
        
        result = await chart_service.get_chart(chart_id)
        
        assert result == test_chart
        mock_chart_repository.get.assert_called_once_with(chart_id)
    
    @pytest.mark.asyncio
    async def test_get_chart_not_found(self, chart_service, mock_chart_repository):
        """Test getting non-existent chart."""
        chart_id = uuid4()
        
        mock_chart_repository.get.return_value = None
        
        result = await chart_service.get_chart(chart_id)
        
        assert result is None
        mock_chart_repository.get.assert_called_once_with(chart_id)
    
    @pytest.mark.asyncio
    async def test_update_chart_success(self, chart_service, mock_chart_repository, test_chart):
        """Test updating a chart."""
        chart_id = test_chart.chart_id
        update_data = {"house_system": "koch", "calculation_version": "2.0"}
        
        updated_chart = test_chart
        updated_chart.house_system = "koch"
        updated_chart.calculation_version = "2.0"
        
        mock_chart_repository.update.return_value = updated_chart
        
        result = await chart_service.update_chart(chart_id, update_data)
        
        assert result == updated_chart
        mock_chart_repository.update.assert_called_once_with(chart_id, update_data)
    
    @pytest.mark.asyncio
    async def test_delete_chart_success(self, chart_service, mock_chart_repository):
        """Test deleting a chart."""
        chart_id = uuid4()
        
        mock_chart_repository.soft_delete.return_value = True
        
        result = await chart_service.delete_chart(chart_id)
        
        assert result is True
        mock_chart_repository.soft_delete.assert_called_once_with(chart_id)
    
    @pytest.mark.asyncio
    async def test_get_person_charts_all(self, chart_service, mock_chart_repository, test_person, test_chart):
        """Test getting all charts for a person."""
        person_id = test_person.person_id
        charts = [test_chart]
        
        mock_chart_repository.get_person_charts.return_value = charts
        
        result = await chart_service.get_person_charts(person_id)
        
        assert result == charts
        mock_chart_repository.get_person_charts.assert_called_once_with(person_id, None)
    
    @pytest.mark.asyncio
    async def test_get_person_charts_by_type(self, chart_service, mock_chart_repository, test_person, test_chart):
        """Test getting charts for a person filtered by type."""
        person_id = test_person.person_id
        chart_type = "vedic"
        charts = [test_chart]
        
        mock_chart_repository.get_person_charts.return_value = charts
        
        result = await chart_service.get_person_charts(person_id, chart_type)
        
        assert result == charts
        mock_chart_repository.get_person_charts.assert_called_once_with(person_id, chart_type)
    
    @pytest.mark.asyncio
    async def test_list_charts_with_pagination(self, chart_service, mock_chart_repository, test_chart):
        """Test listing charts with pagination."""
        charts = [test_chart]
        
        mock_chart_repository.get_multi.return_value = charts
        
        result = await chart_service.list_charts(skip=10, limit=20)
        
        assert result == charts
        mock_chart_repository.get_multi.assert_called_once_with(skip=10, limit=20)
    
    @pytest.mark.asyncio
    async def test_get_latest_chart_success(self, chart_service, mock_chart_repository, test_person, test_chart):
        """Test getting latest chart of specific type."""
        person_id = test_person.person_id
        chart_type = "natal"
        
        mock_chart_repository.get_latest_chart.return_value = test_chart
        
        result = await chart_service.get_latest_chart(person_id, chart_type)
        
        assert result == test_chart
        mock_chart_repository.get_latest_chart.assert_called_once_with(person_id, chart_type)
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_db_session, test_organization_id):
        """Test ChartService initialization."""
        with patch('josi.services.chart_service.ChartRepository') as mock_repo_class:
            with patch('josi.services.chart_service.AstrologyCalculator'):
                with patch('josi.services.chart_service.PanchangCalculator'):
                    with patch('josi.services.chart_service.InterpretationEngine'):
                        service = ChartService(mock_db_session, test_organization_id)
                        
                        # Verify repository was initialized
                        mock_repo_class.assert_called_once_with(AstrologyChart, mock_db_session, test_organization_id)
                        
                        assert service.db == mock_db_session
                        assert service.organization_id == test_organization_id
                        assert hasattr(service, 'chart_repo')
                        assert hasattr(service, 'astrology_calculator')
                        assert hasattr(service, 'panchang_calculator')
                        assert hasattr(service, 'interpretation_engine')
    
    @pytest.mark.asyncio
    async def test_calculate_vedic_chart_details(self, chart_service, test_person, mock_chart_repository, mock_panchang_calculator):
        """Test calculating vedic chart with panchang details."""
        systems = [AstrologySystem.VEDIC]
        
        created_chart = AstrologyChart(
            chart_id=uuid4(),
            person_id=test_person.person_id,
            organization_id=test_person.organization_id,
            chart_type="vedic",
            house_system="whole_sign",
            ayanamsa="lahiri",
            calculated_at=datetime.now(),
            calculation_version="1.0",
            chart_data={
                "planets": {},
                "houses": {},
                "panchang": {
                    "tithi": "Shukla Paksha Dwitiya",
                    "nakshatra": "Rohini"
                }
            }
        )
        mock_chart_repository.create.return_value = created_chart
        
        result = await chart_service.calculate_charts(
            person=test_person,
            systems=systems,
            house_system=HouseSystem.WHOLE_SIGN
        )
        
        assert len(result) == 1
        assert result[0].chart_type == "vedic"
        assert result[0].house_system == "whole_sign"
        
        # Verify panchang was calculated for vedic chart
        mock_panchang_calculator.calculate_panchang.assert_called()
    
    @pytest.mark.asyncio
    async def test_calculate_chart_error_handling(self, chart_service, test_person, mock_astrology_calculator):
        """Test error handling during chart calculation."""
        systems = [AstrologySystem.VEDIC]
        
        # Mock calculation error
        mock_astrology_calculator.calculate_planets.side_effect = Exception("Calculation error")
        
        with pytest.raises(Exception, match="Calculation error"):
            await chart_service.calculate_charts(
                person=test_person,
                systems=systems
            )