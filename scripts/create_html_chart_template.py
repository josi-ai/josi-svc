#!/usr/bin/env python3
"""
Create HTML chart templates based on the astro-chart-export format
"""
from datetime import datetime
from pathlib import Path

def create_html_template():
    """Create an HTML template for astrology charts"""
    
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vedic Astrology Chart - {name}</title>
    <style>
        /* Reset and base styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', Courier, monospace;
            background-color: #f0f0f0;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        
        /* Header styles */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .software-version {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        /* Content sections */
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .section-title {{
            font-size: 1.5em;
            color: #667eea;
            margin-bottom: 20px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        /* Birth details grid */
        .birth-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .detail-item {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .detail-label {{
            font-weight: bold;
            color: #555;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        
        .detail-value {{
            color: #333;
            font-size: 1.1em;
        }}
        
        /* Planetary positions table */
        .planet-table {{
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .planet-table th {{
            background-color: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.9em;
        }}
        
        .planet-table td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        
        .planet-table tr:hover {{
            background-color: #f5f5f5;
        }}
        
        .planet-table tr:last-child td {{
            border-bottom: none;
        }}
        
        /* Special planet highlighting */
        .planet-sun {{ color: #ff6b6b; font-weight: bold; }}
        .planet-moon {{ color: #4ecdc4; font-weight: bold; }}
        .planet-mars {{ color: #ff4757; font-weight: bold; }}
        .planet-mercury {{ color: #32a852; font-weight: bold; }}
        .planet-jupiter {{ color: #ffa502; font-weight: bold; }}
        .planet-venus {{ color: #ff6348; font-weight: bold; }}
        .planet-saturn {{ color: #5f27cd; font-weight: bold; }}
        .planet-rahu {{ color: #00d2d3; font-weight: bold; }}
        .planet-ketu {{ color: #54a0ff; font-weight: bold; }}
        
        .retrograde {{
            color: #e74c3c;
            font-weight: bold;
            font-size: 0.8em;
            vertical-align: super;
        }}
        
        /* Chart diagrams */
        .charts-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        
        .chart-wrapper {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            text-align: center;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
            text-transform: uppercase;
        }}
        
        .chart {{
            font-family: monospace;
            white-space: pre;
            text-align: center;
            font-size: 14px;
            line-height: 1.3;
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            border: 2px solid #667eea;
        }}
        
        /* Dasha section */
        .dasha-info {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        
        .dasha-current {{
            font-weight: bold;
            color: #856404;
            font-size: 1.1em;
        }}
        
        /* House table */
        .house-table {{
            width: 100%;
            margin-top: 20px;
        }}
        
        .house-table td {{
            padding: 8px;
            border: 1px solid #ddd;
            text-align: center;
        }}
        
        .house-table .house-number {{
            font-weight: bold;
            background-color: #f0f0f0;
        }}
        
        /* Strength meters */
        .strength-meter {{
            display: inline-block;
            width: 100px;
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-left: 10px;
        }}
        
        .strength-fill {{
            height: 100%;
            background: linear-gradient(to right, #ff4757, #ffa502, #32a852);
            transition: width 0.3s ease;
        }}
        
        /* Footer */
        .footer {{
            background-color: #f0f0f0;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        /* Print styles */
        @media print {{
            body {{
                background-color: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
            
            .section {{
                break-inside: avoid;
            }}
            
            .charts-container {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* Responsive design */
        @media (max-width: 768px) {{
            .charts-container {{
                grid-template-columns: 1fr;
            }}
            
            .birth-details {{
                grid-template-columns: 1fr;
            }}
            
            .planet-table {{
                font-size: 0.9em;
            }}
            
            .chart {{
                font-size: 12px;
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <div class="header">
            <h1>Horoscope of {name}</h1>
            <div class="software-version">(VER 2.0) Generated by Josi Professional Astrology API</div>
        </div>
        
        <!-- Content Section -->
        <div class="content">
            <!-- Birth Details Section -->
            <div class="section">
                <h2 class="section-title">Birth Details</h2>
                <div class="birth-details">
                    <div class="detail-item">
                        <div class="detail-label">Date of Birth</div>
                        <div class="detail-value">{date_of_birth}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Time</div>
                        <div class="detail-value">{time_of_birth} IST</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Place</div>
                        <div class="detail-value">{place_of_birth}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Coordinates</div>
                        <div class="detail-value">{latitude}°N {longitude}°E</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Time Zone</div>
                        <div class="detail-value">IST (GMT +5:30)</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Ayanamsa</div>
                        <div class="detail-value">Lahiri {ayanamsa}°</div>
                    </div>
                </div>
            </div>
            
            <!-- Panchang Details -->
            <div class="section">
                <h2 class="section-title">Panchang Details</h2>
                <div class="birth-details">
                    <div class="detail-item">
                        <div class="detail-label">Nakshatra</div>
                        <div class="detail-value">{nakshatra} Pada {pada}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Tithi</div>
                        <div class="detail-value">{tithi}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Yoga</div>
                        <div class="detail-value">{yoga}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Karana</div>
                        <div class="detail-value">{karana}</div>
                    </div>
                </div>
            </div>
            
            <!-- Planetary Positions -->
            <div class="section">
                <h2 class="section-title">Nirayana Longitudes (Sidereal Positions)</h2>
                <table class="planet-table">
                    <thead>
                        <tr>
                            <th>Planet</th>
                            <th>Degree</th>
                            <th>Sign</th>
                            <th>Nakshatra</th>
                            <th>Pada</th>
                            <th>House</th>
                            <th>Retrograde</th>
                        </tr>
                    </thead>
                    <tbody>
                        {planetary_positions}
                    </tbody>
                </table>
            </div>
            
            <!-- Charts Section -->
            <div class="section">
                <h2 class="section-title">Charts</h2>
                <div class="charts-container">
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
            
            <!-- Dasha Information -->
            <div class="section">
                <h2 class="section-title">Vimshottari Dasha</h2>
                <div class="dasha-info">
                    <div class="dasha-current">Current Period: {current_dasha}</div>
                    <div>Ends on: {dasha_end_date}</div>
                </div>
                <div style="margin-top: 20px;">
                    <h3>Dasha Sequence</h3>
                    {dasha_table}
                </div>
            </div>
            
            <!-- House Cusps -->
            <div class="section">
                <h2 class="section-title">Bhava (House) Details</h2>
                <table class="planet-table">
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
                        {house_details}
                    </tbody>
                </table>
            </div>
            
            <!-- Planetary Strengths -->
            <div class="section">
                <h2 class="section-title">Planetary Strengths</h2>
                <table class="planet-table">
                    <thead>
                        <tr>
                            <th>Planet</th>
                            <th>Shadbala</th>
                            <th>Strength</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {strength_table}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>Generated on: {generation_date}</p>
            <p>© 2025 Josi Professional Astrology API - Astronomical Calculations by Swiss Ephemeris</p>
        </div>
    </div>
</body>
</html>
"""
    
    return template

def generate_sample_data():
    """Generate sample data for the template"""
    
    # Sample planetary positions HTML
    planetary_positions = ""
    planets = [
        ("Sun", "231:29", "Scorpio", "Jyeshta", "2", "8", ""),
        ("Moon", "105:08", "Cancer", "Pushyami", "4", "4", ""),
        ("Mars", "161:49", "Virgo", "Hasta", "1", "6", ""),
        ("Mercury", "218:39", "Scorpio", "Anuradha", "2", "8", "R"),
        ("Jupiter", "325:20", "Aquarius", "P.Bhadra", "2", "11", ""),
        ("Venus", "241:00", "Sagittarius", "Moola", "1", "9", ""),
        ("Saturn", "3:22", "Aries", "Ashwini", "2", "1", "R"),
        ("Rahu", "121:50", "Leo", "Magha", "1", "5", ""),
        ("Ketu", "301:50", "Aquarius", "Dhanista", "3", "11", ""),
        ("Ascendant", "101:06", "Cancer", "Pushyami", "3", "1", ""),
    ]
    
    for planet, degree, sign, nakshatra, pada, house, retro in planets:
        planet_class = f"planet-{planet.lower()}"
        retro_mark = '<span class="retrograde">R</span>' if retro else ''
        planetary_positions += f"""
                        <tr>
                            <td class="{planet_class}">{planet}</td>
                            <td>{degree}</td>
                            <td>{sign}</td>
                            <td>{nakshatra}</td>
                            <td>{pada}</td>
                            <td>{house}</td>
                            <td>{retro_mark}</td>
                        </tr>"""
    
    # Sample charts
    rasi_chart = """+-------+-------+-------+-------+
|       |       |       |       |
|       |SAT    |       |       |
|       |       |       |       |
+-------+-------+-------+-------+
|       |               |CHA    |
|JUP    |               |ASC    |
|KET    |               |       |
+-------+               +-------+
|       |               |RAH    |
|       |               |       |
|       |               |       |
+-------+-------+-------+-------+
|       |       |       |       |
|VEN    |SUN    |       |MAR    |
|       |MER    |       |       |
+-------+-------+-------+-------+"""
    
    navamsa_chart = """+-------+-------+-------+-------+
|       |       |       |       |
|       |RAH    |       |       |
|       |MAR    |       |       |
+-------+-------+-------+-------+
|       |               |       |
|       |               |       |
|       |               |       |
+-------+               +-------+
|SUN    |               |       |
|       |               |       |
|       |               |       |
+-------+-------+-------+-------+
|       |       |       |       |
|       |MOO    |KET    |MER    |
|       |       |ASC    |       |
+-------+-------+-------+-------+"""
    
    # Sample house details
    house_details = ""
    for i in range(1, 13):
        house_details += f"""
                        <tr>
                            <td class="house-number">House {i}</td>
                            <td>{90 + (i-1)*30:.2f}°</td>
                            <td>Sign {i}</td>
                            <td>Lord {i}</td>
                            <td>-</td>
                        </tr>"""
    
    # Sample strength table
    strength_table = ""
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        strength_table += f"""
                        <tr>
                            <td class="planet-{planet.lower()}">{planet}</td>
                            <td>5.45</td>
                            <td>
                                <div class="strength-meter">
                                    <div class="strength-fill" style="width: 70%;"></div>
                                </div>
                            </td>
                            <td>Strong</td>
                        </tr>"""
    
    return {
        "name": "ARCHANA M",
        "date_of_birth": "07-12-1998 MONDAY",
        "time_of_birth": "21:15:00",
        "place_of_birth": "CHENNAI, TAMIL NADU",
        "latitude": "13.08",
        "longitude": "80.27",
        "ayanamsa": "23.85",
        "nakshatra": "PUSHYAMI",
        "pada": "4",
        "tithi": "Krishna Panchami",
        "yoga": "Indra",
        "karana": "Kaulava",
        "planetary_positions": planetary_positions,
        "rasi_chart": rasi_chart,
        "navamsa_chart": navamsa_chart,
        "current_dasha": "KETU DASA - SATURN BUKTHI",
        "dasha_end_date": "12-02-2024",
        "dasha_table": "<p>Dasha details would go here...</p>",
        "house_details": house_details,
        "strength_table": strength_table,
        "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def main():
    """Generate sample HTML files"""
    template = create_html_template()
    
    # Generate for each person
    persons = ["Archana M", "Valarmathi Kannappan", "Janaki Panneerselvam", 
               "Panneerselvam Chandrasekaran", "Govindarajan Panneerselvam"]
    
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    for person_name in persons:
        # Get sample data
        data = generate_sample_data()
        data["name"] = person_name.upper()
        
        # Fill template
        html_content = template.format(**data)
        
        # Save file
        filename = f"astro-chart-export-{person_name.replace(' ', '_').lower()}.html"
        filepath = reports_dir / filename
        filepath.write_text(html_content)
        
        print(f"Generated: {filepath}")
    
    print("\nAll HTML exports generated successfully!")

if __name__ == "__main__":
    main()