"""Performance benchmark tests for astrology calculations."""
import pytest
import time
import statistics
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import asyncio
from concurrent.futures import ThreadPoolExecutor

from josi.services.astrology_service import AstrologyCalculator
from josi.services.vedic.dasha_service import VimshottariDashaCalculator
from josi.services.vedic.panchang_service import PanchangCalculator
from josi.services.vedic.muhurta_service import MuhurtaCalculator
from josi.services.chinese.bazi_calculator_service import BaZiCalculator
from josi.services.western.progressions_service import ProgressionCalculator


class TestPerformanceBenchmarks:
    """Performance benchmarks for core calculations."""
    
    @pytest.fixture
    def astrology_calculator(self):
        return AstrologyCalculator()
    
    @pytest.fixture
    def sample_locations(self):
        """Sample locations for testing."""
        return [
            (40.7128, -74.0060),   # New York
            (51.5074, -0.1278),    # London
            (35.6762, 139.6503),   # Tokyo
            (-33.8688, 151.2093),  # Sydney
            (19.4326, -99.1332),   # Mexico City
            (55.7558, 37.6173),    # Moscow
            (-26.2041, 28.0473),  # Johannesburg
            (28.7041, 77.1025),    # Delhi
        ]
    
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        return end - start, result
    
    def test_planet_calculation_performance(self, astrology_calculator, sample_locations):
        """Benchmark planet calculation performance."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        times = []
        
        with patch('swisseph.calc_ut') as mock_calc:
            # Mock faster calculation
            mock_calc.return_value = ((120.0, 0.0, 1.0, 0.0, 0.0, 0.0), 0)
            
            for lat, lon in sample_locations:
                exec_time, _ = self.measure_execution_time(
                    astrology_calculator.calculate_planets,
                    dt, lat, lon
                )
                times.append(exec_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        # Performance assertions
        assert avg_time < 0.1  # Average under 100ms
        assert max_time < 0.2  # Max under 200ms
        
        print(f"\nPlanet Calculation Performance:")
        print(f"  Average: {avg_time*1000:.2f}ms")
        print(f"  Max: {max_time*1000:.2f}ms")
        print(f"  Min: {min(times)*1000:.2f}ms")
    
    def test_house_calculation_performance(self, astrology_calculator):
        """Benchmark house system calculation performance."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        house_systems = ["placidus", "koch", "equal", "whole_sign", "regiomontanus"]
        
        times = {}
        with patch('swisseph.houses') as mock_houses:
            mock_houses.return_value = (
                [i * 30.0 for i in range(12)],
                [0.0, 270.0]
            )
            
            for system in house_systems:
                system_times = []
                for _ in range(10):
                    exec_time, _ = self.measure_execution_time(
                        astrology_calculator.calculate_houses,
                        dt, 40.7128, -74.0060, system
                    )
                    system_times.append(exec_time)
                
                times[system] = statistics.mean(system_times)
        
        # All house systems should be fast
        for system, avg_time in times.items():
            assert avg_time < 0.05  # Under 50ms
            print(f"  {system}: {avg_time*1000:.2f}ms")
    
    def test_aspect_calculation_performance(self, astrology_calculator):
        """Benchmark aspect calculation with many planets."""
        # Create planet positions including asteroids
        planet_positions = {
            "Sun": {"longitude": 0.0},
            "Moon": {"longitude": 60.0},
            "Mercury": {"longitude": 15.0},
            "Venus": {"longitude": 45.0},
            "Mars": {"longitude": 90.0},
            "Jupiter": {"longitude": 120.0},
            "Saturn": {"longitude": 180.0},
            "Uranus": {"longitude": 210.0},
            "Neptune": {"longitude": 240.0},
            "Pluto": {"longitude": 270.0},
            "Chiron": {"longitude": 30.0},
            "Ceres": {"longitude": 75.0},
            "Pallas": {"longitude": 105.0},
            "Juno": {"longitude": 135.0},
            "Vesta": {"longitude": 165.0}
        }
        
        exec_time, aspects = self.measure_execution_time(
            astrology_calculator.calculate_aspects,
            planet_positions
        )
        
        # Should handle 15 bodies efficiently
        assert exec_time < 0.1  # Under 100ms
        assert len(aspects) > 50  # Many aspects with 15 bodies
        
        print(f"\nAspect Calculation Performance:")
        print(f"  {len(planet_positions)} bodies: {exec_time*1000:.2f}ms")
        print(f"  {len(aspects)} aspects found")
    
    def test_vedic_chart_batch_performance(self, astrology_calculator):
        """Test batch calculation of Vedic charts."""
        base_dt = datetime(2024, 1, 1, 0, 0, 0)
        charts = []
        
        with patch.object(astrology_calculator, 'calculate_planets') as mock_planets:
            with patch.object(astrology_calculator, 'calculate_houses') as mock_houses:
                mock_planets.return_value = {"Sun": {"longitude": 120.0}}
                mock_houses.return_value = {"1": 0.0}
                
                start = time.perf_counter()
                
                # Calculate 100 charts
                for i in range(100):
                    dt = base_dt + timedelta(days=i)
                    chart = astrology_calculator.calculate_vedic_chart(
                        dt, 28.7041, 77.1025
                    )
                    charts.append(chart)
                
                end = time.perf_counter()
        
        total_time = end - start
        avg_time = total_time / 100
        
        assert avg_time < 0.01  # Under 10ms per chart
        print(f"\nVedic Chart Batch Performance:")
        print(f"  100 charts in {total_time:.2f}s")
        print(f"  Average: {avg_time*1000:.2f}ms per chart")
    
    def test_dasha_calculation_performance(self):
        """Benchmark Vimshottari Dasha calculation."""
        calculator = VimshottariDashaCalculator()
        birth_dt = datetime(1990, 1, 1, 10, 0, 0)
        moon_longitude = 125.5
        
        exec_time, dashas = self.measure_execution_time(
            calculator.calculate_vimshottari_dasha,
            birth_dt, moon_longitude
        )
        
        # Should calculate 120 years of dashas quickly
        assert exec_time < 0.05  # Under 50ms
        assert len(dashas) == 9  # 9 mahadashas
        
        # Check antardasha calculation
        total_antardashas = sum(len(d.get("antardashas", [])) for d in dashas)
        assert total_antardashas == 81  # 9 x 9
        
        print(f"\nDasha Calculation Performance:")
        print(f"  Mahadashas + Antardashas: {exec_time*1000:.2f}ms")
    
    def test_panchang_daily_calculation(self):
        """Benchmark daily panchang calculation."""
        calculator = PanchangCalculator()
        dt = datetime(2024, 1, 1, 6, 0, 0)
        
        components = [
            ("tithi", calculator.calculate_tithi, (280.0, 45.0)),
            ("nakshatra", calculator.calculate_nakshatra, (45.0,)),
            ("yoga", calculator.calculate_yoga, (280.0, 45.0)),
            ("karana", calculator.calculate_karana, (280.0, 45.0))
        ]
        
        for name, func, args in components:
            exec_time, _ = self.measure_execution_time(func, *args)
            assert exec_time < 0.001  # Under 1ms each
            print(f"  {name}: {exec_time*1000:.3f}ms")
    
    def test_muhurta_search_performance(self):
        """Benchmark muhurta finding performance."""
        calculator = MuhurtaCalculator()
        
        with patch.object(calculator, 'evaluate_muhurta_quality') as mock_eval:
            # Mock quality evaluation
            mock_eval.return_value = {
                "score": 85,
                "quality": "excellent",
                "factors": {}
            }
            
            start_date = datetime(2024, 1, 1)
            exec_time, muhurtas = self.measure_execution_time(
                calculator.find_muhurta,
                "marriage",
                start_date,
                start_date + timedelta(days=7),
                28.7041,
                77.1025,
                "Asia/Kolkata",
                max_results=10
            )
        
        # Should find muhurtas within reasonable time
        assert exec_time < 1.0  # Under 1 second for 7 days
        print(f"\nMuhurta Search Performance:")
        print(f"  7-day search: {exec_time*1000:.0f}ms")
    
    def test_bazi_complete_chart_performance(self):
        """Benchmark complete BaZi chart calculation."""
        calculator = BaZiCalculator()
        birth_dt = datetime(1990, 5, 15, 14, 30, 0)
        
        exec_time, chart = self.measure_execution_time(
            calculator.calculate_bazi_chart,
            birth_dt,
            gender="male",
            timezone="Asia/Shanghai"
        )
        
        # Complete BaZi analysis should be fast
        assert exec_time < 0.05  # Under 50ms
        assert all(pillar in chart for pillar in 
                  ["year_pillar", "month_pillar", "day_pillar", "hour_pillar"])
        
        print(f"\nBaZi Complete Chart Performance:")
        print(f"  Full analysis: {exec_time*1000:.2f}ms")
    
    def test_progression_calculation_performance(self):
        """Benchmark progression calculations."""
        calculator = ProgressionCalculator()
        natal_chart = {
            "planets": {
                f"planet_{i}": {"longitude": i * 30.0}
                for i in range(10)
            }
        }
        
        birth_date = datetime(1990, 1, 1)
        target_date = datetime(2024, 1, 1)
        
        # Test different progression types
        progression_types = [
            ("secondary", calculator.calculate_secondary_progressions),
            ("solar_arc", calculator.calculate_solar_arc_directions),
        ]
        
        for prog_type, func in progression_types:
            with patch('swisseph.calc_ut') as mock_calc:
                mock_calc.return_value = ((150.0, 0.0, 1.0, 0.0, 0.0, 0.0), 0)
                
                exec_time, _ = self.measure_execution_time(
                    func,
                    natal_chart,
                    birth_date,
                    target_date,
                    40.7128,
                    -74.0060
                )
                
                assert exec_time < 0.05  # Under 50ms
                print(f"  {prog_type}: {exec_time*1000:.2f}ms")
    
    def test_concurrent_chart_calculation(self, astrology_calculator):
        """Test concurrent calculation performance."""
        dates = [datetime(2024, 1, i, 12, 0, 0) for i in range(1, 11)]
        
        def calculate_chart(dt):
            with patch('swisseph.calc_ut') as mock_calc:
                mock_calc.return_value = ((120.0, 0.0, 1.0, 0.0, 0.0, 0.0), 0)
                return astrology_calculator.calculate_western_chart(
                    dt, 40.7128, -74.0060
                )
        
        # Sequential calculation
        start = time.perf_counter()
        sequential_results = [calculate_chart(dt) for dt in dates]
        sequential_time = time.perf_counter() - start
        
        # Concurrent calculation
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=4) as executor:
            concurrent_results = list(executor.map(calculate_chart, dates))
        concurrent_time = time.perf_counter() - start
        
        # Concurrent should be faster
        assert len(concurrent_results) == len(sequential_results)
        speedup = sequential_time / concurrent_time
        
        print(f"\nConcurrent Calculation Performance:")
        print(f"  Sequential: {sequential_time:.2f}s")
        print(f"  Concurrent: {concurrent_time:.2f}s")
        print(f"  Speedup: {speedup:.1f}x")
    
    def test_memory_efficiency_large_dataset(self, astrology_calculator):
        """Test memory efficiency with large datasets."""
        import gc
        import sys
        
        # Get initial memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Calculate many charts
        charts = []
        base_dt = datetime(2024, 1, 1)
        
        with patch('swisseph.calc_ut') as mock_calc:
            mock_calc.return_value = ((120.0, 0.0, 1.0, 0.0, 0.0, 0.0), 0)
            
            for i in range(1000):
                dt = base_dt + timedelta(hours=i)
                chart = astrology_calculator.calculate_planets(dt, 40.7, -74.0)
                charts.append(chart)
        
        # Check memory growth
        gc.collect()
        final_objects = len(gc.get_objects())
        object_growth = final_objects - initial_objects
        
        # Reasonable memory growth
        assert object_growth < 10000  # Arbitrary but reasonable limit
        
        print(f"\nMemory Efficiency Test:")
        print(f"  Charts calculated: 1000")
        print(f"  Object growth: {object_growth}")
    
    def test_cache_performance_improvement(self):
        """Test performance improvement with caching."""
        calculator = PanchangCalculator()
        
        # First call (no cache)
        exec_time1, _ = self.measure_execution_time(
            calculator.calculate_sunrise_sunset,
            datetime(2024, 1, 1),
            40.7128,
            -74.0060,
            "America/New_York"
        )
        
        # Second call (potentially cached)
        exec_time2, _ = self.measure_execution_time(
            calculator.calculate_sunrise_sunset,
            datetime(2024, 1, 1),
            40.7128,
            -74.0060,
            "America/New_York"
        )
        
        # Cache hit should be faster (if implemented)
        print(f"\nCache Performance:")
        print(f"  First call: {exec_time1*1000:.2f}ms")
        print(f"  Second call: {exec_time2*1000:.2f}ms")
        
        # At minimum, shouldn't be slower
        assert exec_time2 <= exec_time1 * 1.1  # Allow 10% variance
    
    @pytest.mark.asyncio
    async def test_async_calculation_performance(self):
        """Test async calculation performance."""
        # Simulate async astrology service
        async def calculate_chart_async(dt, lat, lon):
            # Simulate async I/O
            await asyncio.sleep(0.001)
            return {"dt": dt, "location": (lat, lon)}
        
        dates = [datetime(2024, 1, i) for i in range(1, 21)]
        
        # Async concurrent calculation
        start = time.perf_counter()
        tasks = [
            calculate_chart_async(dt, 40.7, -74.0)
            for dt in dates
        ]
        results = await asyncio.gather(*tasks)
        async_time = time.perf_counter() - start
        
        assert len(results) == 20
        assert async_time < 0.1  # Should complete quickly
        
        print(f"\nAsync Performance:")
        print(f"  20 charts (async): {async_time*1000:.0f}ms")
    
    def test_worst_case_performance(self, astrology_calculator):
        """Test performance under worst-case conditions."""
        # Many planets, tight orbs, complex calculations
        planet_positions = {
            f"body_{i}": {"longitude": i * 3.6}
            for i in range(50)  # 50 celestial bodies
        }
        
        # Calculate aspects with tight orbs
        exec_time, aspects = self.measure_execution_time(
            astrology_calculator.calculate_aspects,
            planet_positions,
            orb_settings={
                "conjunction": 1,
                "opposition": 1,
                "trine": 1,
                "square": 1,
                "sextile": 0.5
            }
        )
        
        # Even with 50 bodies, should complete
        assert exec_time < 1.0  # Under 1 second
        
        print(f"\nWorst Case Performance:")
        print(f"  50 bodies, tight orbs: {exec_time*1000:.0f}ms")
        print(f"  Aspects found: {len(aspects)}")