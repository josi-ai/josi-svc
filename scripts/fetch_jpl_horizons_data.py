#!/usr/bin/env python3
"""
Fetch astronomical data from NASA JPL Horizons system.
This script retrieves high-precision ephemeris data for verification.
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class JPLHorizonsClient:
    """Client for NASA JPL Horizons API."""
    
    BASE_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
    
    # Body codes for JPL Horizons
    BODIES = {
        'sun': '10',
        'moon': '301',
        'mercury': '199',
        'venus': '299',
        'mars': '499',
        'jupiter': '599',
        'saturn': '699',
        'uranus': '799',
        'neptune': '899',
        'pluto': '999'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting to be respectful of the API."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def fetch_ephemeris(
        self,
        body: str,
        start_date: datetime,
        stop_date: datetime,
        step_size: str = '1d',
        center: str = '500@399',  # Earth geocenter
        ref_plane: str = 'ECLIPTIC',
        ref_system: str = 'J2000'
    ) -> Optional[Dict]:
        """
        Fetch ephemeris data from JPL Horizons.
        
        Args:
            body: Name of celestial body (e.g., 'sun', 'moon', 'mercury')
            start_date: Start date for ephemeris
            stop_date: End date for ephemeris
            step_size: Step size (e.g., '1d', '1h', '10m')
            center: Observer location (default: Earth center)
            ref_plane: Reference plane (ECLIPTIC or FRAME)
            ref_system: Reference system (J2000 or ICRF)
        
        Returns:
            Dictionary containing ephemeris data
        """
        if body.lower() not in self.BODIES:
            raise ValueError(f"Unknown body: {body}")
        
        # Rate limiting
        self._rate_limit()
        
        # Format dates
        start_str = start_date.strftime('%Y-%m-%d %H:%M')
        stop_str = stop_date.strftime('%Y-%m-%d %H:%M')
        
        # Build request parameters
        params = {
            'format': 'json',
            'COMMAND': self.BODIES[body.lower()],
            'EPHEM_TYPE': 'OBSERVER',
            'CENTER': center,
            'START_TIME': start_str,
            'STOP_TIME': stop_str,
            'STEP_SIZE': step_size,
            'QUANTITIES': '1,2,31',  # 1=RA/DEC, 2=apparent RA/DEC, 31=observer ecliptic lon/lat
            'REF_PLANE': ref_plane,
            'REF_SYSTEM': ref_system,
            'CAL_FORMAT': 'CAL',
            'TIME_DIGITS': 'SECONDS',
            'ANG_FORMAT': 'DEG',
            'APPARENT': 'AIRLESS',
            'RANGE_UNITS': 'AU',
            'SUPPRESS_RANGE_RATE': 'NO',
            'SKIP_DAYLT': 'NO',
            'EXTRA_PREC': 'YES',
            'R_T_S_ONLY': 'NO',
            'CSV_FORMAT': 'NO'
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'result' not in data:
                print(f"Error: No result in response for {body}")
                return None
            
            # Parse the result
            return self._parse_horizons_output(data['result'], body)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {body}: {e}")
            return None
    
    def _parse_horizons_output(self, result: str, body: str) -> Dict:
        """Parse the text output from Horizons into structured data."""
        lines = result.split('\n')
        
        # Find start of ephemeris data
        start_marker = "$$SOE"
        end_marker = "$$EOE"
        
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if start_marker in line:
                start_idx = i + 1
            elif end_marker in line:
                end_idx = i
                break
        
        if start_idx is None or end_idx is None:
            print("Could not find ephemeris data markers")
            return None
        
        # Extract data lines
        data_lines = lines[start_idx:end_idx]
        
        ephemeris_data = []
        
        for line in data_lines:
            if line.strip():
                # Parse each line of ephemeris data
                # Format depends on QUANTITIES requested
                # This is a simplified parser - adjust based on actual output
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        # Example parsing - adjust based on actual format
                        date_str = f"{parts[0]} {parts[1]}"
                        # Parse additional fields based on format
                        
                        ephemeris_data.append({
                            'datetime': date_str,
                            'raw_line': line
                        })
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing line: {line}")
                        continue
        
        return {
            'body': body,
            'ephemeris': ephemeris_data,
            'raw_result': result
        }
    
    def fetch_current_positions(self, bodies: List[str] = None) -> Dict:
        """Fetch current positions of celestial bodies."""
        if bodies is None:
            bodies = list(self.BODIES.keys())
        
        now = datetime.utcnow()
        results = {}
        
        for body in bodies:
            print(f"Fetching current position for {body}...")
            data = self.fetch_ephemeris(
                body=body,
                start_date=now,
                stop_date=now + timedelta(minutes=1),
                step_size='1m'
            )
            
            if data:
                results[body] = data
        
        return results
    
    def fetch_test_dates(self) -> Dict:
        """Fetch ephemeris for standard test dates."""
        test_dates = [
            {
                'name': 'J2000.0',
                'date': datetime(2000, 1, 1, 12, 0, 0),
                'description': 'J2000.0 epoch'
            },
            {
                'name': 'Spring Equinox 2024',
                'date': datetime(2024, 3, 20, 3, 6, 20),
                'description': 'Sun at 0° ecliptic longitude'
            },
            {
                'name': 'Summer Solstice 2024',
                'date': datetime(2024, 6, 20, 20, 51, 0),
                'description': 'Sun at 90° ecliptic longitude'
            }
        ]
        
        results = {}
        
        for test in test_dates:
            print(f"\nFetching data for {test['name']}...")
            date = test['date']
            
            # Fetch Sun and Moon positions
            for body in ['sun', 'moon']:
                key = f"{test['name']}_{body}"
                data = self.fetch_ephemeris(
                    body=body,
                    start_date=date - timedelta(minutes=5),
                    stop_date=date + timedelta(minutes=5),
                    step_size='1m'
                )
                
                if data:
                    results[key] = {
                        'test_name': test['name'],
                        'date': date.isoformat(),
                        'body': body,
                        'data': data
                    }
        
        return results

def save_horizons_data(output_file: str = 'jpl_horizons_test_data.json'):
    """Fetch and save JPL Horizons data for testing."""
    client = JPLHorizonsClient()
    
    print("Fetching JPL Horizons test data...")
    print("=" * 60)
    
    # Fetch test data
    test_data = client.fetch_test_dates()
    
    # Fetch current positions
    print("\nFetching current positions...")
    current_positions = client.fetch_current_positions(['sun', 'moon', 'mercury', 'venus', 'mars'])
    
    # Combine all data
    all_data = {
        'fetch_date': datetime.utcnow().isoformat(),
        'source': 'NASA JPL Horizons',
        'test_positions': test_data,
        'current_positions': current_positions
    }
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2, default=str)
    
    print(f"\nData saved to {output_file}")
    
    # Print summary
    print("\nSummary:")
    print(f"- Test positions fetched: {len(test_data)}")
    print(f"- Current positions fetched: {len(current_positions)}")

def main():
    """Main function to run data collection."""
    print("NASA JPL Horizons Data Fetcher")
    print("=" * 60)
    print("\nThis script fetches high-precision ephemeris data from NASA JPL")
    print("for verifying astronomical calculations.\n")
    
    # Note about API usage
    print("NOTE: This script accesses NASA's public API.")
    print("Please be respectful and avoid excessive requests.\n")
    
    try:
        save_horizons_data()
        
        print("\n✅ Data collection complete!")
        print("\nNext steps:")
        print("1. Review the generated JSON file")
        print("2. Extract ecliptic longitude/latitude values")
        print("3. Use these as reference values in tests")
        print("4. Compare your calculations against JPL data")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())