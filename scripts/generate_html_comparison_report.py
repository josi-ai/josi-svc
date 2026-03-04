#!/usr/bin/env python3
"""
Generate HTML comparison report for all 5 persons with VedicAstroAPI data.
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.josi.services.astrology_service import AstrologyCalculator

# HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Astrology Calculation Comparison Report - {name}</title>
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
        .excellent {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .good {{
            color: #FF9800;
            font-weight: bold;
        }}
        .poor {{
            color: #f44336;
            font-weight: bold;
        }}
        .chart-container {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }}
        .chart {{
            width: 400px;
            height: 400px;
            position: relative;
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
        }}
        .summary {{
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Vedic Astrology Calculation Comparison Report</h1>
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
                    <td>GMT+{tz}</td>
                    <td><strong>Ayanamsa:</strong></td>
                    <td>{ayanamsa_name} ({ayanamsa_value:.6f}°)</td>
                </tr>
            </table>
        </div>

        <h3>Planetary Position Comparison</h3>
        <table>
            <thead>
                <tr>
                    <th>Planet</th>
                    <th>VedicAstroAPI</th>
                    <th>Josi Calculation</th>
                    <th>Difference (°)</th>
                    <th>Arc Minutes</th>
                    <th>Accuracy</th>
                    <th>Sign</th>
                    <th>Nakshatra</th>
                </tr>
            </thead>
            <tbody>
                {planet_rows}
            </tbody>
        </table>

        <div class="summary">
            <h3>Accuracy Summary</h3>
            <table>
                <tr>
                    <td><strong>Total Comparisons:</strong></td>
                    <td>{total_comparisons}</td>
                    <td><strong>Average Difference:</strong></td>
                    <td>{avg_diff:.6f}° ({avg_diff_arcmin:.2f}')</td>
                </tr>
                <tr>
                    <td><strong>Maximum Difference:</strong></td>
                    <td>{max_diff:.6f}° ({max_diff_arcmin:.2f}')</td>
                    <td><strong>Overall Accuracy:</strong></td>
                    <td class="{accuracy_class}">{overall_accuracy}</td>
                </tr>
            </table>
        </div>

        <h3>Chart Representation</h3>
        <div class="chart-container">
            <div>
                <div class="chart-title">South Indian Chart</div>
                <pre>{south_indian_chart}</pre>
            </div>
            <div>
                <div class="chart-title">North Indian Chart</div>
                <pre>{north_indian_chart}</pre>
            </div>
        </div>

        <h3>Additional Information</h3>
        <div class="info-section">
            <p><strong>Retrograde Planets:</strong> {retrograde_planets}</p>
            <p><strong>Ketu Verification:</strong> {ketu_verification}</p>
            <p><strong>House System:</strong> Placidus</p>
            <p><strong>Calculation Method:</strong> Swiss Ephemeris</p>
        </div>

        <div class="info-section">
            <h4>Technical Details</h4>
            <p><strong>VedicAstroAPI Version:</strong> v3</p>
            <p><strong>Josi API Version:</strong> v1</p>
            <p><strong>Comparison Date:</strong> {comparison_date}</p>
        </div>
    </div>
</body>
</html>"""

def load_latest_data(filename: str) -> dict:
    """Load latest VedicAstroAPI data."""
    filepath = f"test_data/vedicastro_api/latest_fetch/{filename}"
    with open(filepath, 'r') as f:
        return json.load(f)

def calculate_locally(test_case: dict) -> dict:
    """Calculate using local AstrologyCalculator."""
    calc = AstrologyCalculator()
    
    dob_parts = test_case['dob'].split('/')
    tob_parts = test_case['tob'].split(':')
    
    dt = datetime(
        int(dob_parts[2]), int(dob_parts[1]), int(dob_parts[0]),
        int(tob_parts[0]), int(tob_parts[1])
    )
    
    chart = calc.calculate_vedic_chart(
        dt=dt,
        latitude=test_case['lat'],
        longitude=test_case['lon'],
        timezone="Asia/Kolkata",
        house_system='placidus'
    )
    
    return chart

