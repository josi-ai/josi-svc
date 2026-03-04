#!/usr/bin/env python3
"""
Generate HTML chart exports for all test persons
"""
import asyncio
import httpx
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
API_BASE = "http://localhost:8000/api/v1"
API_KEY = "test-api-key"

# Test persons data
TEST_PERSONS = [
    {
        "name": "Archana M",
        "gender": "female",
        "date_of_birth": "1998-12-07",
        "time_of_birth": "21:15:00",
        "place_of_birth": "Chennai, Tamil Nadu, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Valarmathi Kannappan",
        "gender": "female", 
        "date_of_birth": "1961-02-11",
        "time_of_birth": "15:30:00",
        "place_of_birth": "Kovur, Tamil Nadu, India",
        "latitude": 13.011362,
        "longitude": 80.120858,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Janaki Panneerselvam",
        "gender": "female",
        "date_of_birth": "1982-12-18",
        "time_of_birth": "10:10:00",
        "place_of_birth": "Chennai, Tamil Nadu, India",
        "latitude": 13.083694,
        "longitude": 80.270186,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Panneerselvam Chandrasekaran",
        "gender": "male",
        "date_of_birth": "1954-08-20",
        "time_of_birth": "18:20:00",
        "place_of_birth": "Kanchipuram, Tamil Nadu, India",
        "latitude": 12.833237,
        "longitude": 79.703644,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Govindarajan Panneerselvam",
        "gender": "male",
        "date_of_birth": "1984-05-20",
        "time_of_birth": "23:00:00",
        "place_of_birth": "Chennai, Tamil Nadu, India",
        "latitude": 13.083694,
        "longitude": 80.270186,
        "timezone": "Asia/Kolkata"
    }
]

