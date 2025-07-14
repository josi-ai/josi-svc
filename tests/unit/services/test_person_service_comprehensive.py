"""Comprehensive unit tests for Person service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from uuid import uuid4

from josi.services.person_service import PersonService
from josi.models.person_model import Person


class TestPersonServiceComprehensive:
    """Comprehensive test coverage for PersonService."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock all dependencies."""
        return {
            'person_repository': AsyncMock(),
            'geocoding_service': MagicMock(),
            'organization_id': str(uuid4())
        }
    
    @pytest.fixture
    def person_service(self, mock_dependencies):
        """Create PersonService with mocked dependencies."""
        return PersonService(
            person_repository=mock_dependencies['person_repository'],
            geocoding_service=mock_dependencies['geocoding_service']
        )
    
    @pytest.fixture
    def test_person_data(self):
        """Test person data for creation."""
        return {
            'first_name': 'John',
            'last_name': 'Doe',
            'birth_date': datetime(1990, 1, 1),
            'birth_time': datetime(1990, 1, 1, 12, 0, 0),
            'birth_place_city': 'New York',
            'birth_place_state': 'NY',
            'birth_place_country': 'USA',
            'email': 'john.doe@example.com',
            'phone': '+1234567890'
        }
    
    @pytest.fixture
    def test_person(self, test_person_data, mock_dependencies):
        """Test person instance."""
        return Person(
            person_id=str(uuid4()),
            **test_person_data,
            latitude=40.7128,
            longitude=-74.0060,
            timezone='America/New_York',
            organization_id=mock_dependencies['organization_id']
        )
    
    @pytest.mark.asyncio
    async def test_create_person_with_geocoding(self, person_service, mock_dependencies, test_person_data):
        """Test creating a person with geocoding."""
        # Setup mocks
        mock_dependencies['geocoding_service'].get_coordinates_and_timezone.return_value = (
            40.7128, -74.0060, 'America/New_York'
        )
        
        created_person = Person(
            person_id=str(uuid4()),
            **test_person_data,
            latitude=40.7128,
            longitude=-74.0060,
            timezone='America/New_York',
            organization_id=mock_dependencies['organization_id']
        )
        mock_dependencies['person_repository'].create.return_value = created_person
        
        # Test
        result = await person_service.create_person(
            test_person_data,
            organization_id=mock_dependencies['organization_id']
        )
        
        # Assertions
        assert result.person_id is not None
        assert result.latitude == 40.7128
        assert result.longitude == -74.0060
        assert result.timezone == 'America/New_York'
        
        mock_dependencies['geocoding_service'].get_coordinates_and_timezone.assert_called_once_with(
            city='New York',
            state='NY',
            country='USA'
        )
        mock_dependencies['person_repository'].create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_person_with_existing_coordinates(self, person_service, mock_dependencies, test_person_data):
        """Test creating a person with pre-existing coordinates."""
        # Add coordinates to test data
        test_person_data['latitude'] = 40.7128
        test_person_data['longitude'] = -74.0060
        test_person_data['timezone'] = 'America/New_York'
        
        created_person = Person(
            person_id=str(uuid4()),
            **test_person_data,
            organization_id=mock_dependencies['organization_id']
        )
        mock_dependencies['person_repository'].create.return_value = created_person
        
        # Test
        result = await person_service.create_person(
            test_person_data,
            organization_id=mock_dependencies['organization_id']
        )
        
        # Should not call geocoding service
        mock_dependencies['geocoding_service'].get_coordinates_and_timezone.assert_not_called()
        assert result.latitude == 40.7128
    
    @pytest.mark.asyncio
    async def test_create_person_geocoding_failure(self, person_service, mock_dependencies, test_person_data):
        """Test creating a person when geocoding fails."""
        # Setup mock to raise exception
        mock_dependencies['geocoding_service'].get_coordinates_and_timezone.side_effect = ValueError(
            "Could not find location"
        )
        
        # Test - should raise the geocoding error
        with pytest.raises(ValueError, match="Could not find location"):
            await person_service.create_person(
                test_person_data,
                organization_id=mock_dependencies['organization_id']
            )
    
    @pytest.mark.asyncio
    async def test_create_person_minimal_data(self, person_service, mock_dependencies):
        """Test creating a person with minimal required data."""
        minimal_data = {
            'first_name': 'Jane',
            'birth_date': datetime(1995, 5, 15)
        }
        
        created_person = Person(
            person_id=str(uuid4()),
            **minimal_data,
            organization_id=mock_dependencies['organization_id']
        )
        mock_dependencies['person_repository'].create.return_value = created_person
        
        # Test
        result = await person_service.create_person(
            minimal_data,
            organization_id=mock_dependencies['organization_id']
        )
        
        assert result.first_name == 'Jane'
        assert result.birth_date == datetime(1995, 5, 15)
        # Should not attempt geocoding without location data
        mock_dependencies['geocoding_service'].get_coordinates_and_timezone.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_person(self, person_service, mock_dependencies, test_person):
        """Test getting a person by ID."""
        mock_dependencies['person_repository'].get.return_value = test_person
        
        result = await person_service.get_person(
            person_id=test_person.person_id,
            organization_id=test_person.organization_id
        )
        
        assert result == test_person
        mock_dependencies['person_repository'].get.assert_called_once_with(
            test_person.person_id
        )
    
    @pytest.mark.asyncio
    async def test_get_person_not_found(self, person_service, mock_dependencies):
        """Test getting a non-existent person."""
        mock_dependencies['person_repository'].get.return_value = None
        
        result = await person_service.get_person(
            person_id=str(uuid4()),
            organization_id=str(uuid4())
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_person(self, person_service, mock_dependencies, test_person):
        """Test updating a person."""
        update_data = {
            'email': 'newemail@example.com',
            'phone': '+9876543210'
        }
        
        updated_person = test_person.model_copy()
        updated_person.email = update_data['email']
        updated_person.phone = update_data['phone']
        
        mock_dependencies['person_repository'].get.return_value = test_person
        mock_dependencies['person_repository'].update.return_value = updated_person
        
        # Test
        result = await person_service.update_person(
            person_id=test_person.person_id,
            update_data=update_data,
            organization_id=test_person.organization_id
        )
        
        assert result.email == 'newemail@example.com'
        assert result.phone == '+9876543210'
    
    @pytest.mark.asyncio
    async def test_update_person_location(self, person_service, mock_dependencies, test_person):
        """Test updating a person's location."""
        update_data = {
            'birth_place_city': 'Los Angeles',
            'birth_place_state': 'CA',
            'birth_place_country': 'USA'
        }
        
        mock_dependencies['geocoding_service'].get_coordinates_and_timezone.return_value = (
            34.0522, -118.2437, 'America/Los_Angeles'
        )
        
        updated_person = test_person.model_copy()
        updated_person.birth_place_city = 'Los Angeles'
        updated_person.birth_place_state = 'CA'
        updated_person.latitude = 34.0522
        updated_person.longitude = -118.2437
        updated_person.timezone = 'America/Los_Angeles'
        
        mock_dependencies['person_repository'].get.return_value = test_person
        mock_dependencies['person_repository'].update.return_value = updated_person
        
        # Test
        result = await person_service.update_person(
            person_id=test_person.person_id,
            update_data=update_data,
            organization_id=test_person.organization_id
        )
        
        assert result.latitude == 34.0522
        assert result.longitude == -118.2437
        assert result.timezone == 'America/Los_Angeles'
        
        # Should have called geocoding service
        mock_dependencies['geocoding_service'].get_coordinates_and_timezone.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_person_not_found(self, person_service, mock_dependencies):
        """Test updating a non-existent person."""
        mock_dependencies['person_repository'].get.return_value = None
        
        with pytest.raises(ValueError, match="Person not found"):
            await person_service.update_person(
                person_id=str(uuid4()),
                update_data={'email': 'test@example.com'},
                organization_id=str(uuid4())
            )
    
    @pytest.mark.asyncio
    async def test_delete_person(self, person_service, mock_dependencies, test_person):
        """Test deleting a person."""
        mock_dependencies['person_repository'].get.return_value = test_person
        mock_dependencies['person_repository'].soft_delete.return_value = True
        
        result = await person_service.delete_person(
            person_id=test_person.person_id,
            organization_id=test_person.organization_id
        )
        
        assert result is True
        mock_dependencies['person_repository'].soft_delete.assert_called_once_with(
            test_person.person_id
        )
    
    @pytest.mark.asyncio
    async def test_delete_person_not_found(self, person_service, mock_dependencies):
        """Test deleting a non-existent person."""
        mock_dependencies['person_repository'].get.return_value = None
        
        with pytest.raises(ValueError, match="Person not found"):
            await person_service.delete_person(
                person_id=str(uuid4()),
                organization_id=str(uuid4())
            )
    
    @pytest.mark.asyncio
    async def test_list_persons(self, person_service, mock_dependencies, test_person):
        """Test listing persons with pagination."""
        mock_dependencies['person_repository'].list.return_value = [test_person]
        
        result = await person_service.list_persons(
            organization_id=test_person.organization_id,
            skip=0,
            limit=10
        )
        
        assert len(result) == 1
        assert result[0] == test_person
        mock_dependencies['person_repository'].list.assert_called_once_with(
            skip=0,
            limit=10,
            filters={}
        )
    
    @pytest.mark.asyncio
    async def test_list_persons_with_filters(self, person_service, mock_dependencies, test_person):
        """Test listing persons with filters."""
        filters = {
            'first_name': 'John',
            'birth_date__gte': datetime(1990, 1, 1),
            'birth_date__lte': datetime(2000, 12, 31)
        }
        
        mock_dependencies['person_repository'].list.return_value = [test_person]
        
        result = await person_service.list_persons(
            organization_id=test_person.organization_id,
            skip=0,
            limit=10,
            filters=filters
        )
        
        assert len(result) == 1
        mock_dependencies['person_repository'].list.assert_called_once_with(
            skip=0,
            limit=10,
            filters=filters
        )
    
    @pytest.mark.asyncio
    async def test_search_persons(self, person_service, mock_dependencies, test_person):
        """Test searching persons by name."""
        search_query = "John"
        
        mock_dependencies['person_repository'].search_by_name.return_value = [test_person]
        
        result = await person_service.search_persons(
            query=search_query,
            organization_id=test_person.organization_id
        )
        
        assert len(result) == 1
        assert result[0] == test_person
        mock_dependencies['person_repository'].search_by_name.assert_called_once_with(
            search_query
        )
    
    @pytest.mark.asyncio
    async def test_get_persons_by_birth_date(self, person_service, mock_dependencies, test_person):
        """Test getting persons by birth date."""
        birth_date = datetime(1990, 1, 1)
        
        mock_dependencies['person_repository'].get_by_birth_date.return_value = [test_person]
        
        result = await person_service.get_persons_by_birth_date(
            birth_date=birth_date,
            organization_id=test_person.organization_id
        )
        
        assert len(result) == 1
        assert result[0] == test_person
    
    @pytest.mark.asyncio
    async def test_validate_person_data(self, person_service, test_person_data):
        """Test person data validation."""
        # Valid data should pass
        is_valid = person_service.validate_person_data(test_person_data)
        assert is_valid is True
        
        # Missing required field
        invalid_data = test_person_data.copy()
        del invalid_data['first_name']
        
        with pytest.raises(ValueError, match="First name is required"):
            person_service.validate_person_data(invalid_data)
        
        # Invalid email format
        invalid_data = test_person_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        with pytest.raises(ValueError, match="Invalid email format"):
            person_service.validate_person_data(invalid_data)
    
    @pytest.mark.asyncio
    async def test_calculate_age(self, person_service, test_person):
        """Test age calculation."""
        current_date = datetime(2024, 1, 1)
        
        age = person_service.calculate_age(test_person.birth_date, current_date)
        
        assert age == 34  # Born in 1990, current year 2024
    
    @pytest.mark.asyncio
    async def test_merge_duplicate_persons(self, person_service, mock_dependencies, test_person):
        """Test merging duplicate person records."""
        duplicate_person = test_person.model_copy()
        duplicate_person.person_id = str(uuid4())
        duplicate_person.email = 'duplicate@example.com'
        
        mock_dependencies['person_repository'].get.side_effect = [test_person, duplicate_person]
        mock_dependencies['person_repository'].update.return_value = test_person
        mock_dependencies['person_repository'].hard_delete.return_value = True
        
        result = await person_service.merge_persons(
            primary_id=test_person.person_id,
            duplicate_id=duplicate_person.person_id,
            organization_id=test_person.organization_id
        )
        
        assert result == test_person
        # Should have deleted the duplicate
        mock_dependencies['person_repository'].hard_delete.assert_called_once_with(
            duplicate_person.person_id
        )
    
    @pytest.mark.asyncio
    async def test_export_person_data(self, person_service, mock_dependencies, test_person):
        """Test exporting person data."""
        mock_dependencies['person_repository'].get.return_value = test_person
        
        # Mock chart repository to get person's charts
        with patch('josi.services.person_service.ChartRepository') as mock_chart_repo:
            mock_chart_instance = AsyncMock()
            mock_chart_repo.return_value = mock_chart_instance
            mock_chart_instance.get_by_person.return_value = []
            
            export_data = await person_service.export_person_data(
                person_id=test_person.person_id,
                organization_id=test_person.organization_id,
                include_charts=True
            )
            
            assert 'person' in export_data
            assert 'charts' in export_data
            assert export_data['person']['person_id'] == str(test_person.person_id)
    
    @pytest.mark.asyncio
    async def test_import_person_data(self, person_service, mock_dependencies):
        """Test importing person data."""
        import_data = {
            'person': {
                'first_name': 'Imported',
                'last_name': 'Person',
                'birth_date': '1995-05-15T00:00:00',
                'birth_place_city': 'Boston',
                'birth_place_state': 'MA',
                'birth_place_country': 'USA'
            }
        }
        
        mock_dependencies['geocoding_service'].get_coordinates_and_timezone.return_value = (
            42.3601, -71.0589, 'America/New_York'
        )
        
        created_person = Person(
            person_id=str(uuid4()),
            first_name='Imported',
            last_name='Person',
            birth_date=datetime(1995, 5, 15),
            birth_place_city='Boston',
            birth_place_state='MA',
            birth_place_country='USA',
            latitude=42.3601,
            longitude=-71.0589,
            timezone='America/New_York',
            organization_id=mock_dependencies['organization_id']
        )
        mock_dependencies['person_repository'].create.return_value = created_person
        
        result = await person_service.import_person_data(
            import_data=import_data,
            organization_id=mock_dependencies['organization_id']
        )
        
        assert result.first_name == 'Imported'
        assert result.last_name == 'Person'
    
    @pytest.mark.asyncio
    async def test_batch_create_persons(self, person_service, mock_dependencies):
        """Test batch creation of multiple persons."""
        persons_data = [
            {
                'first_name': 'Person1',
                'birth_date': datetime(1990, 1, 1)
            },
            {
                'first_name': 'Person2',
                'birth_date': datetime(1991, 2, 2)
            },
            {
                'first_name': 'Person3',
                'birth_date': datetime(1992, 3, 3)
            }
        ]
        
        created_persons = []
        for data in persons_data:
            person = Person(
                person_id=str(uuid4()),
                **data,
                organization_id=mock_dependencies['organization_id']
            )
            created_persons.append(person)
        
        mock_dependencies['person_repository'].create.side_effect = created_persons
        
        results = await person_service.batch_create_persons(
            persons_data=persons_data,
            organization_id=mock_dependencies['organization_id']
        )
        
        assert len(results) == 3
        assert all(r.person_id is not None for r in results)
        assert mock_dependencies['person_repository'].create.call_count == 3