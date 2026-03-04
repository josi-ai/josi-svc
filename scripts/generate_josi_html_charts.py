#!/usr/bin/env python3
"""
Generate HTML chart exports using Josi API data for all 5 persons.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.josi.services.astrology_service import AstrologyCalculator

# HTML template for individual charts
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Vedic Astrology Chart - {name}</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            text-align: center;
            color: #333;
        }}
        .info-section {{
            background-color: #f9f9f9;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .retrograde {{
            color: #ff6b6b;
            font-weight: bold;
        }}
        .chart-container {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }}
        .chart {{
            margin: 20px;
        }}
        .chart-title {{
            text-align: center;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 14px;
        }}
        .nakshatra-info {{
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            font-style: italic;
        }}
        .speed-info {{
            font-size: 0.9em;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Vedic Astrology Birth Chart</h1>
        <h2>{name}</h2>
        <p class="timestamp">Generated on: {timestamp}</p>
        
        <div class="info-section">
            <h3>Birth Information</h3>
            <table>
                <tr>
                    <td><strong>Date of Birth:</strong></td>
                    <td>{dob}</td>
                    <td><strong>Time of Birth:</strong></td>
                    <td>{tob}</td>
                </tr>
                <tr>
                    <td><strong>Place of Birth:</strong></td>
                    <td colspan="3">{place}</td>
                </tr>
                <tr>
                    <td><strong>Latitude:</strong></td>
                    <td>{latitude}°</td>
                    <td><strong>Longitude:</strong></td>
                    <td>{longitude}°</td>
                </tr>
                <tr>
                    <td><strong>Timezone:</strong></td>
                    <td>{timezone}</td>
                    <td><strong>Ayanamsa:</strong></td>
                    <td>{ayanamsa_name} ({ayanamsa_value:.6f}°)</td>
                </tr>
            </table>
        </div>

        <h3>Planetary Positions</h3>
        <table>
            <thead>
                <tr>
                    <th>Planet</th>
                    <th>Longitude</th>
                    <th>Sign</th>
                    <th>House</th>
                    <th>Nakshatra</th>
                    <th>Pada</th>
                    <th>Speed (°/day)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {planet_rows}
            </tbody>
        </table>

        <div class="chart-container">
            <div class="chart">
                <div class="chart-title">South Indian Chart (Fixed Houses)</div>
                <pre>{south_indian_chart}</pre>
            </div>
            <div class="chart">
                <div class="chart-title">North Indian Chart (Fixed Signs)</div>
                <pre>{north_indian_chart}</pre>
            </div>
        </div>

        <div class="nakshatra-info">
            <h3>Nakshatra Details</h3>
            <table>
                <tr>
                    <td><strong>Birth Nakshatra (Moon):</strong></td>
                    <td>{moon_nakshatra} Pada {moon_pada}</td>
                    <td><strong>Nakshatra Lord:</strong></td>
                    <td>{moon_nakshatra_lord}</td>
                </tr>
                <tr>
                    <td><strong>Ascendant Nakshatra:</strong></td>
                    <td>{asc_nakshatra} Pada {asc_pada}</td>
                    <td><strong>Nakshatra Lord:</strong></td>
                    <td>{asc_nakshatra_lord}</td>
                </tr>
            </table>
        </div>

        <div class="info-section">
            <h3>Additional Information</h3>
            <p><strong>Retrograde Planets:</strong> {retrograde_planets}</p>
            <p><strong>House System:</strong> {house_system}</p>
            <p><strong>Calculation Method:</strong> Swiss Ephemeris with Lahiri Ayanamsa</p>
            <p><strong>Chart Style:</strong> Traditional Vedic (Sidereal Zodiac)</p>
        </div>

        <div class="info-section">
            <h4>House Cusps</h4>
            <table>
                <tr>
                    {house_cusps_row1}
                </tr>
                <tr>
                    {house_cusps_row2}
                </tr>
            </table>
        </div>
    </div>
</body>
</html>"""

# Nakshatra lords mapping
NAKSHATRA_LORDS = {
    "Ashwini": "Ketu",
    "Bharani": "Venus",
    "Krittika": "Sun",
    "Rohini": "Moon",
    "Mrigashira": "Mars",
    "Ardra": "Rahu",
    "Punarvasu": "Jupiter",
    "Pushya": "Saturn",
    "Ashlesha": "Mercury",
    "Magha": "Ketu",
    "Purva Phalguni": "Venus",
    "Uttara Phalguni": "Sun",
    "Hasta": "Moon",
    "Chitra": "Mars",
    "Swati": "Rahu",
    "Vishakha": "Jupiter",
    "Anuradha": "Saturn",
    "Jyeshtha": "Mercury",
    "Mula": "Ketu",
    "Purva Ashadha": "Venus",
    "Uttara Ashadha": "Sun",
    "Shravana": "Moon",
    "Dhanishta": "Mars",
    "Shatabhisha": "Rahu",
    "Purva Bhadrapada": "Jupiter",
    "Uttara Bhadrapada": "Saturn",
    "Revati": "Mercury"
}