def create_south_indian_chart(planets: dict, ascendant: dict) -> str:
    """Create ASCII representation of South Indian chart."""
    # Initialize houses
    houses = [[] for _ in range(12)]
    
    # Get ascendant house (always 1 in South Indian)
    asc_sign_num = int(ascendant['longitude'] / 30)
    
    # Place planets in houses based on their sign positions
    for planet, data in planets.items():
        if planet in ['Uranus', 'Neptune', 'Pluto']:
            continue
        sign_num = int(data['longitude'] / 30)
        house_num = (sign_num - asc_sign_num) % 12
        houses[house_num].append(planet[:2])
    
    # Add Ascendant
    houses[0].append('As')
    
    # Format chart
    chart = """
    ┌─────────┬─────────┬─────────┬─────────┐
    │    12   │    1    │    2    │    3    │
    │ {h11:^7} │ {h0:^7} │ {h1:^7} │ {h2:^7} │
    ├─────────┼─────────┴─────────┼─────────┤
    │    11   │                   │    4    │
    │ {h10:^7} │       RASI        │ {h3:^7} │
    ├─────────┤                   ├─────────┤
    │    10   │                   │    5    │
    │ {h9:^7} │                   │ {h4:^7} │
    ├─────────┼─────────┬─────────┼─────────┤
    │    9    │    8    │    7    │    6    │
    │ {h8:^7} │ {h7:^7} │ {h6:^7} │ {h5:^7} │
    └─────────┴─────────┴─────────┴─────────┘
    """.format(
        h0=' '.join(houses[0]) if houses[0] else '',
        h1=' '.join(houses[1]) if houses[1] else '',
        h2=' '.join(houses[2]) if houses[2] else '',
        h3=' '.join(houses[3]) if houses[3] else '',
        h4=' '.join(houses[4]) if houses[4] else '',
        h5=' '.join(houses[5]) if houses[5] else '',
        h6=' '.join(houses[6]) if houses[6] else '',
        h7=' '.join(houses[7]) if houses[7] else '',
        h8=' '.join(houses[8]) if houses[8] else '',
        h9=' '.join(houses[9]) if houses[9] else '',
        h10=' '.join(houses[10]) if houses[10] else '',
        h11=' '.join(houses[11]) if houses[11] else ''
    )
    
    return chart

