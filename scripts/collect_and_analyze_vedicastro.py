#!/usr/bin/env python3
"""
Enhanced VedicAstroAPI data collection with detailed analysis for each test case.
Generates individual markdown reports for each person.
"""
import os
import json
import time
import httpx
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
API_KEY = "30548028-046d-54bb-abd7-8db05db5536b"
BASE_URL = "https://api.vedicastroapi.com/v3-json"
RATE_LIMIT_DELAY = 0.5  # seconds between requests

# Test data storage paths
TEST_DATA_DIR = Path("test_data/vedicastro_api")
RAW_RESPONSES_DIR = TEST_DATA_DIR / "raw_responses"
PROCESSED_DATA_DIR = TEST_DATA_DIR / "processed_data"
DETAILED_REPORTS_DIR = TEST_DATA_DIR / "detailed_reports"
VALIDATION_RESULTS_DIR = TEST_DATA_DIR / "validation_results"

# Create directories
for dir_path in [RAW_RESPONSES_DIR, PROCESSED_DATA_DIR, DETAILED_REPORTS_DIR, VALIDATION_RESULTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

class VedicAstroAPIClient:
    """Client for fetching data from VedicAstroAPI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.last_request_time = 0
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            await asyncio.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Make API request with error handling"""
        await self._rate_limit()
        
        # Add API key and language
        params['api_key'] = self.api_key
        params['lang'] = 'en'
        
        url = f"{BASE_URL}/{endpoint}"
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 200:
                return data
            else:
                logger.error(f"API error for {endpoint}: {data}")
                return None
                
        except httpx.HTTPError as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            return None
    
    # All endpoint methods
    async def get_planet_details(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        return await self._make_request("horoscope/planet-details", {
            'dob': dob, 'tob': tob, 'lat': lat, 'lon': lon, 'tz': tz
        })
    
    async def get_extended_kundli(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        return await self._make_request("extended-horoscope/extended-kundli-details", {
            'dob': dob, 'tob': tob, 'lat': lat, 'lon': lon, 'tz': tz
        })
    
    async def get_panchang(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        return await self._make_request("panchang/panchang", {
            'dob': dob, 'tob': tob, 'lat': lat, 'lon': lon, 'tz': tz
        })
    
    async def get_mahadasha(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        return await self._make_request("dashas/maha-dasha", {
            'dob': dob, 'tob': tob, 'lat': lat, 'lon': lon, 'tz': tz
        })
    
    async def get_western_planets(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        return await self._make_request("western/planet-details", {
            'dob': dob, 'tob': tob, 'lat': lat, 'lon': lon, 'tz': tz
        })
    
    async def get_mangal_dosha(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        return await self._make_request("dosha/mangal-dosh", {
            'dob': dob, 'tob': tob, 'lat': lat, 'lon': lon, 'tz': tz
        })
    
    async def get_kaalsarp_dosha(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        return await self._make_request("dosha/kaalsarp-dosh", {
            'dob': dob, 'tob': tob, 'lat': lat, 'lon': lon, 'tz': tz
        })
    
    async def get_personal_characteristics(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        return await self._make_request("horoscope/personal-characteristics", {
            'dob': dob, 'tob': tob, 'lat': lat, 'lon': lon, 'tz': tz
        })
    
    async def get_planetary_aspects(self, dob: str, tob: str, lat: float, lon: float, tz: float) -> Optional[Dict]:
        return await self._make_request("horoscope/planetary-aspects", {
            'dob': dob, 'tob': tob, 'lat': lat, 'lon': lon, 'tz': tz
        })

def load_test_cases() -> List[Dict]:
    """Load only the Indian family test cases"""
    # Indian family test cases
    test_cases = [
        {
            "name": "Panneerselvam_Chandrasekaran",
            "display_name": "Panneerselvam Chandrasekaran",
            "dob": "20/08/1954",
            "tob": "18:20",  # 06:20 PM
            "lat": 12.8185,   # Kanchipuram
            "lon": 79.6947,
            "tz": 5.5,        # India Standard Time
            "place": "Kanchipuram, Tamil Nadu, India",
            "relation": "Father"
        },
        {
            "name": "Valarmathi_Kannappan",
            "display_name": "Valarmathi Kannappan",
            "dob": "11/02/1961",
            "tob": "15:30",  # 03:30 PM
            "lat": 13.1622,   # Kovur (near Chennai)
            "lon": 80.0050,
            "tz": 5.5,
            "place": "Kovur, Tamil Nadu, India",
            "relation": "Mother"
        },
        {
            "name": "Janaki_Panneerselvam",
            "display_name": "Janaki Panneerselvam",
            "dob": "18/12/1982",
            "tob": "10:10",  # 10:10 AM
            "lat": 13.0827,   # Chennai
            "lon": 80.2707,
            "tz": 5.5,
            "place": "Chennai, Tamil Nadu, India",
            "relation": "Daughter"
        },
        {
            "name": "Govindarajan_Panneerselvam",
            "display_name": "Govindarajan Panneerselvam",
            "dob": "29/12/1989",
            "tob": "12:12",  # 12:12 PM
            "lat": 13.0827,   # Chennai
            "lon": 80.2707,
            "tz": 5.5,
            "place": "Chennai, Tamil Nadu, India",
            "relation": "Son"
        }
    ]
    
    return test_cases

def generate_detailed_report(test_case: Dict, collected_data: Dict):
    """Generate a detailed markdown report for each test case"""
    report_path = DETAILED_REPORTS_DIR / f"{test_case['name']}_detailed_analysis.md"
    
    with open(report_path, 'w') as f:
        # Header
        f.write(f"# Detailed Astrological Analysis: {test_case['display_name']}\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Source**: VedicAstroAPI\n\n")
        
        # Birth Details
        f.write("## Birth Details\n\n")
        f.write(f"- **Name**: {test_case['display_name']}\n")
        f.write(f"- **Date of Birth**: {test_case['dob']}\n")
        f.write(f"- **Time of Birth**: {test_case['tob']}\n")
        f.write(f"- **Place**: {test_case['place']}\n")
        f.write(f"- **Coordinates**: {test_case['lat']}°N, {test_case['lon']}°E\n")
        f.write(f"- **Timezone**: UTC+{test_case['tz']}\n")
        f.write(f"- **Relation**: {test_case.get('relation', 'N/A')}\n\n")
        
        # Planetary Positions
        if 'planet_details' in collected_data['data']:
            f.write("## Planetary Positions (Vedic)\n\n")
            f.write("| Planet | Full Name | Longitude | Sign | House | Retrograde |\n")
            f.write("|--------|-----------|-----------|------|-------|------------|\n")
            
            planets = collected_data['data']['planet_details']
            if isinstance(planets, dict):
                # Filter and sort numeric keys only
                numeric_keys = [k for k in planets.keys() if k.isdigit()]
                for key in sorted(numeric_keys, key=int):
                    planet = planets[key]
                    f.write(f"| {planet['name']} | {planet['full_name']} | ")
                    f.write(f"{planet['global_degree']:.4f}° | ")
                    f.write(f"{planet.get('zodiac', 'N/A')} | {planet.get('house', 'N/A')} | ")
                    f.write(f"{'Yes' if planet.get('retro', False) else 'No'} |\n")
            elif isinstance(planets, list):
                for planet in planets:
                    f.write(f"| {planet['name']} | {planet.get('full_name', planet['name'])} | ")
                    f.write(f"{planet.get('longitude', planet.get('global_degree', 0)):.4f}° | ")
                    f.write(f"{planet.get('sign', planet.get('zodiac', 'N/A'))} | ")
                    f.write(f"{planet.get('house', 'N/A')} | ")
                    f.write(f"{'Yes' if planet.get('retrograde', planet.get('retro', False)) else 'No'} |\n")
            f.write("\n")
        
        # Extended Kundli Details
        if 'extended_kundli' in collected_data['data']:
            kundli = collected_data['data']['extended_kundli']
            
            # Ascendant
            f.write("## Ascendant (Lagna)\n\n")
            f.write(f"- **Sign**: {kundli.get('lagna', {}).get('rashi', kundli.get('ascendant', 'N/A'))}\n")
            f.write(f"- **Degree**: {kundli.get('lagna', {}).get('degree', kundli.get('ascendant_degree', 0)):.4f}°\n")
            f.write(f"- **Nakshatra**: {kundli.get('lagna', {}).get('nakshatra', kundli.get('ascendant_nakshatra', 'N/A'))}\n\n")
            
            # Moon Details
            f.write("## Moon Details\n\n")
            f.write(f"- **Sign**: {kundli.get('moon', {}).get('rashi', kundli.get('moon_sign', 'N/A'))}\n")
            f.write(f"- **Nakshatra**: {kundli.get('moon', {}).get('nakshatra', kundli.get('moon_nakshatra', 'N/A'))}\n")
            f.write(f"- **Pada**: {kundli.get('moon', {}).get('nakshatra_pada', kundli.get('moon_nakshatra_pada', 'N/A'))}\n\n")
            
            # Sun Details
            f.write("## Sun Details\n\n")
            f.write(f"- **Sign**: {kundli.get('sun', {}).get('rashi', kundli.get('sun_sign', 'N/A'))}\n")
            f.write(f"- **Nakshatra**: {kundli.get('sun', {}).get('nakshatra', kundli.get('sun_nakshatra', 'N/A'))}\n\n")
        
        # Panchang
        if 'panchang' in collected_data['data']:
            panchang = collected_data['data']['panchang']
            f.write("## Panchang Elements\n\n")
            f.write(f"- **Tithi**: {panchang.get('tithi', 'N/A')}\n")
            f.write(f"- **Nakshatra**: {panchang.get('nakshatra', 'N/A')}\n")
            f.write(f"- **Yoga**: {panchang.get('yoga', 'N/A')}\n")
            f.write(f"- **Karana**: {panchang.get('karana', 'N/A')}\n")
            f.write(f"- **Weekday**: {panchang.get('day', 'N/A')}\n\n")
        
        # Dasha
        if 'mahadasha' in collected_data['data']:
            dasha = collected_data['data']['mahadasha']
            f.write("## Vimshottari Dasha\n\n")
            
            if 'mahadasha' in dasha and 'mahadasha_order' in dasha:
                f.write("### Mahadasha Order\n\n")
                f.write("| Planet | Start Date |\n")
                f.write("|--------|------------|\n")
                
                for planet, date in zip(dasha['mahadasha'], dasha['mahadasha_order']):
                    f.write(f"| {planet} | {date} |\n")
                
                f.write(f"\n**Dasha Balance at Birth**: {dasha.get('dasha_remaining_at_birth', 'N/A')}\n\n")
        
        # Doshas
        if 'mangal_dosha' in collected_data['data']:
            dosha = collected_data['data']['mangal_dosha']
            f.write("## Mangal/Manglik Dosha Analysis\n\n")
            f.write(f"- **Present**: {'Yes' if dosha.get('is_dosha_present', False) else 'No'}\n")
            f.write(f"- **Score**: {dosha.get('score', 0)}%\n")
            f.write(f"- **Assessment**: {dosha.get('bot_response', 'N/A')}\n\n")
            
            if 'factors' in dosha:
                f.write("### Contributing Factors\n\n")
                for key, value in dosha['factors'].items():
                    f.write(f"- **{key.title()}**: {value}\n")
                f.write("\n")
        
        if 'kaalsarp_dosha' in collected_data['data']:
            dosha = collected_data['data']['kaalsarp_dosha']
            f.write("## Kaal Sarp Dosha Analysis\n\n")
            f.write(f"- **Present**: {'Yes' if dosha.get('is_dosha_present', False) else 'No'}\n")
            if dosha.get('is_dosha_present'):
                f.write(f"- **Type**: {dosha.get('dosha_type', 'N/A')}\n")
                f.write(f"- **Direction**: {dosha.get('dosha_direction', 'N/A')}\n")
                f.write(f"- **Rahu-Ketu Axis**: {dosha.get('rahu_ketu_axis', 'N/A')}\n")
            f.write("\n")
        
        # Personal Characteristics
        if 'personal_characteristics' in collected_data['data']:
            chars = collected_data['data']['personal_characteristics']
            f.write("## Personal Characteristics\n\n")
            if isinstance(chars, dict):
                f.write(f"{chars.get('description', 'N/A')}\n\n")
            elif isinstance(chars, list) and len(chars) > 0:
                f.write(f"{chars[0] if isinstance(chars[0], str) else 'N/A'}\n\n")
            else:
                f.write("N/A\n\n")
        
        # Planetary Aspects
        if 'planetary_aspects' in collected_data['data']:
            aspects = collected_data['data']['planetary_aspects']
            f.write("## Major Planetary Aspects\n\n")
            f.write("| Planet 1 | Aspect | Planet 2 | Orb |\n")
            f.write("|----------|--------|----------|-----|\n")
            
            if isinstance(aspects, list):
                for aspect in aspects[:10]:  # Top 10 aspects
                    if isinstance(aspect, dict):
                        f.write(f"| {aspect.get('planet1', '')} | ")
                        f.write(f"{aspect.get('aspect', '')} | ")
                        f.write(f"{aspect.get('planet2', '')} | ")
                        f.write(f"{aspect.get('orb', '')}° |\n")
            f.write("\n")
        
        # Raw Data Reference
        f.write("## Data Files\n\n")
        f.write(f"- Complete data: `collected_{test_case['name']}.json`\n")
        f.write(f"- Planetary positions: `raw_responses/planet_details/{test_case['name']}_planet_details.json`\n")
        f.write(f"- Extended kundli: `raw_responses/extended_kundli/{test_case['name']}_extended_kundli.json`\n")
        f.write(f"- Panchang: `raw_responses/panchang/{test_case['name']}_panchang.json`\n")
        f.write(f"- Dasha: `raw_responses/mahadasha/{test_case['name']}_mahadasha.json`\n")
    
    logger.info(f"Detailed report saved to {report_path}")

async def collect_data_for_test_case(client: VedicAstroAPIClient, test_case: Dict) -> Dict:
    """Collect all relevant data for a single test case"""
    logger.info(f"Collecting data for: {test_case['display_name']}")
    
    result = {
        "test_case": test_case,
        "timestamp": datetime.utcnow().isoformat(),
        "data": {}
    }
    
    # Collect different types of data
    endpoints = [
        ("planet_details", client.get_planet_details),
        ("extended_kundli", client.get_extended_kundli),
        # ("panchang", client.get_panchang),  # Requires current date
        ("mahadasha", client.get_mahadasha),
        # ("western_planets", client.get_western_planets),  # Needs house type param
        ("mangal_dosha", client.get_mangal_dosha),
        ("kaalsarp_dosha", client.get_kaalsarp_dosha),
        ("personal_characteristics", client.get_personal_characteristics),
        # ("planetary_aspects", client.get_planetary_aspects)  # Needs type param
    ]
    
    for endpoint_name, endpoint_func in endpoints:
        logger.info(f"  Fetching {endpoint_name}...")
        data = await endpoint_func(
            test_case['dob'],
            test_case['tob'],
            test_case['lat'],
            test_case['lon'],
            test_case['tz']
        )
        
        if data:
            result['data'][endpoint_name] = data['response']
            
            # Save raw response
            filename = f"{test_case['name']}_{endpoint_name}.json"
            filepath = RAW_RESPONSES_DIR / endpoint_name / filename
            filepath.parent.mkdir(exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            logger.error(f"  Failed to fetch {endpoint_name}")
    
    return result

async def main():
    """Main execution function"""
    logger.info("Starting VedicAstroAPI data collection with detailed analysis...")
    
    # Initialize client
    client = VedicAstroAPIClient(API_KEY)
    
    # Load test cases
    test_cases = load_test_cases()
    logger.info(f"Loaded {len(test_cases)} test cases")
    
    # Summary report
    summary_report = {
        "collection_date": datetime.utcnow().isoformat(),
        "test_cases_processed": [],
        "api_key_used": API_KEY[:10] + "...",
        "endpoints_tested": [
            "planet_details", "extended_kundli", "panchang", "mahadasha",
            "western_planets", "mangal_dosha", "kaalsarp_dosha",
            "personal_characteristics", "planetary_aspects"
        ]
    }
    
    # Collect data for each test case
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Processing: {test_case['display_name']}")
        print(f"{'='*60}")
        
        # Collect data
        result = await collect_data_for_test_case(client, test_case)
        
        # Save complete data
        filepath = TEST_DATA_DIR / f"collected_{test_case['name']}.json"
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Generate detailed report
        generate_detailed_report(test_case, result)
        
        # Update summary
        summary_report['test_cases_processed'].append({
            "name": test_case['display_name'],
            "file": f"collected_{test_case['name']}.json",
            "report": f"detailed_reports/{test_case['name']}_detailed_analysis.md",
            "endpoints_successful": len(result['data'])
        })
        
        print(f"✅ Completed: {test_case['display_name']}")
        print(f"   - Data saved to: collected_{test_case['name']}.json")
        print(f"   - Report saved to: detailed_reports/{test_case['name']}_detailed_analysis.md")
    
    # Save summary report
    summary_path = DETAILED_REPORTS_DIR / "collection_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary_report, f, indent=2)
    
    # Create index file
    index_path = DETAILED_REPORTS_DIR / "INDEX.md"
    with open(index_path, 'w') as f:
        f.write("# VedicAstroAPI Test Data Analysis Index\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Test Cases Analyzed\n\n")
        
        for tc in summary_report['test_cases_processed']:
            f.write(f"1. [{tc['name']}]({tc['report'].split('/')[-1]})\n")
            f.write(f"   - Data file: `{tc['file']}`\n")
            f.write(f"   - Endpoints successful: {tc['endpoints_successful']}\n\n")
    
    print(f"\n{'='*60}")
    print("✅ Data collection and analysis complete!")
    print(f"{'='*60}")
    print(f"\nReports generated in: {DETAILED_REPORTS_DIR}")
    print(f"- Individual reports: {len(test_cases)} files")
    print(f"- Summary report: collection_summary.json")
    print(f"- Index file: INDEX.md")
    
    print("\nNext steps:")
    print("1. Review the detailed reports for each person")
    print("2. Run validation against our API: python validate_our_apis.py")
    print("3. Check accuracy metrics in validation reports")
    
    # Close the client
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())