# Test persons data
ALL_PERSONS = [
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
        "latitude": 13.1622,
        "longitude": 80.005,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Janaki Panneerselvam",
        "gender": "female",
        "date_of_birth": "1982-12-18",
        "time_of_birth": "10:10:00",
        "place_of_birth": "Chennai, Tamil Nadu, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Govindarajan Panneerselvam",
        "gender": "male",
        "date_of_birth": "1989-12-29",
        "time_of_birth": "12:12:00",
        "place_of_birth": "Chennai, Tamil Nadu, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata"
    },
    {
        "name": "Panneerselvam Chandrasekaran",
        "gender": "male",
        "date_of_birth": "1954-08-20",
        "time_of_birth": "18:20:00",
        "place_of_birth": "Kanchipuram, Tamil Nadu, India",
        "latitude": 12.8185,
        "longitude": 79.6947,
        "timezone": "Asia/Kolkata"
    }
]

def calculate_chart(person: dict) -> dict:
    """Calculate chart using Josi AstrologyCalculator."""
    calc = AstrologyCalculator()
    
    # Parse datetime
    dob_parts = person['date_of_birth'].split('-')
    tob_parts = person['time_of_birth'].split(':')
    
    dt = datetime(
        int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2]),
        int(tob_parts[0]), int(tob_parts[1]), int(tob_parts[2])
    )
    
    # Calculate chart
    chart = calc.calculate_vedic_chart(
        dt=dt,
        latitude=person['latitude'],
        longitude=person['longitude'],
        timezone=person['timezone'],
        house_system='placidus'
    )
    
    return chart

def create_south_indian_chart(planets: dict, ascendant: dict) -> str:
    """Create ASCII representation of South Indian chart."""
    # Initialize houses
    houses = [[] for _ in range(12)]
    
    # Get ascendant sign
    asc_sign_num = int(ascendant['longitude'] / 30)
    
    # Place planets in houses
    for planet, data in planets.items():
        sign_num = int(data['longitude'] / 30)
        house_num = (sign_num - asc_sign_num) % 12
        houses[house_num].append(planet[:2])
    
    # Add Ascendant
    houses[0].append('As')
    
    # Format chart
    chart = """
    ┌─────────┬─────────┬─────────┬─────────┐
    │   12    │    1    │    2    │    3    │
    │ {h11:^7} │ {h0:^7} │ {h1:^7} │ {h2:^7} │
    ├─────────┼─────────┴─────────┼─────────┤
    │   11    │                   │    4    │
    │ {h10:^7} │                   │ {h3:^7} │
    ├─────────┤       RASI        ├─────────┤
    │   10    │                   │    5    │
    │ {h9:^7} │                   │ {h4:^7} │
    ├─────────┼─────────┬─────────┼─────────┤
    │    9    │    8    │    7    │    6    │
    │ {h8:^7} │ {h7:^7} │ {h6:^7} │ {h5:^7} │
    └─────────┴─────────┴─────────┴─────────┘
    """.format(
        h0=' '.join(houses[0][:3]) if houses[0] else '',
        h1=' '.join(houses[1][:3]) if houses[1] else '',
        h2=' '.join(houses[2][:3]) if houses[2] else '',
        h3=' '.join(houses[3][:3]) if houses[3] else '',
        h4=' '.join(houses[4][:3]) if houses[4] else '',
        h5=' '.join(houses[5][:3]) if houses[5] else '',
        h6=' '.join(houses[6][:3]) if houses[6] else '',
        h7=' '.join(houses[7][:3]) if houses[7] else '',
        h8=' '.join(houses[8][:3]) if houses[8] else '',
        h9=' '.join(houses[9][:3]) if houses[9] else '',
        h10=' '.join(houses[10][:3]) if houses[10] else '',
        h11=' '.join(houses[11][:3]) if houses[11] else ''
    )
    
    return chart