def create_north_indian_chart(planets: dict, ascendant: dict) -> str:
    """Create ASCII representation of North Indian chart."""
    # Initialize houses with signs
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
        if planet in ['Uranus', 'Neptune', 'Pluto']:
            continue
        sign_num = int(data['longitude'] / 30)
        house_num = (sign_num - asc_sign_num) % 12
        house_planets[house_num].append(planet[:2])
    
    # Add ascendant
    house_planets[0].append('As')
    
    # Format chart
    chart = """
           ┌─────────────────────┐
           │         12          │
           │   {s11}   {p11:^9} │
    ┌──────┼──────┬──────┬──────┼──────┐
    │  11  │      │  As  │      │  2   │
    │ {s10} │  {p10:^4}│ {s0} {p0:^4}│ {p1:^4} │ {s1}  │
    ├──────┼──────┼──────┼──────┼──────┤
    │  10  │      │      │      │  3   │
    │ {s9}  │ {p9:^4} │      │ {p2:^4} │ {s2}  │
    ├──────┼──────┤ RASI ├──────┼──────┤
    │  9   │      │      │      │  4   │
    │ {s8}  │ {p8:^4} │      │ {p3:^4} │ {s3}  │
    ├──────┼──────┼──────┼──────┼──────┤
    │  8   │      │  7   │      │  5   │
    │ {s7}  │ {p7:^4} │ {s6} {p6:^4}│ {p4:^4} │ {s4}  │
    └──────┼──────┴──────┴──────┼──────┘
           │         6          │
           │   {s5}   {p5:^9} │
           └─────────────────────┘
    """.format(
        s0=house_signs[0], s1=house_signs[1], s2=house_signs[2],
        s3=house_signs[3], s4=house_signs[4], s5=house_signs[5],
        s6=house_signs[6], s7=house_signs[7], s8=house_signs[8],
        s9=house_signs[9], s10=house_signs[10], s11=house_signs[11],
        p0=' '.join(house_planets[0][:2]) if house_planets[0] else '',
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

def generate_html_report(person_name: str, vedic_data: dict, local_chart: dict, output_file: str):
    """Generate HTML report for a person."""
    
    test_case = vedic_data['test_case']
    planet_details = vedic_data['data']['planet_details']
    
    # Calculate comparison data
    planet_rows = []
    total_diff = 0
    count = 0
    max_diff = 0
    
    # Planet order
    planet_order = [
        ('0', 'Ascendant', 'Ascendant'),
        ('1', 'Sun', 'Sun'),
        ('2', 'Moon', 'Moon'),
        ('3', 'Mars', 'Mars'),
        ('4', 'Mercury', 'Mercury'),
        ('5', 'Jupiter', 'Jupiter'),
        ('6', 'Venus', 'Venus'),
        ('7', 'Saturn', 'Saturn'),
        ('8', 'Rahu', 'Rahu'),
        ('9', 'Ketu', 'Ketu')
    ]
    
    for planet_id, vedic_name, local_name in planet_order:
        if planet_id in planet_details and isinstance(planet_details[planet_id], dict):
            vedic_pos = planet_details[planet_id].get('global_degree', 0)
            
            if local_name == 'Ascendant':
                local_pos = local_chart['ascendant']['longitude']
                sign = local_chart['ascendant']['sign']
                nakshatra = local_chart['ascendant']['nakshatra']
            elif local_name in local_chart['planets']:
                local_pos = local_chart['planets'][local_name]['longitude']
                sign = local_chart['planets'][local_name]['sign']
                nakshatra = local_chart['planets'][local_name]['nakshatra']
            else:
                continue
            
            diff = abs(vedic_pos - local_pos)
            arc_min = diff * 60
            
            if diff < 0.01:
                accuracy = 'EXCELLENT'
                accuracy_class = 'excellent'
            elif diff < 0.1:
                accuracy = 'GOOD'
                accuracy_class = 'good'
            else:
                accuracy = 'POOR'
                accuracy_class = 'poor'
            
            planet_rows.append(f"""
                <tr>
                    <td><strong>{vedic_name}</strong></td>
                    <td>{vedic_pos:.6f}°</td>
                    <td>{local_pos:.6f}°</td>
                    <td>{diff:.6f}°</td>
                    <td>{arc_min:.2f}'</td>
                    <td class="{accuracy_class}">{accuracy}</td>
                    <td>{sign}</td>
                    <td>{nakshatra}</td>
                </tr>
            """)
            
            if planet_id not in ['8', '9']:  # Don't include Rahu/Ketu in main average
                total_diff += diff
                count += 1
                max_diff = max(max_diff, diff)
    
    # Calculate averages
    avg_diff = total_diff / count if count > 0 else 0
    avg_diff_arcmin = avg_diff * 60
    max_diff_arcmin = max_diff * 60
    
    if avg_diff < 0.01:
        overall_accuracy = 'EXCELLENT'
        accuracy_class = 'excellent'
    elif avg_diff < 0.1:
        overall_accuracy = 'GOOD'
        accuracy_class = 'good'
    else:
        overall_accuracy = 'NEEDS IMPROVEMENT'
        accuracy_class = 'poor'
    
    # Find retrograde planets
    retrograde = []
    for planet_name, planet_data in local_chart['planets'].items():
        if planet_data.get('speed', 0) < 0 and planet_name not in ['Rahu', 'Ketu']:
            retrograde.append(planet_name)
    
    retrograde_planets = ', '.join(retrograde) if retrograde else 'None'
    
    # Ketu verification
    if 'Rahu' in local_chart['planets'] and 'Ketu' in local_chart['planets']:
        rahu_pos = local_chart['planets']['Rahu']['longitude']
        ketu_pos = local_chart['planets']['Ketu']['longitude']
        ketu_expected = (rahu_pos + 180.0) % 360.0
        ketu_diff = abs(ketu_pos - ketu_expected)
        ketu_verification = f"Ketu at {ketu_pos:.6f}° is correctly 180° opposite to Rahu at {rahu_pos:.6f}° ✓" if ketu_diff < 0.0001 else f"ERROR: Ketu position incorrect"
    else:
        ketu_verification = "N/A"
    
    # Generate charts
    south_indian_chart = create_south_indian_chart(local_chart['planets'], local_chart['ascendant'])
    north_indian_chart = create_north_indian_chart(local_chart['planets'], local_chart['ascendant'])
    
    # Fill template
    html_content = HTML_TEMPLATE.format(
        name=person_name,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        dob=test_case['dob'],
        tob=test_case['tob'],
        place=test_case['place'],
        latitude=test_case['lat'],
        longitude=test_case['lon'],
        tz=test_case['tz'],
        ayanamsa_name=local_chart['ayanamsa_name'],
        ayanamsa_value=local_chart['ayanamsa'],
        planet_rows=''.join(planet_rows),
        total_comparisons=count,
        avg_diff=avg_diff,
        avg_diff_arcmin=avg_diff_arcmin,
        max_diff=max_diff,
        max_diff_arcmin=max_diff_arcmin,
        overall_accuracy=overall_accuracy,
        accuracy_class=accuracy_class,
        south_indian_chart=south_indian_chart,
        north_indian_chart=north_indian_chart,
        retrograde_planets=retrograde_planets,
        ketu_verification=ketu_verification,
        comparison_date=datetime.now().strftime("%Y-%m-%d")
    )
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  Generated: {output_file}")

def main():
    """Generate HTML reports for all persons."""
    
    print("Generating HTML Comparison Reports")
    print("=" * 80)
    
    # Create output directory
    output_dir = "reports/html_comparisons"
    os.makedirs(output_dir, exist_ok=True)
    
    # All persons
    test_persons = [
        ("Archana M", "Archana_M_latest.json"),
        ("Valarmathi Kannappan", "Valarmathi_Kannappan_latest.json"),
        ("Janaki Panneerselvam", "Janaki_Panneerselvam_latest.json"),
        ("Govindarajan Panneerselvam", "Govindarajan_Panneerselvam_latest.json"),
        ("Panneerselvam Chandrasekaran", "Panneerselvam_Chandrasekaran_latest.json")
    ]
    
    for person_name, filename in test_persons:
        try:
            print(f"\nProcessing: {person_name}")
            
            # Load data
            vedic_data = load_latest_data(filename)
            test_case = vedic_data['test_case']
            
            # Calculate locally
            local_chart = calculate_locally(test_case)
            
            # Generate HTML
            output_file = f"{output_dir}/{person_name.replace(' ', '_')}_comparison.html"
            generate_html_report(person_name, vedic_data, local_chart, output_file)
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # Generate index file
    index_html = """<!DOCTYPE html>
<html>
<head>
    <title>Astrology Comparison Reports - Index</title>
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
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
        a {
            text-decoration: none;
            color: #4CAF50;
            font-size: 18px;
        }
        a:hover {
            text-decoration: underline;
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
        <h1>Vedic Astrology Comparison Reports</h1>
        <p class="timestamp">Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        <h2>Available Reports:</h2>
        <ul>
            <li><a href="Archana_M_comparison.html">Archana M</a></li>
            <li><a href="Valarmathi_Kannappan_comparison.html">Valarmathi Kannappan</a></li>
            <li><a href="Janaki_Panneerselvam_comparison.html">Janaki Panneerselvam</a></li>
            <li><a href="Govindarajan_Panneerselvam_comparison.html">Govindarajan Panneerselvam</a></li>
            <li><a href="Panneerselvam_Chandrasekaran_comparison.html">Panneerselvam Chandrasekaran</a></li>
        </ul>
    </div>
</body>
</html>"""
    
    with open(f"{output_dir}/index.html", 'w') as f:
        f.write(index_html)
    
    print(f"\n{'='*80}")
    print(f"All reports generated in: {output_dir}/")
    print(f"Open {output_dir}/index.html to view all reports")

if __name__ == "__main__":
    main()