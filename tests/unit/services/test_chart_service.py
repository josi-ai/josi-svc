"""Unit tests for ChartService."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
from decimal import Decimal

from josi.services.chart_service import ChartService
from josi.models.chart_model import AstrologyChart, ChartEntity
from josi.models.person_model import Person


class TestChartService:
    """Test ChartService functionality."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_person_repository(self):
        """Create a mock person repository."""
        repo = AsyncMock()
        return repo
    
    @pytest.fixture
    def mock_chart_repository(self):
        """Create a mock chart repository."""
        repo = AsyncMock()
        return repo
    
    @pytest.fixture
    def mock_astrology_service(self):
        """Create a mock astrology service."""
        service = AsyncMock()
        service.calculate_vedic_chart = AsyncMock(return_value={
            "houses": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "planets": {
                "Sun": {"longitude": 120.5, "sign": "Leo", "house": 5},
                "Moon": {"longitude": 45.2, "sign": "Taurus", "house": 2}
            },
            "ascendant": 30.0
        })
        return service
    
    @pytest.fixture
    def test_organization_id(self):
        """Test organization ID."""
        return uuid4()
    
    @pytest.fixture
    def test_person(self, test_organization_id):
        """Create a test person."""
        return Person(
            person_id=uuid4(),
            organization_id=test_organization_id,
            name="John Doe",
            date_of_birth=datetime(1990, 1, 1).date(),
            time_of_birth=datetime(1990, 1, 1, 12, 0, 0),
            place_of_birth="New York, NY, USA",
            latitude=Decimal("40.7128"),
            longitude=Decimal("-74.0060"),
            timezone="America/New_York"
        )
    
    @pytest.fixture
    def chart_service(self, mock_db_session, test_organization_id, mock_person_repository, mock_chart_repository, mock_astrology_service):
        """Create a ChartService instance."""
        with patch('josi.services.chart_service.PersonRepository', return_value=mock_person_repository):
            with patch('josi.services.chart_service.ChartRepository', return_value=mock_chart_repository):
                with patch('josi.services.chart_service.AstrologyService', return_value=mock_astrology_service):
                    service = ChartService(mock_db_session, test_organization_id)
                    service.person_repository = mock_person_repository
                    service.chart_repository = mock_chart_repository
                    service.astrology_service = mock_astrology_service
                    return service
    
    @pytest.mark.asyncio
    async def test_create_natal_chart(self, chart_service, mock_person_repository, mock_chart_repository, mock_astrology_service, test_person, test_organization_id):
        """Test creating a natal chart."""
        person_id = test_person.person_id
        
        # Mock person lookup
        mock_person_repository.get.return_value = test_person
        
        # Expected chart
        expected_chart = AstrologyChart(
            chart_id=uuid4(),
            organization_id=test_organization_id,
            person_id=person_id,
            chart_type="vedic",
            house_system="placidus",
            ayanamsa="lahiri",
            calculated_at=datetime.now(),
            calculation_version="1.0",
            chart_data={
                "houses": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                "planets": {
                    "Sun": {"longitude": 120.5, "sign": "Leo", "house": 5},
                    "Moon": {"longitude": 45.2, "sign": "Taurus", "house": 2}
                },
                "ascendant": 30.0
            }
        )
        
        # Mock repository response
        mock_chart_repository.create.return_value = expected_chart
        
        # Chart request data
        chart_data = ChartEntity(
            chart_type="vedic",
            house_system="placidus",
            ayanamsa="lahiri",
            calculated_at=datetime.now(),
            calculation_version="1.0"
        )
        
        # Call service
        result = await chart_service.create_chart(person_id, chart_data)
        
        # Verify person was fetched
        mock_person_repository.get.assert_called_once_with(person_id)
        
        # Verify astrology calculation was called
        mock_astrology_service.calculate_vedic_chart.assert_called_once()
        
        # Verify chart was created
        assert mock_chart_repository.create.called
        create_args = mock_chart_repository.create.call_args[0][0]
        assert create_args.person_id == person_id
        assert create_args.chart_type == "vedic"
        
        # Verify result
        assert result == expected_chart
    
    @pytest.mark.asyncio
    async def test_create_chart_person_not_found(self, chart_service, mock_person_repository):
        """Test creating a chart when person doesn't exist."""
        person_id = uuid4()
        
        # Mock person not found
        mock_person_repository.get.return_value = None
        
        # Chart request data
        chart_data = ChartEntity(
            chart_type="vedic",
            house_system="placidus",
            ayanamsa="lahiri",
            calculated_at=datetime.now(),
            calculation_version="1.0"
        )
        
        # Call service and expect exception
        with pytest.raises(ValueError, match="Person not found"):
            await chart_service.create_chart(person_id, chart_data)
    
    @pytest.mark.asyncio
    async def test_get_chart_by_id(self, chart_service, mock_chart_repository, test_organization_id):
        """Test getting a chart by ID."""
        chart_id = uuid4()
        
        # Expected chart
        expected_chart = AstrologyChart(
            chart_id=chart_id,
            organization_id=test_organization_id,
            person_id=uuid4(),
            chart_type="vedic",
            house_system="placidus",
            ayanamsa="lahiri",
            calculated_at=datetime.now(),
            calculation_version="1.0",
            chart_data={"test": "data"}
        )
        
        # Mock repository response
        mock_chart_repository.get.return_value = expected_chart
        
        # Call service
        result = await chart_service.get_chart(chart_id)
        
        # Verify repository was called
        mock_chart_repository.get.assert_called_once_with(chart_id)
        
        # Verify result
        assert result == expected_chart
    
    @pytest.mark.asyncio
    async def test_get_charts_by_person(self, chart_service, mock_chart_repository, test_person, test_organization_id):
        """Test getting all charts for a person."""
        person_id = test_person.person_id
        
        # Expected charts
        expected_charts = [
            AstrologyChart(
                chart_id=uuid4(),
                organization_id=test_organization_id,
                person_id=person_id,
                chart_type="vedic",
                house_system="placidus",
                ayanamsa="lahiri",
                calculated_at=datetime.now(),
                calculation_version="1.0",
                chart_data={"test": "data1"}
            ),
            AstrologyChart(
                chart_id=uuid4(),
                organization_id=test_organization_id,
                person_id=person_id,
                chart_type="western",
                house_system="placidus",
                calculated_at=datetime.now(),
                calculation_version="1.0",
                chart_data={"test": "data2"}
            )
        ]
        
        # Mock repository response
        mock_chart_repository.get_by_person.return_value = expected_charts
        
        # Call service
        result = await chart_service.get_charts_by_person(person_id)
        
        # Verify repository was called
        mock_chart_repository.get_by_person.assert_called_once_with(person_id)
        
        # Verify result
        assert result == expected_charts
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_delete_chart(self, chart_service, mock_chart_repository):
        """Test deleting a chart."""
        chart_id = uuid4()
        
        # Mock repository response
        mock_chart_repository.delete.return_value = True
        
        # Call service
        result = await chart_service.delete_chart(chart_id)
        
        # Verify repository was called
        mock_chart_repository.delete.assert_called_once_with(chart_id)
        
        # Verify result
        assert result is True
    
    @pytest.mark.asyncio
    async def test_calculate_western_chart(self, chart_service, mock_person_repository, mock_chart_repository, test_person):
        """Test creating a western chart."""
        person_id = test_person.person_id
        
        # Mock person lookup
        mock_person_repository.get.return_value = test_person
        
        # Mock western calculation
        with patch.object(chart_service.astrology_service, 'calculate_western_chart', return_value={
            "houses": [30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360],
            "planets": {
                "Sun": {"longitude": 120.5, "sign": "Leo", "house": 5},
                "Moon": {"longitude": 45.2, "sign": "Taurus", "house": 2}
            },
            "ascendant": 30.0
        }) as mock_western_calc:
            
            # Chart request data
            chart_data = ChartEntity(
                chart_type="western",
                house_system="placidus",
                calculated_at=datetime.now(),
                calculation_version="1.0"
            )
            
            # Expected chart
            expected_chart = AstrologyChart(
                chart_id=uuid4(),
                organization_id=test_person.organization_id,
                person_id=person_id,
                chart_type="western",
                house_system="placidus",
                calculated_at=datetime.now(),
                calculation_version="1.0",
                chart_data={}
            )
            
            # Mock repository response
            mock_chart_repository.create.return_value = expected_chart
            
            # Call service
            result = await chart_service.create_chart(person_id, chart_data)
            
            # Verify western calculation was called
            assert mock_western_calc.called
            
            # Verify result
            assert result == expected_chart