def create_north_indian_chart(planets: dict, ascendant: dict) -> str:
    """Create ASCII representation of North Indian chart."""
    # Signs
    signs = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]
    asc_sign_num = int(ascendant['longitude'] / 30)
    
    # Create house to sign mapping
    house_signs = []
    for i in range(12):
        sign_idx = (asc_sign_num + i) % 12
        house_signs.append(signs[sign_idx])
    
    # Place planets
    house_planets = [[] for _ in range(12)]
    for planet, data in planets.items():
        sign_num = int(data['longitude'] / 30)
        house_num = (sign_num - asc_sign_num) % 12
        house_planets[house_num].append(planet[:2])
    
    # Add ascendant
    house_planets[0].append('As')
    
    # Format chart
    chart = """
           ┌─────────────────────┐
           │        12           │
           │  {s11}  {p11:^9}    │
    ┌──────┼──────┬──────┬──────┼──────┐
    │  11  │      │  1   │      │  2   │
    │ {s10} │{p10:^6}│{s0} As│{p1:^6}│ {s1}  │
    ├──────┼──────┼──────┼──────┼──────┤
    │  10  │      │      │      │  3   │
    │ {s9}  │{p9:^6}│      │{p2:^6}│ {s2}  │
    ├──────┼──────┤ RASI ├──────┼──────┤
    │  9   │      │      │      │  4   │
    │ {s8}  │{p8:^6}│      │{p3:^6}│ {s3}  │
    ├──────┼──────┼──────┼──────┼──────┤
    │  8   │      │  7   │      │  5   │
    │ {s7}  │{p7:^6}│{s6}{p6:^4}│{p4:^6}│ {s4}  │
    └──────┼──────┴──────┴──────┼──────┘
           │        6            │
           │  {s5}  {p5:^9}    │
           └─────────────────────┘
    """.format(
        s0=house_signs[0], s1=house_signs[1], s2=house_signs[2],
        s3=house_signs[3], s4=house_signs[4], s5=house_signs[5],
        s6=house_signs[6], s7=house_signs[7], s8=house_signs[8],
        s9=house_signs[9], s10=house_signs[10], s11=house_signs[11],
        p0=' '.join(house_planets[0][:2]) if len(house_planets[0]) > 1 else '',
        p1=' '.join(house_planets[1][:2]) if house_planets[1] else '',
        p2=' '.join(house_planets[2][:2]) if house_planets[2] else '',
        p3=' '.join(house_planets[3][:2]) if house_planets[3] else '',
        p4=' '.join(house_planets[4][:2]) if house_planets[4] else '',
        p5=' '.join(house_planets[5][:2]) if house_planets[5] else '',
        p6=' '.join(house_planets[6][:2]) if house_planets[6] else '',
        p7=' '.join(house_planets[7][:2]) if house_planets[7] else '',
        p8=' '.join(house_planets[8][:2]) if house_planets[8] else '',
        p9=' '.join(house_planets[9][:2]) if house_planets[9] else '',
        p10=' '.join(house_planets[10][:2]) if house_planets[10] else '',
        p11=' '.join(house_planets[11][:2]) if house_planets[11] else ''
    )
    
    return chart