class ChartExporter:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.headers = {"X-API-Key": API_KEY}
        self.results = []
        
    async def close(self):
        await self.client.aclose()
        
    async def create_person(self, person_data: Dict) -> Optional[str]:
        """Create a person and return their ID"""
        try:
            response = await self.client.post(
                f"{API_BASE}/persons/",
                json=person_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()['data']['person_id']
            else:
                logger.error(f"Failed to create person {person_data['name']}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating person: {e}")
            return None
            
    async def get_chart_data(self, person_id: str) -> Optional[Dict]:
        """Get comprehensive chart data for a person"""
        try:
            # Get Vedic chart
            response = await self.client.post(
                f"{API_BASE}/charts/calculate/",
                params={
                    "person_id": person_id,
                    "systems": "vedic",
                    "house_system": "placidus",
                    "ayanamsa": "lahiri"
                },
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to calculate chart: {response.text}")
                return None
                
            return response.json()['data'][0]
            
        except Exception as e:
            logger.error(f"Error calculating chart: {e}")
            return None
            
    def generate_html_export(self, person_data: Dict, chart_data: Dict) -> str:
        """Generate HTML export in the style of the text format"""
        
        # Extract data
        name = person_data['name'].upper()
        dob = datetime.strptime(person_data['date_of_birth'], "%Y-%m-%d")
        tob = datetime.strptime(person_data['time_of_birth'], "%H:%M:%S")
        
        # Get planetary positions
        planets = chart_data.get('planet_positions', {})
        
        # Generate Rasi chart ASCII
        rasi_chart = self.generate_ascii_chart(planets, "rasi")
        navamsa_chart = self.generate_ascii_chart(planets, "navamsa")
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Horoscope of {name}</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background-color: #f5f5f5;
            margin: 20px;
            line-height: 1.4;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #333;
            font-size: 24px;
            margin-bottom: 30px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            font-weight: bold;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }}
        .info-item {{
            background-color: #ecf0f1;
            padding: 8px 12px;
            border-radius: 5px;
        }}
        .label {{
            font-weight: bold;
            color: #34495e;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 8px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .chart-container {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }}
        .chart {{
            background-color: #fff;
            border: 2px solid #2c3e50;
            padding: 10px;
            font-family: monospace;
            white-space: pre;
        }}
        .planet-table {{
            font-size: 14px;
        }}
        .retrograde {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .highlight {{
            background-color: #f39c12;
            color: white;
            padding: 2px 5px;
            border-radius: 3px;
        }}
        @media print {{
            body {{
                margin: 0;
                background-color: white;
            }}
            .container {{
                box-shadow: none;
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>HOROSCOPE OF {name}</h1>
        
        <div class="section">
            <div class="section-title">Birth Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="label">Date of Birth:</span> {dob.strftime('%d-%m-%Y %A').upper()}
                </div>
                <div class="info-item">
                    <span class="label">Time:</span> {tob.strftime('%H:%M')} HRS (IST)
                </div>
                <div class="info-item">
                    <span class="label">Place:</span> {person_data['place_of_birth'].upper()}
                </div>
                <div class="info-item">
                    <span class="label">Coordinates:</span> {person_data['latitude']:.1f}°N {person_data['longitude']:.1f}°E
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Astronomical Data</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="label">Ayanamsa:</span> {chart_data.get('chart_data', {}).get('ayanamsa', 0):.2f}°
                </div>
                <div class="info-item">
                    <span class="label">Sidereal Time:</span> {chart_data.get('chart_data', {}).get('sidereal_time', 'N/A')}
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Planetary Positions (Nirayana/Sidereal)</div>
            <table class="planet-table">
                <tr>
                    <th>Planet</th>
                    <th>Longitude</th>
                    <th>Sign</th>
                    <th>Nakshatra</th>
                    <th>Pada</th>
                    <th>Speed</th>
                    <th>Retrograde</th>
                </tr>
"""
        
        # Add planetary positions
        planet_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
        for planet_name in planet_order:
            if planet_name in planets:
                planet = planets[planet_name]
                is_retro = planet.get('speed', 0) < 0 and planet_name not in ['Rahu', 'Ketu']
                
                html_content += f"""
                <tr>
                    <td>{planet_name}</td>
                    <td>{planet.get('longitude', 0):.2f}°</td>
                    <td>{planet.get('sign', 'N/A')}</td>
                    <td>{planet.get('nakshatra', 'N/A')}</td>
                    <td>{planet.get('pada', 'N/A')}</td>
                    <td>{planet.get('speed', 0):.4f}</td>
                    <td>{'<span class="retrograde">R</span>' if is_retro else ''}</td>
                </tr>
"""
        
        # Add Ascendant
        asc_data = chart_data.get('chart_data', {}).get('ascendant', {})
        html_content += f"""
                <tr>
                    <td><span class="highlight">Ascendant</span></td>
                    <td>{asc_data.get('longitude', 0):.2f}°</td>
                    <td>{asc_data.get('sign', 'N/A')}</td>
                    <td>{asc_data.get('nakshatra', 'N/A')}</td>
                    <td>{asc_data.get('pada', 'N/A')}</td>
                    <td>-</td>
                    <td>-</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Charts</div>
            <div class="chart-container">
                <div>
                    <h3>RASI CHART</h3>
                    <div class="chart">{rasi_chart}</div>
                </div>
                <div>
                    <h3>NAVAMSA CHART</h3>
                    <div class="chart">{navamsa_chart}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">House Positions</div>
            <table>
                <tr>
                    <th>House</th>
                    <th>Sign</th>
                    <th>Degree</th>
                    <th>Planets</th>
                </tr>
"""
        
        # Add house data
        houses = chart_data.get('chart_data', {}).get('houses', [])
        house_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                       "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        for i in range(12):
            house_num = i + 1
            house_deg = houses[i] if i < len(houses) else 0
            sign_idx = int(house_deg / 30)
            sign = house_signs[sign_idx] if sign_idx < 12 else "N/A"
            
            # Find planets in this house
            planets_in_house = []
            for planet_name, planet_data in planets.items():
                if planet_data.get('house') == house_num:
                    planets_in_house.append(planet_name)
                    
            html_content += f"""
                <tr>
                    <td>House {house_num}</td>
                    <td>{sign}</td>
                    <td>{house_deg:.2f}°</td>
                    <td>{', '.join(planets_in_house) if planets_in_house else '-'}</td>
                </tr>
"""
        
        html_content += """
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Additional Information</div>
            <p>Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            <p>Software: Josi Professional Astrology API v2.0</p>
            <p>Ayanamsa: Lahiri</p>
            <p>House System: Placidus</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html_content
        
    def generate_ascii_chart(self, planets: Dict, chart_type: str = "rasi") -> str:
        """Generate ASCII representation of chart"""
        # Simple 12-house grid
        houses = [[] for _ in range(12)]
        
        # Place planets in houses
        for planet_name, planet_data in planets.items():
            house = planet_data.get('house', 1) - 1
            if 0 <= house < 12:
                # Use abbreviations
                abbrev = {
                    'Sun': 'SUN', 'Moon': 'MOO', 'Mars': 'MAR',
                    'Mercury': 'MER', 'Jupiter': 'JUP', 'Venus': 'VEN',
                    'Saturn': 'SAT', 'Rahu': 'RAH', 'Ketu': 'KET'
                }.get(planet_name, planet_name[:3].upper())
                houses[house].append(abbrev)
        
        # Create ASCII chart
        chart = "+-------+-------+-------+-------+\n"
        chart += f"|  {' '.join(houses[11][:2]):^5} |  {' '.join(houses[0][:2]):^5} |  {' '.join(houses[1][:2]):^5} |  {' '.join(houses[2][:2]):^5} |\n"
        chart += "+-------+-------+-------+-------+\n"
        chart += f"|  {' '.join(houses[10][:2]):^5} |               |  {' '.join(houses[3][:2]):^5} |\n"
        chart += "+-------+               +-------+\n"
        chart += f"|  {' '.join(houses[9][:2]):^5} |               |  {' '.join(houses[4][:2]):^5} |\n"
        chart += "+-------+-------+-------+-------+\n"
        chart += f"|  {' '.join(houses[8][:2]):^5} |  {' '.join(houses[7][:2]):^5} |  {' '.join(houses[6][:2]):^5} |  {' '.join(houses[5][:2]):^5} |\n"
        chart += "+-------+-------+-------+-------+"
        
        return chart
        
    async def process_all_persons(self):
        """Process all test persons and generate exports"""
        for person_data in TEST_PERSONS:
            logger.info(f"Processing {person_data['name']}...")
            
            # Create person
            person_id = await self.create_person(person_data)
            if not person_id:
                continue
                
            # Get chart data
            chart_data = await self.get_chart_data(person_id)
            if not chart_data:
                continue
                
            # Generate HTML
            html_content = self.generate_html_export(person_data, chart_data)
            
            # Save to file
            filename = f"astro-chart-export-{person_data['name'].replace(' ', '_').lower()}.html"
            filepath = Path(__file__).parent.parent / "reports" / filename
            filepath.write_text(html_content)
            
            logger.info(f"Generated export: {filepath}")
            
async def main():
    exporter = ChartExporter()
    
    try:
        # Check API health
        response = await exporter.client.get(f"{API_BASE}/health/")
        if response.status_code != 200:
            logger.error("API is not healthy")
            return
            
        logger.info("Starting chart export generation...")
        await exporter.process_all_persons()
        
        print("\n" + "="*60)
        print("CHART EXPORT GENERATION COMPLETE")
        print("="*60)
        print("Generated HTML exports in reports/ directory")
        print("="*60)
        
    finally:
        await exporter.close()

if __name__ == "__main__":
    asyncio.run(main())