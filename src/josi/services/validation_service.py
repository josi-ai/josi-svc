import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json
import math


class AstrologyValidator:
    """
    Validates astronomical calculations against multiple sources.
    """
    
    def __init__(self):
        self.tolerance = {
            'longitude': 0.01,  # degrees (36 arcseconds)
            'latitude': 0.01,   # degrees
            'speed': 0.001,     # degrees/day
        }
    
    def validate_with_horizons(self, planet: str, dt: datetime, 
                             latitude: float, longitude: float) -> Dict:
        """
        Validate against NASA JPL Horizons (would require API key in production).
        For now, this is a placeholder showing the structure.
        """
        # In production, you would query JPL Horizons API
        # https://ssd.jpl.nasa.gov/horizons/
        pass
    
    def validate_planet_position(self, calculated: Dict, reference: Dict) -> Dict:
        """
        Compare calculated positions with reference data.
        
        Returns:
            Dict with validation results and differences
        """
        results = {
            'valid': True,
            'differences': {},
            'warnings': []
        }
        
        # Check longitude
        long_diff = abs(calculated['longitude'] - reference['longitude'])
        if long_diff > 180:  # Handle 360° wrap-around
            long_diff = 360 - long_diff
        
        results['differences']['longitude'] = long_diff
        if long_diff > self.tolerance['longitude']:
            results['valid'] = False
            results['warnings'].append(
                f"Longitude difference {long_diff:.4f}° exceeds tolerance"
            )
        
        # Check latitude
        if 'latitude' in reference:
            lat_diff = abs(calculated['latitude'] - reference['latitude'])
            results['differences']['latitude'] = lat_diff
            if lat_diff > self.tolerance['latitude']:
                results['valid'] = False
                results['warnings'].append(
                    f"Latitude difference {lat_diff:.4f}° exceeds tolerance"
                )
        
        # Check speed
        if 'speed' in reference and 'speed' in calculated:
            speed_diff = abs(calculated['speed'] - reference['speed'])
            results['differences']['speed'] = speed_diff
            if speed_diff > self.tolerance['speed']:
                results['warnings'].append(
                    f"Speed difference {speed_diff:.4f}°/day exceeds tolerance"
                )
        
        return results
    
    def validate_ayanamsa(self, calculated: float, system: str, dt: datetime) -> Dict:
        """
        Validate ayanamsa value against known standards.
        """
        # Known ayanamsa values for Jan 1, 2000
        ayanamsa_2000 = {
            'lahiri': 23.85,
            'krishnamurti': 23.73,
            'raman': 22.36,
            'fagan_bradley': 24.74,
        }
        
        # Approximate precession rate: 50.29 arcseconds/year
        years_diff = (dt.year + dt.month/12 + dt.day/365.25) - 2000
        precession = (50.29 / 3600) * years_diff
        
        expected = ayanamsa_2000.get(system.lower(), 23.85) + precession
        difference = abs(calculated - expected)
        
        return {
            'valid': difference < 0.1,
            'expected': expected,
            'calculated': calculated,
            'difference': difference
        }


class AccuracyImprover:
    """
    Implements high-precision astronomical calculations.
    """
    
    @staticmethod
    def apply_aberration_correction(longitude: float, speed: float) -> float:
        """
        Apply aberration of light correction.
        """
        # Constant of aberration: 20.49552 arcseconds
        aberration = 20.49552 / 3600  # Convert to degrees
        # Simplified correction (full calculation requires Earth's velocity vector)
        return longitude - aberration * (1 + speed/30)
    
    @staticmethod
    def apply_nutation_correction(longitude: float, obliquity: float, 
                                  nutation_long: float, nutation_obl: float) -> float:
        """
        Apply nutation corrections for higher precision.
        """
        # This is a simplified version
        return longitude + nutation_long
    
    @staticmethod
    def calculate_topocentric_position(geocentric_pos: Dict, 
                                       observer_lat: float, 
                                       observer_lon: float,
                                       observer_elevation: float = 0) -> Dict:
        """
        Convert geocentric to topocentric (observer-centered) positions.
        Important for Moon calculations.
        """
        # Earth's radius in km
        earth_radius = 6371.0
        
        # Calculate parallax correction (simplified)
        # Full calculation requires distance to celestial body
        parallax_correction = 0.0
        
        if 'distance' in geocentric_pos:
            # Horizontal parallax
            hp = math.degrees(math.asin(earth_radius / geocentric_pos['distance']))
            parallax_correction = hp * math.cos(math.radians(observer_lat))
        
        topocentric_pos = geocentric_pos.copy()
        topocentric_pos['longitude'] -= parallax_correction
        
        return topocentric_pos