def generate_html_chart(person: dict, chart: dict, output_file: str):
    """Generate HTML chart for a person."""
    
    # Prepare planet rows
    planet_rows = []
    
    # Ascendant first
    asc = chart['ascendant']
    planet_rows.append(f"""
        <tr>
            <td><strong>Ascendant</strong></td>
            <td>{asc['longitude']:.6f}°</td>
            <td>{asc['sign']}</td>
            <td>1</td>
            <td>{asc['nakshatra']}</td>
            <td>{asc['pada']}</td>
            <td>-</td>
            <td>-</td>
        </tr>
    """)
    
    # Planets
    planet_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    retrograde_planets = []
    
    for planet_name in planet_order:
        if planet_name in chart['planets']:
            planet = chart['planets'][planet_name]
            speed = planet.get('speed', 0)
            
            # Check retrograde
            if speed < 0 and planet_name not in ['Rahu', 'Ketu']:
                retrograde_planets.append(planet_name)
                status = '<span class="retrograde">Retrograde</span>'
            elif planet_name in ['Rahu', 'Ketu']:
                status = 'Always Retrograde'
            else:
                status = 'Direct'
            
            planet_rows.append(f"""
                <tr>
                    <td><strong>{planet_name}</strong></td>
                    <td>{planet['longitude']:.6f}°</td>
                    <td>{planet['sign']}</td>
                    <td>{planet['house']}</td>
                    <td>{planet['nakshatra']}</td>
                    <td>{planet['pada']}</td>
                    <td class="speed-info">{speed:.6f}</td>
                    <td>{status}</td>
                </tr>
            """)
    
    # Get Moon and Ascendant nakshatra details
    moon_nakshatra = chart['planets']['Moon']['nakshatra']
    moon_pada = chart['planets']['Moon']['pada']
    moon_nakshatra_lord = NAKSHATRA_LORDS.get(moon_nakshatra, 'Unknown')
    
    asc_nakshatra = chart['ascendant']['nakshatra']
    asc_pada = chart['ascendant']['pada']
    asc_nakshatra_lord = NAKSHATRA_LORDS.get(asc_nakshatra, 'Unknown')
    
    # House cusps
    houses = chart.get('houses', [])
    house_cusps_row1 = ""
    house_cusps_row2 = ""
    
    for i in range(6):
        if i < len(houses):
            house_cusps_row1 += f"<td><strong>House {i+1}:</strong></td><td>{houses[i]:.2f}°</td>"
        if i+6 < len(houses):
            house_cusps_row2 += f"<td><strong>House {i+7}:</strong></td><td>{houses[i+6]:.2f}°</td>"
    
    # Generate charts
    south_indian_chart = create_south_indian_chart(chart['planets'], chart['ascendant'])
    north_indian_chart = create_north_indian_chart(chart['planets'], chart['ascendant'])
    
    # Fill template
    html_content = HTML_TEMPLATE.format(
        name=person['name'],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        dob=person['date_of_birth'],
        tob=person['time_of_birth'],
        place=person['place_of_birth'],
        latitude=person['latitude'],
        longitude=person['longitude'],
        timezone=person['timezone'],
        ayanamsa_name=chart['ayanamsa_name'],
        ayanamsa_value=chart['ayanamsa'],
        planet_rows=''.join(planet_rows),
        south_indian_chart=south_indian_chart,
        north_indian_chart=north_indian_chart,
        moon_nakshatra=moon_nakshatra,
        moon_pada=moon_pada,
        moon_nakshatra_lord=moon_nakshatra_lord,
        asc_nakshatra=asc_nakshatra,
        asc_pada=asc_pada,
        asc_nakshatra_lord=asc_nakshatra_lord,
        retrograde_planets=', '.join(retrograde_planets) if retrograde_planets else 'None',
        house_system=chart.get('house_system', 'Placidus').title(),
        house_cusps_row1=house_cusps_row1,
        house_cusps_row2=house_cusps_row2
    )
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  Generated: {output_file}")

def main():
    """Generate HTML charts for all persons."""
    
    print("Generating Josi HTML Chart Exports")
    print("=" * 80)
    
    # Create output directory
    output_dir = "reports/josi_charts"
    os.makedirs(output_dir, exist_ok=True)
    
    for person in ALL_PERSONS:
        try:
            print(f"\nProcessing: {person['name']}")
            
            # Calculate chart
            chart = calculate_chart(person)
            
            # Generate HTML
            output_file = f"{output_dir}/{person['name'].replace(' ', '_')}_chart.html"
            generate_html_chart(person, chart, output_file)
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # Generate index file
    index_html = """<!DOCTYPE html>
<html>
<head>
    <title>Josi Vedic Astrology Charts</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            margin: 15px 0;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        a {
            text-decoration: none;
            color: #4CAF50;
            font-size: 18px;
        }
        a:hover {
            text-decoration: underline;
        }
        .info {
            color: #666;
            font-size: 14px;
        }
        .timestamp {
            text-align: center;
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Josi Vedic Astrology Charts</h1>
        <p class="timestamp">Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        <h2>Available Charts:</h2>
        <ul>
            <li>
                <a href="Archana_M_chart.html">Archana M</a>
                <span class="info">DOB: 1998-12-07, Chennai</span>
            </li>
            <li>
                <a href="Valarmathi_Kannappan_chart.html">Valarmathi Kannappan</a>
                <span class="info">DOB: 1961-02-11, Kovur</span>
            </li>
            <li>
                <a href="Janaki_Panneerselvam_chart.html">Janaki Panneerselvam</a>
                <span class="info">DOB: 1982-12-18, Chennai</span>
            </li>
            <li>
                <a href="Govindarajan_Panneerselvam_chart.html">Govindarajan Panneerselvam</a>
                <span class="info">DOB: 1989-12-29, Chennai</span>
            </li>
            <li>
                <a href="Panneerselvam_Chandrasekaran_chart.html">Panneerselvam Chandrasekaran</a>
                <span class="info">DOB: 1954-08-20, Kanchipuram</span>
            </li>
        </ul>
    </div>
</body>
</html>"""
    
    with open(f"{output_dir}/index.html", 'w') as f:
        f.write(index_html)
    
    print(f"\n{'='*80}")
    print(f"All charts generated in: {output_dir}/")
    print(f"Open {output_dir}/index.html to view all charts")

if __name__ == "__main__":
    main()