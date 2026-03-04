#!/usr/bin/env python3
"""
Generate comprehensive HTML chart exports with all astrological details
Replicates the text format with enhanced HTML presentation
"""
import asyncio
import httpx
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import math

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

class ComprehensiveChartGenerator:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.headers = {"X-API-Key": API_KEY}
        
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
            # Get Vedic chart with full details
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
            
    def calculate_dasha_periods(self, moon_nakshatra: str, birth_date: datetime) -> List[Dict]:
        """Calculate Vimshottari Dasha periods"""
        # Nakshatra lords in order
        nakshatra_lords = {
            'Ashwini': 'Ketu', 'Bharani': 'Venus', 'Krittika': 'Sun',
            'Rohini': 'Moon', 'Mrigashira': 'Mars', 'Ardra': 'Rahu',
            'Punarvasu': 'Jupiter', 'Pushya': 'Saturn', 'Ashlesha': 'Mercury',
            'Magha': 'Ketu', 'Purva Phalguni': 'Venus', 'Uttara Phalguni': 'Sun',
            'Hasta': 'Moon', 'Chitra': 'Mars', 'Swati': 'Rahu',
            'Vishakha': 'Jupiter', 'Anuradha': 'Saturn', 'Jyeshtha': 'Mercury',
            'Mula': 'Ketu', 'Purva Ashadha': 'Venus', 'Uttara Ashadha': 'Sun',
            'Shravana': 'Moon', 'Dhanishta': 'Mars', 'Shatabhisha': 'Rahu',
            'Purva Bhadrapada': 'Jupiter', 'Uttara Bhadrapada': 'Saturn', 'Revati': 'Mercury'
        }
        
        # Dasha periods in years
        dasha_years = {
            'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18,
            'Jupiter': 16, 'Saturn': 19, 'Mercury': 17,
            'Ketu': 7, 'Venus': 20
        }
        
        # Dasha order
        dasha_order = ['Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury', 'Ketu', 'Venus']
        
        # Get starting dasha lord
        start_lord = nakshatra_lords.get(moon_nakshatra.split()[0], 'Ketu')
        start_index = dasha_order.index(start_lord)
        
        # Reorder dasha sequence
        ordered_dashas = dasha_order[start_index:] + dasha_order[:start_index]
        
        dashas = []
        current_date = birth_date
        
        for lord in ordered_dashas:
            end_date = current_date + timedelta(days=dasha_years[lord] * 365.25)
            dashas.append({
                'lord': lord,
                'start': current_date,
                'end': end_date,
                'years': dasha_years[lord]
            })
            current_date = end_date
            
        return dashas
        
    def format_degrees(self, degrees: float) -> str:
        """Format degrees to deg:min format"""
        deg = int(degrees)
        min = int((degrees - deg) * 60)
        return f"{deg:3d}:{min:02d}"
        
    def generate_comprehensive_html(self, person_data: Dict, chart_data: Dict) -> str:
        """Generate comprehensive HTML chart with all details"""
        
        # Extract data
        name = person_data['name'].upper()
        dob = datetime.strptime(person_data['date_of_birth'], "%Y-%m-%d")
        tob = datetime.strptime(person_data['time_of_birth'], "%H:%M:%S")
        
        # Get chart details
        chart_info = chart_data.get('chart_data', {})
        planets = chart_data.get('planet_positions', {})
        
        # Calculate current Dasha
        moon_data = planets.get('Moon', {})
        moon_nakshatra = moon_data.get('nakshatra', 'Ashwini')
        dashas = self.calculate_dasha_periods(moon_nakshatra, dob)
        
        # Find current dasha/bhukti
        current_date = datetime.now()
        current_dasha = None
        for dasha in dashas:
            if dasha['start'] <= current_date <= dasha['end']:
                current_dasha = dasha
                break
                
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Horoscope of {name}</title>
    <style>
        /* Typography and Base Styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', Courier, monospace;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #2c3e50;
            line-height: 1.6;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            border-radius: 15px;
            overflow: hidden;
        }}
        
        /* Header Styles */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: repeating-linear-gradient(
                45deg,
                transparent,
                transparent 10px,
                rgba(255,255,255,0.05) 10px,
                rgba(255,255,255,0.05) 20px
            );
            animation: slide 20s linear infinite;
        }}
        
        @keyframes slide {{
            0% {{ transform: translate(0, 0); }}
            100% {{ transform: translate(50px, 50px); }}
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 3px;
            position: relative;
            z-index: 1;
        }}
        
        .header .subtitle {{
            font-size: 1em;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }}
        
        /* Content Sections */
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .section-title {{
            font-size: 1.6em;
            color: #667eea;
            margin-bottom: 20px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Information Grid */
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        
        .info-item {{
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .info-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }}
        
        .info-label {{
            font-weight: bold;
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 5px;
            letter-spacing: 0.5px;
        }}
        
        .info-value {{
            color: #2c3e50;
            font-size: 1.1em;
            font-weight: 500;
        }}
        
        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        /* Planet Styling */
        .planet-sun {{ color: #e74c3c; font-weight: bold; }}
        .planet-moon {{ color: #3498db; font-weight: bold; }}
        .planet-mars {{ color: #e67e22; font-weight: bold; }}
        .planet-mercury {{ color: #27ae60; font-weight: bold; }}
        .planet-jupiter {{ color: #f39c12; font-weight: bold; }}
        .planet-venus {{ color: #e91e63; font-weight: bold; }}
        .planet-saturn {{ color: #9b59b6; font-weight: bold; }}
        .planet-rahu {{ color: #00bcd4; font-weight: bold; }}
        .planet-ketu {{ color: #795548; font-weight: bold; }}
        
        .retrograde {{
            color: #e74c3c;
            font-weight: bold;
            font-size: 0.9em;
            vertical-align: super;
        }}
        
        /* Charts Container */
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        
        .chart-wrapper {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            text-align: center;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.3em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .chart {{
            font-family: 'Courier New', monospace;
            white-space: pre;
            text-align: center;
            font-size: 14px;
            line-height: 1.4;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #667eea;
            overflow-x: auto;
        }}
        
        /* Special Sections */
        .dasha-info {{
            background: linear-gradient(135deg, #fff9c4 0%, #ffeb3b 100%);
            border-left: 5px solid #ffc107;
            padding: 20px;
            margin-bottom: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(255, 193, 7, 0.2);
        }}
        
        .dasha-current {{
            font-weight: bold;
            color: #f57c00;
            font-size: 1.2em;
            margin-bottom: 10px;
        }}
        
        .dasha-period {{
            color: #795548;
            font-size: 1em;
        }}
        
        /* Panchang Section */
        .panchang-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .panchang-item {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
        }}
        
        .panchang-label {{
            font-size: 0.85em;
            color: #1565c0;
            text-transform: uppercase;
            margin-bottom: 5px;
            font-weight: bold;
        }}
        
        .panchang-value {{
            font-size: 1.1em;
            color: #0d47a1;
            font-weight: 600;
        }}
        
        /* Footer */
        .footer {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 30px;
            text-align: center;
            font-size: 0.9em;
        }}
        
        .footer a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        /* Print Styles */
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
                border-radius: 0;
            }}
            
            .section {{
                break-inside: avoid;
                page-break-inside: avoid;
            }}
            
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            table {{
                font-size: 0.9em;
            }}
            
            .chart {{
                font-size: 12px;
                padding: 15px;
            }}
        }}
        
        /* Special Effects */
        .highlight {{
            background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: bold;
            background: #667eea;
            color: white;
            margin-left: 10px;
        }}
        
        /* Loading Animation */
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
        
        .loading {{
            animation: pulse 2s infinite;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <div class="header">
            <h1>Horoscope of {name}</h1>
            <div class="subtitle">(VER 2.0) Generated by Josi Professional Astrology API</div>
        </div>
        
        <!-- Content Section -->
        <div class="content">
            <!-- Birth Details Section -->
            <div class="section">
                <h2 class="section-title">Birth Details</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Date of Birth</div>
                        <div class="info-value">{dob.strftime('%d-%m-%Y %A').upper()}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Time of Birth</div>
                        <div class="info-value">{tob.strftime('%H:%M:%S')} IST</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Place of Birth</div>
                        <div class="info-value">{person_data['place_of_birth'].upper()}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Coordinates</div>
                        <div class="info-value">{person_data['latitude']:.4f}°N {person_data['longitude']:.4f}°E</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Time Zone</div>
                        <div class="info-value">IST (GMT +5:30)</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Ayanamsa</div>
                        <div class="info-value">Lahiri {chart_info.get('ayanamsa', 0):.4f}°</div>
                    </div>
                </div>
            </div>
"""
        
        # Add Panchang Details
        moon_data = planets.get('Moon', {})
        sun_data = planets.get('Sun', {})
        
        html_content += f"""
            <!-- Panchang Details -->
            <div class="section">
                <h2 class="section-title">Panchang Details</h2>
                <div class="panchang-grid">
                    <div class="panchang-item">
                        <div class="panchang-label">Nakshatra</div>
                        <div class="panchang-value">{moon_data.get('nakshatra', 'N/A')} Pada {moon_data.get('pada', 'N/A')}</div>
                    </div>
                    <div class="panchang-item">
                        <div class="panchang-label">Rasi (Moon Sign)</div>
                        <div class="panchang-value">{moon_data.get('sign', 'N/A')}</div>
                    </div>
                    <div class="panchang-item">
                        <div class="panchang-label">Lagna (Ascendant)</div>
                        <div class="panchang-value">{chart_info.get('ascendant', {}).get('sign', 'N/A')}</div>
                    </div>
                    <div class="panchang-item">
                        <div class="panchang-label">Sun Sign</div>
                        <div class="panchang-value">{sun_data.get('sign', 'N/A')}</div>
                    </div>
                </div>
            </div>
"""
        
        # Add Planetary Positions
        html_content += f"""
            <!-- Planetary Positions -->
            <div class="section">
                <h2 class="section-title">Nirayana Longitudes (Sidereal Positions)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Planet</th>
                            <th>Degree</th>
                            <th>Position</th>
                            <th>Sign</th>
                            <th>Nakshatra</th>
                            <th>Pada</th>
                            <th>House</th>
                            <th>Speed</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Add planets
        planet_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
        for planet_name in planet_order:
            if planet_name in planets:
                planet = planets[planet_name]
                is_retro = planet.get('speed', 0) < 0 and planet_name not in ['Rahu', 'Ketu']
                status = '<span class="retrograde">R</span>' if is_retro else ''
                
                # Format degree position
                deg_formatted = self.format_degrees(planet.get('longitude', 0))
                
                html_content += f"""
                        <tr>
                            <td class="planet-{planet_name.lower()}">{planet_name}</td>
                            <td>{planet.get('longitude', 0):.4f}°</td>
                            <td>{deg_formatted}</td>
                            <td>{planet.get('sign', 'N/A')}</td>
                            <td>{planet.get('nakshatra', 'N/A')}</td>
                            <td>{planet.get('pada', 'N/A')}</td>
                            <td>{planet.get('house', 'N/A')}</td>
                            <td>{planet.get('speed', 0):.4f}</td>
                            <td>{status}</td>
                        </tr>
"""
        
        # Add Ascendant
        asc_data = chart_info.get('ascendant', {})
        html_content += f"""
                        <tr>
                            <td><span class="highlight">Ascendant</span></td>
                            <td>{asc_data.get('longitude', 0):.4f}°</td>
                            <td>{self.format_degrees(asc_data.get('longitude', 0))}</td>
                            <td>{asc_data.get('sign', 'N/A')}</td>
                            <td>{asc_data.get('nakshatra', 'N/A')}</td>
                            <td>{asc_data.get('pada', 'N/A')}</td>
                            <td>1</td>
                            <td>-</td>
                            <td>-</td>
                        </tr>
                    </tbody>
                </table>
            </div>
"""
        
        # Add Charts
        rasi_chart = self.generate_detailed_ascii_chart(planets, chart_info, "rasi")
        navamsa_chart = self.generate_detailed_ascii_chart(planets, chart_info, "navamsa")
        
        html_content += f"""
            <!-- Charts Section -->
            <div class="section">
                <h2 class="section-title">Birth Charts</h2>
                <div class="charts-grid">
                    <div class="chart-wrapper">
                        <div class="chart-title">Rasi Chart (D1)</div>
                        <div class="chart">{rasi_chart}</div>
                    </div>
                    <div class="chart-wrapper">
                        <div class="chart-title">Navamsa Chart (D9)</div>
                        <div class="chart">{navamsa_chart}</div>
                    </div>
                </div>
            </div>
"""
        
        # Add Dasha Information
        if current_dasha:
            dasha_end = current_dasha['end'].strftime('%d-%m-%Y')
            dasha_name = f"{current_dasha['lord'].upper()} DASA"
            
            html_content += f"""
            <!-- Vimshottari Dasha -->
            <div class="section">
                <h2 class="section-title">Vimshottari Dasha System</h2>
                <div class="dasha-info">
                    <div class="dasha-current">Current Period: {dasha_name}</div>
                    <div class="dasha-period">Valid Until: {dasha_end}</div>
                </div>
                
                <h3 style="margin-top: 25px; margin-bottom: 15px;">Dasha Sequence (120 Years)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Dasha Lord</th>
                            <th>Period (Years)</th>
                            <th>Start Date</th>
                            <th>End Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            
            for dasha in dashas[:9]:  # Show first 9 dashas
                is_current = dasha == current_dasha
                status = '<span class="badge">CURRENT</span>' if is_current else ''
                
                html_content += f"""
                        <tr{'style="background: #fff9c4;"' if is_current else ''}>
                            <td class="planet-{dasha['lord'].lower()}">{dasha['lord']}</td>
                            <td>{dasha['years']} years</td>
                            <td>{dasha['start'].strftime('%d-%m-%Y')}</td>
                            <td>{dasha['end'].strftime('%d-%m-%Y')}</td>
                            <td>{status}</td>
                        </tr>
"""
            
            html_content += """
                    </tbody>
                </table>
            </div>
"""
        
        # Add House Details
        html_content += f"""
            <!-- House Cusps and Positions -->
            <div class="section">
                <h2 class="section-title">Bhava (House) Details</h2>
                <table>
                    <thead>
                        <tr>
                            <th>House</th>
                            <th>Cusp Degree</th>
                            <th>Sign</th>
                            <th>Sign Lord</th>
                            <th>Occupants</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # House lords mapping
        sign_lords = {
            'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
            'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
            'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
            'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
        }
        
        houses = chart_info.get('houses', [])
        house_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                       "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        for i in range(12):
            house_num = i + 1
            house_deg = houses[i] if i < len(houses) else 0
            sign_idx = int(house_deg / 30) % 12
            sign = house_signs[sign_idx]
            lord = sign_lords.get(sign, 'N/A')
            
            # Find planets in this house
            planets_in_house = []
            for planet_name, planet_data in planets.items():
                if planet_data.get('house') == house_num:
                    planets_in_house.append(planet_name)
                    
            html_content += f"""
                        <tr>
                            <td>House {house_num}</td>
                            <td>{house_deg:.2f}°</td>
                            <td>{sign}</td>
                            <td class="planet-{lord.lower()}">{lord}</td>
                            <td>{', '.join(planets_in_house) if planets_in_house else '-'}</td>
                        </tr>
"""
        
        html_content += """
                    </tbody>
                </table>
            </div>
"""
        
        # Add Additional Calculations section
        html_content += f"""
            <!-- Additional Calculations -->
            <div class="section">
                <h2 class="section-title">Additional Astronomical Data</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Julian Day Number</div>
                        <div class="info-value">{chart_info.get('julian_day', 'N/A')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Sidereal Time</div>
                        <div class="info-value">{chart_info.get('sidereal_time', 'N/A')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Sunrise</div>
                        <div class="info-value">{chart_info.get('sunrise', 'N/A')}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Sunset</div>
                        <div class="info-value">{chart_info.get('sunset', 'N/A')}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>© 2025 Josi Professional Astrology API - Astronomical Calculations by Swiss Ephemeris</p>
            <p><a href="https://josi.ai">www.josi.ai</a></p>
        </div>
    </div>
</body>
</html>
"""
        
        return html_content
        
    def generate_detailed_ascii_chart(self, planets: Dict, chart_info: Dict, chart_type: str = "rasi") -> str:
        """Generate detailed ASCII representation of chart"""
        # Initialize 12 houses
        houses = [[] for _ in range(12)]
        
        # Add Ascendant
        if chart_type == "rasi":
            asc_house = chart_info.get('ascendant', {}).get('house', 1) - 1
            if 0 <= asc_house < 12:
                houses[asc_house].append('LAG')
        
        # Place planets in houses
        for planet_name, planet_data in planets.items():
            if chart_type == "rasi":
                house = planet_data.get('house', 1) - 1
            else:  # navamsa
                # Calculate navamsa position (simplified)
                longitude = planet_data.get('longitude', 0)
                navamsa_pos = (longitude * 9) % 360
                house = int(navamsa_pos / 30)
                
            if 0 <= house < 12:
                # Use abbreviations
                abbrev = {
                    'Sun': 'SUN', 'Moon': 'CHA', 'Mars': 'KUJ',
                    'Mercury': 'BUD', 'Jupiter': 'GUR', 'Venus': 'SUK',
                    'Saturn': 'SAN', 'Rahu': 'RAH', 'Ketu': 'KET'
                }.get(planet_name, planet_name[:3].upper())
                houses[house].append(abbrev)
        
        # Create detailed ASCII chart
        chart = "+-------+-------+-------+-------+\n"
        chart += f"!{' ':^7}!{' ':^7}!{' ':^7}!{' ':^7}!\n"
        
        # House 12, 1, 2, 3
        for i, h in enumerate([11, 0, 1, 2]):
            planets_str = ' '.join(houses[h][:3])
            if planets_str:
                chart += f"!{planets_str:^7}"
            else:
                chart += f"!{' ':^7}"
        chart += "!\n"
        
        chart += f"!{' ':^7}!{' ':^7}!{' ':^7}!{' ':^7}!\n"
        chart += "+-------+-------+-------+-------+\n"
        
        # House 11 and 4
        chart += f"!{' ':^7}!               !{' ':^7}!\n"
        planets_11 = ' '.join(houses[10][:3])
        planets_4 = ' '.join(houses[3][:3])
        chart += f"!{planets_11:^7}!               !{planets_4:^7}!\n"
        chart += f"!{' ':^7}!               !{' ':^7}!\n"
        chart += "+-------+               +-------+\n"
        
        # House 10 and 5
        chart += f"!{' ':^7}!               !{' ':^7}!\n"
        planets_10 = ' '.join(houses[9][:3])
        planets_5 = ' '.join(houses[4][:3])
        chart += f"!{planets_10:^7}!               !{planets_5:^7}!\n"
        chart += f"!{' ':^7}!               !{' ':^7}!\n"
        chart += "+-------+-------+-------+-------+\n"
        
        # House 9, 8, 7, 6
        chart += f"!{' ':^7}!{' ':^7}!{' ':^7}!{' ':^7}!\n"
        for i, h in enumerate([8, 7, 6, 5]):
            planets_str = ' '.join(houses[h][:3])
            if planets_str:
                chart += f"!{planets_str:^7}"
            else:
                chart += f"!{' ':^7}"
        chart += "!\n"
        
        chart += f"!{' ':^7}!{' ':^7}!{' ':^7}!{' ':^7}!\n"
        chart += "+-------+-------+-------+-------+"
        
        return chart
        
    async def process_all_persons(self):
        """Process all test persons and generate comprehensive exports"""
        for person_data in TEST_PERSONS:
            logger.info(f"Processing {person_data['name']}...")
            
            # Create person
            person_id = await self.create_person(person_data)
            if not person_id:
                logger.error(f"Failed to create person: {person_data['name']}")
                continue
                
            # Get chart data
            chart_data = await self.get_chart_data(person_id)
            if not chart_data:
                logger.error(f"Failed to get chart data for: {person_data['name']}")
                continue
                
            # Generate comprehensive HTML
            html_content = self.generate_comprehensive_html(person_data, chart_data)
            
            # Save to file
            filename = f"comprehensive-chart-{person_data['name'].replace(' ', '_').lower()}.html"
            filepath = Path(__file__).parent.parent / "reports" / filename
            filepath.write_text(html_content)
            
            logger.info(f"Generated comprehensive export: {filepath}")
            
async def main():
    generator = ComprehensiveChartGenerator()
    
    try:
        # Check API health
        response = await generator.client.get(f"{API_BASE}/health/")
        if response.status_code != 200:
            logger.error("API is not healthy")
            return
            
        logger.info("Starting comprehensive chart generation...")
        await generator.process_all_persons()
        
        print("\n" + "="*70)
        print("COMPREHENSIVE CHART GENERATION COMPLETE")
        print("="*70)
        print("Generated comprehensive HTML exports in reports/ directory")
        print("Files created:")
        print("  - comprehensive-chart-archana_m.html")
        print("  - comprehensive-chart-valarmathi_kannappan.html")
        print("  - comprehensive-chart-janaki_panneerselvam.html")
        print("  - comprehensive-chart-panneerselvam_chandrasekaran.html")
        print("  - comprehensive-chart-govindarajan_panneerselvam.html")
        print("="*70)
        
    finally:
        await generator.close()

if __name__ == "__main__":
    asyncio.run(main())