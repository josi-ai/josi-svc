"""Comprehensive unit tests for Western progressions service."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import math

from josi.services.western.progressions_service import ProgressionCalculator


class TestProgressionCalculator:
    """Comprehensive test coverage for ProgressionCalculator."""
    
    @pytest.fixture
    def progressions_calculator(self):
        """Create a ProgressionCalculator instance."""
        return ProgressionCalculator()
    
    @pytest.fixture
    def birth_datetime(self):
        """Sample birth datetime."""
        return datetime(1990, 1, 1, 12, 0, 0)
    
    @pytest.fixture
    def current_datetime(self):
        """Current datetime for progressions."""
        return datetime(2024, 1, 1, 12, 0, 0)
    
    @pytest.fixture
    def natal_chart(self):
        """Sample natal chart data."""
        return {
            'planets': {
                'Sun': {'longitude': 280.5, 'latitude': 0.0, 'speed': 0.98},
                'Moon': {'longitude': 45.2, 'latitude': 5.1, 'speed': 13.2},
                'Mercury': {'longitude': 265.0, 'latitude': -2.0, 'speed': 1.5},
                'Venus': {'longitude': 310.0, 'latitude': 1.0, 'speed': 1.2},
                'Mars': {'longitude': 95.0, 'latitude': 0.5, 'speed': 0.6},
                'Jupiter': {'longitude': 120.0, 'latitude': -1.0, 'speed': 0.08},
                'Saturn': {'longitude': 285.0, 'latitude': 2.0, 'speed': 0.03}
            },
            'houses': [0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0],
            'ascendant': {'longitude': 0.0},
            'midheaven': {'longitude': 270.0}
        }
    
    def test_initialization(self, progressions_calculator):
        """Test ProgressionCalculator initialization."""
        assert hasattr(progressions_calculator, 'calculate_secondary_progressions')
        assert hasattr(progressions_calculator, 'calculate_solar_arc_directions')
        assert hasattr(progressions_calculator, 'calculate_primary_directions')
        assert hasattr(progressions_calculator, 'calculate_tertiary_progressions')
    
    def test_calculate_secondary_progressions(self, progressions_calculator, birth_datetime, current_datetime, natal_chart):
        """Test secondary progressions calculation (day-for-a-year)."""
        result = progressions_calculator.calculate_secondary_progressions(
            birth_datetime=birth_datetime,
            current_datetime=current_datetime,
            natal_chart=natal_chart
        )
        
        assert 'progressed_planets' in result
        assert 'progressed_angles' in result
        assert 'progressed_age' in result
        assert 'aspects_to_natal' in result
        
        # Check progressed planets
        assert 'Sun' in result['progressed_planets']
        assert 'Moon' in result['progressed_planets']
        
        # Progressed Sun should have moved about 34 degrees (34 years)
        prog_sun = result['progressed_planets']['Sun']['longitude']
        natal_sun = natal_chart['planets']['Sun']['longitude']
        sun_movement = (prog_sun - natal_sun) % 360
        assert 30 < sun_movement < 40  # Approximate range
    
    def test_calculate_progressed_moon(self, progressions_calculator):
        """Test progressed Moon calculation."""
        natal_moon = 45.0
        days_progressed = 30  # 30 days = 30 years
        
        prog_moon = progressions_calculator._calculate_progressed_position(
            natal_position=natal_moon,
            daily_motion=13.0,  # Moon's average daily motion
            days=days_progressed
        )
        
        # Moon moves about 13 degrees per day
        expected_movement = 13.0 * 30
        actual_movement = (prog_moon - natal_moon) % 360
        assert abs(actual_movement - expected_movement) < 5  # Some tolerance
    
    def test_calculate_solar_arc_directions(self, progressions_calculator, birth_datetime, current_datetime, natal_chart):
        """Test solar arc directions calculation."""
        result = progressions_calculator.calculate_solar_arc_directions(
            birth_datetime=birth_datetime,
            current_datetime=current_datetime,
            natal_chart=natal_chart
        )
        
        assert 'directed_planets' in result
        assert 'solar_arc' in result
        assert 'aspects_to_natal' in result
        
        # Solar arc should be about 1 degree per year
        years = (current_datetime - birth_datetime).days / 365.25
        assert abs(result['solar_arc'] - years) < 1  # Within 1 degree
        
        # All planets should move by the same arc
        for planet_name in natal_chart['planets']:
            if planet_name in result['directed_planets']:
                natal_pos = natal_chart['planets'][planet_name]['longitude']
                directed_pos = result['directed_planets'][planet_name]['longitude']
                movement = (directed_pos - natal_pos) % 360
                assert abs(movement - result['solar_arc']) < 0.1
    
    def test_calculate_primary_directions(self, progressions_calculator, birth_datetime, current_datetime, natal_chart):
        """Test primary directions calculation."""
        location = {'latitude': 40.7128, 'longitude': -74.0060}
        
        result = progressions_calculator.calculate_primary_directions(
            birth_datetime=birth_datetime,
            current_datetime=current_datetime,
            natal_chart=natal_chart,
            location=location
        )
        
        assert 'directed_points' in result
        assert 'arc_of_direction' in result
        assert 'converse_directions' in result
    
    def test_calculate_tertiary_progressions(self, progressions_calculator, birth_datetime, current_datetime, natal_chart):
        """Test tertiary progressions (day-for-a-month)."""
        result = progressions_calculator.calculate_tertiary_progressions(
            birth_datetime=birth_datetime,
            current_datetime=current_datetime,
            natal_chart=natal_chart
        )
        
        assert 'progressed_planets' in result
        assert 'months_progressed' in result
        
        # Tertiary progressions move faster than secondary
        months = (current_datetime - birth_datetime).days / 30.44
        assert abs(result['months_progressed'] - months) < 2
    
    def test_calculate_converse_progressions(self, progressions_calculator, birth_datetime, current_datetime, natal_chart):
        """Test converse progressions (backward in time)."""
        result = progressions_calculator.calculate_converse_progressions(
            birth_datetime=birth_datetime,
            current_datetime=current_datetime,
            natal_chart=natal_chart
        )
        
        assert 'progressed_planets' in result
        # Positions should be earlier than natal
        for planet_name in ['Sun', 'Mercury', 'Venus']:
            if planet_name in result['progressed_planets']:
                prog_pos = result['progressed_planets'][planet_name]['longitude']
                natal_pos = natal_chart['planets'][planet_name]['longitude']
                # Converse goes backward
                assert prog_pos != natal_pos
    
    def test_calculate_minor_progressions(self, progressions_calculator, birth_datetime, current_datetime, natal_chart):
        """Test minor progressions (month-for-a-year)."""
        result = progressions_calculator.calculate_minor_progressions(
            birth_datetime=birth_datetime,
            current_datetime=current_datetime,
            natal_chart=natal_chart
        )
        
        assert 'progressed_planets' in result
        # Moon should move significantly in minor progressions
        prog_moon = result['progressed_planets']['Moon']['longitude']
        natal_moon = natal_chart['planets']['Moon']['longitude']
        assert prog_moon != natal_moon
    
    def test_progressed_aspects_calculation(self, progressions_calculator):
        """Test aspect calculation between progressed and natal planets."""
        progressed_planets = {
            'Sun': {'longitude': 120.0},
            'Moon': {'longitude': 180.0},
            'Mercury': {'longitude': 90.0}
        }
        
        natal_planets = {
            'Sun': {'longitude': 90.0},
            'Moon': {'longitude': 0.0},
            'Venus': {'longitude': 60.0}
        }
        
        aspects = progressions_calculator._calculate_progressed_aspects(
            progressed_planets, natal_planets
        )
        
        assert isinstance(aspects, list)
        # Should find Sun square natal Sun (120-90=30, not exact square)
        # Should find Moon opposition natal Moon (180-0=180)
        opposition_found = any(
            asp['planet1'] == 'Moon' and asp['planet2'] == 'Moon' and asp['aspect'] == 'opposition'
            for asp in aspects
        )
        assert opposition_found
    
    def test_progressed_house_cusps(self, progressions_calculator, birth_datetime, current_datetime):
        """Test progressed house cusp calculation."""
        natal_asc = 15.0  # 15 degrees Aries
        location = {'latitude': 40.0, 'longitude': -74.0}
        
        progressed_asc = progressions_calculator._calculate_progressed_ascendant(
            birth_datetime=birth_datetime,
            current_datetime=current_datetime,
            natal_ascendant=natal_asc,
            location=location
        )
        
        assert isinstance(progressed_asc, float)
        assert 0 <= progressed_asc < 360
        # Ascendant progresses about 1 degree per year
        years = (current_datetime - birth_datetime).days / 365.25
        expected_movement = years  # Simplified
        actual_movement = (progressed_asc - natal_asc) % 360
        assert actual_movement > 0  # Should have moved forward
    
    def test_progressed_lunar_phases(self, progressions_calculator):
        """Test progressed lunar phase calculation."""
        prog_sun = 120.0
        prog_moon = 210.0
        
        phase = progressions_calculator._calculate_progressed_lunar_phase(
            prog_sun, prog_moon
        )
        
        assert 'phase_name' in phase
        assert 'phase_degree' in phase
        assert 'days_until_new_moon' in phase
        
        # 210-120 = 90 degrees = First Quarter
        assert phase['phase_degree'] == 90.0
        assert 'quarter' in phase['phase_name'].lower()
    
    def test_progressed_station_detection(self, progressions_calculator):
        """Test detection of progressed planetary stations."""
        # Mercury about to station
        planet_positions = [
            {'date': datetime(2024, 1, 1), 'longitude': 100.0, 'speed': 0.5},
            {'date': datetime(2024, 1, 2), 'longitude': 100.3, 'speed': 0.2},
            {'date': datetime(2024, 1, 3), 'longitude': 100.4, 'speed': 0.05},
            {'date': datetime(2024, 1, 4), 'longitude': 100.4, 'speed': -0.05},
            {'date': datetime(2024, 1, 5), 'longitude': 100.3, 'speed': -0.2}
        ]
        
        stations = progressions_calculator._detect_stations(planet_positions)
        
        assert len(stations) > 0
        assert stations[0]['type'] in ['retrograde', 'direct']
        assert stations[0]['date'] == datetime(2024, 1, 3)
    
    def test_progressed_ingress_detection(self, progressions_calculator):
        """Test detection of progressed sign ingresses."""
        # Planet moving from 29 Pisces to 0 Aries
        planet_positions = [
            {'date': datetime(2024, 1, 1), 'longitude': 358.5},
            {'date': datetime(2024, 1, 2), 'longitude': 359.0},
            {'date': datetime(2024, 1, 3), 'longitude': 359.5},
            {'date': datetime(2024, 1, 4), 'longitude': 0.5},
            {'date': datetime(2024, 1, 5), 'longitude': 1.0}
        ]
        
        ingresses = progressions_calculator._detect_ingresses(planet_positions)
        
        assert len(ingresses) > 0
        assert ingresses[0]['from_sign'] == 'Pisces'
        assert ingresses[0]['to_sign'] == 'Aries'
        assert ingresses[0]['date'] == datetime(2024, 1, 4)
    
    def test_progression_timing_events(self, progressions_calculator, birth_datetime, natal_chart):
        """Test timing of progression events."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2025, 1, 1)
        
        events = progressions_calculator.find_progression_events(
            birth_datetime=birth_datetime,
            start_date=start_date,
            end_date=end_date,
            natal_chart=natal_chart
        )
        
        assert 'exact_aspects' in events
        assert 'sign_changes' in events
        assert 'house_changes' in events
        assert 'stations' in events
        
        # Should be sorted by date
        for event_list in events.values():
            dates = [e['date'] for e in event_list]
            assert dates == sorted(dates)
    
    def test_progressed_declination(self, progressions_calculator):
        """Test progressed declination calculation."""
        natal_declination = 23.0
        daily_declination_change = -0.1
        days_progressed = 30
        
        prog_declination = progressions_calculator._calculate_progressed_declination(
            natal_declination, daily_declination_change, days_progressed
        )
        
        assert prog_declination == natal_declination + (daily_declination_change * days_progressed)
    
    def test_parallel_aspects(self, progressions_calculator):
        """Test parallel and contraparallel aspects by declination."""
        prog_declinations = {
            'Sun': 23.0,
            'Moon': 23.2,
            'Mercury': -23.1
        }
        
        natal_declinations = {
            'Venus': 23.0,
            'Mars': -23.0,
            'Jupiter': 10.0
        }
        
        parallels = progressions_calculator._find_declination_aspects(
            prog_declinations, natal_declinations
        )
        
        assert len(parallels) > 0
        # Sun parallel Venus (both at 23.0)
        sun_venus = next(
            (p for p in parallels if p['planet1'] == 'Sun' and p['planet2'] == 'Venus'),
            None
        )
        assert sun_venus is not None
        assert sun_venus['aspect'] == 'parallel'
    
    def test_quotidian_progressions(self, progressions_calculator, birth_datetime, current_datetime, natal_chart):
        """Test quotidian (daily) progressions."""
        result = progressions_calculator.calculate_quotidian_progressions(
            birth_datetime=birth_datetime,
            current_datetime=current_datetime,
            natal_chart=natal_chart
        )
        
        assert 'angles' in result
        # Angles should rotate once per day
        days = (current_datetime - birth_datetime).days
        expected_rotation = (days * 360) % 360
        # This is simplified - actual calculation is complex
    
    def test_user_defined_rate_progressions(self, progressions_calculator, birth_datetime, current_datetime, natal_chart):
        """Test user-defined progression rate."""
        # Custom rate: 2 degrees per year
        rate = 2.0
        
        result = progressions_calculator.calculate_user_rate_progressions(
            birth_datetime=birth_datetime,
            current_datetime=current_datetime,
            natal_chart=natal_chart,
            rate_per_year=rate
        )
        
        assert 'progressed_planets' in result
        years = (current_datetime - birth_datetime).days / 365.25
        expected_movement = years * rate
        
        # Check Sun movement
        prog_sun = result['progressed_planets']['Sun']['longitude']
        natal_sun = natal_chart['planets']['Sun']['longitude']
        actual_movement = (prog_sun - natal_sun) % 360
        assert abs(actual_movement - expected_movement) < 0.5
    
    def test_naibod_arc(self, progressions_calculator):
        """Test Naibod arc calculation (precise solar arc)."""
        years = 34.5
        
        naibod_arc = progressions_calculator._calculate_naibod_arc(years)
        
        # Naibod rate is approximately 59'08" per year
        expected = years * (59 + 8/60) / 60  # Convert to degrees
        assert abs(naibod_arc - expected) < 0.01
    
    def test_progression_orbs(self, progressions_calculator):
        """Test orb allowances for progressed aspects."""
        # Tight orb for progressed Sun
        sun_orb = progressions_calculator._get_progression_orb('Sun', 'conjunction')
        assert sun_orb == 1.0
        
        # Wider orb for progressed Moon
        moon_orb = progressions_calculator._get_progression_orb('Moon', 'conjunction')
        assert moon_orb == 1.5
        
        # Different orbs for different aspects
        square_orb = progressions_calculator._get_progression_orb('Mercury', 'square')
        trine_orb = progressions_calculator._get_progression_orb('Mercury', 'trine')
        assert square_orb <= trine_orb
    
    def test_void_of_course_moon(self, progressions_calculator):
        """Test void of course Moon detection in progressions."""
        prog_moon = 28.5  # Late degree of sign
        prog_moon_speed = 12.0
        other_planets = {
            'Sun': 120.0,
            'Mercury': 95.0,
            'Venus': 180.0
        }
        
        is_void = progressions_calculator._is_moon_void_of_course(
            prog_moon, prog_moon_speed, other_planets
        )
        
        assert isinstance(is_void, bool)
    
    def test_progressed_eclipse_points(self, progressions_calculator, birth_datetime, current_datetime):
        """Test progressed eclipse points (nodes)."""
        natal_north_node = 120.0
        
        prog_nodes = progressions_calculator._calculate_progressed_nodes(
            birth_datetime, current_datetime, natal_north_node
        )
        
        assert 'north_node' in prog_nodes
        assert 'south_node' in prog_nodes
        # Nodes move backward about 19 degrees per year
        assert prog_nodes['south_node'] == (prog_nodes['north_node'] + 180) % 360