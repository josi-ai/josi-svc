#!/usr/bin/env python3
"""
Generate a detailed comparison report between our API and VedicAstroAPI
"""
import json
import asyncio
import httpx
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from tabulate import tabulate
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
OUR_API_BASE = "http://localhost:8000/api/v1"
API_KEY = "test-api-key"
TEST_DATA_DIR = Path(__file__).parent.parent / "test_data" / "vedicastro_api"
REPORTS_DIR = Path(__file__).parent.parent / "reports"

class ComparisonReporter:
    """Generate detailed comparison reports between our API and VedicAstroAPI"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.headers = {"X-API-Key": API_KEY}
        self.results = []
        
    async def close(self):
        await self.client.aclose()
        
    async def create_person(self, test_case: Dict) -> Optional[str]:
        """Create a person for testing"""
        dob_parts = test_case['dob'].split('/')
        tob_parts = test_case['tob'].split(':')
        
        person_data = {
            "name": test_case.get('name', 'Test Person'),
            "date_of_birth": f"{dob_parts[2]}-{dob_parts[1]}-{dob_parts[0]}",
            "time_of_birth": f"{tob_parts[0]}:{tob_parts[1]}:00",
            "place_of_birth": test_case.get('place', 'Test Location'),
            "latitude": test_case['lat'],
            "longitude": test_case['lon'],
            "timezone": "Asia/Kolkata" if test_case['tz'] == 5.5 else str(test_case['tz']),
            "gender": test_case.get('gender', 'male')
        }
        
        try:
            response = await self.client.post(
                f"{OUR_API_BASE}/persons/",
                json=person_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()['data']['person_id']
            else:
                logger.error(f"Failed to create person: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating person: {e}")
            return None
            
    async def get_chart_data(self, person_id: str) -> Optional[Dict]:
        """Get chart calculation from our API"""
        try:
            response = await self.client.post(
                f"{OUR_API_BASE}/charts/calculate/",
                params={
                    "person_id": person_id,
                    "systems": "vedic",
                    "house_system": "placidus",
                    "ayanamsa": "lahiri"
                },
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()['data'][0]
            else:
                logger.error(f"Chart calculation failed: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error calculating chart: {e}")
            return None
            
    def compare_planetary_positions(self, our_data: Dict, vedic_data: Dict) -> Dict:
        """Compare planetary positions between our API and VedicAstroAPI"""
        comparison = {
            "person_name": vedic_data['test_case']['name'],
            "birth_datetime": f"{vedic_data['test_case']['dob']} {vedic_data['test_case']['tob']}",
            "place": vedic_data['test_case']['place'],
            "planetary_comparisons": []
        }
        
        # Map planet names
        planet_map = {
            '0': 'Ascendant',
            '1': 'Sun',
            '2': 'Moon', 
            '3': 'Mars',
            '4': 'Mercury',
            '5': 'Jupiter',
            '6': 'Venus',
            '7': 'Saturn',
            '8': 'Rahu',
            '9': 'Ketu'
        }
        
        # Get VedicAstroAPI planet details
        vedic_planets = vedic_data['data'].get('planet_details', {})
        our_planets = our_data.get('planet_positions', {})
        
        for planet_key, planet_name in planet_map.items():
            if planet_key not in vedic_planets:
                continue
                
            vedic_planet = vedic_planets[planet_key]
            vedic_longitude = vedic_planet['global_degree']
            vedic_sign = vedic_planet.get('sign', 'N/A')
            vedic_house = vedic_planet.get('house', 'N/A')
            
            # Get our data
            if planet_name == 'Ascendant':
                our_longitude = our_data.get('chart_data', {}).get('ascendant', {}).get('longitude', 0)
                our_sign = our_data.get('chart_data', {}).get('ascendant', {}).get('sign', 'N/A')
                our_house = 1  # Ascendant is always in 1st house
            else:
                our_planet_data = our_planets.get(planet_name, {})
                our_longitude = our_planet_data.get('longitude', 0)
                our_sign = our_planet_data.get('sign', 'N/A')
                our_house = our_planet_data.get('house', 'N/A')
            
            # Calculate difference
            diff_degrees = abs(vedic_longitude - our_longitude)
            
            # Determine accuracy
            if diff_degrees < 0.01:
                accuracy = "EXCELLENT"
                accuracy_color = "green"
            elif diff_degrees < 0.1:
                accuracy = "GOOD"
                accuracy_color = "yellow"
            elif diff_degrees < 1.0:
                accuracy = "FAIR"
                accuracy_color = "orange"
            else:
                accuracy = "POOR"
                accuracy_color = "red"
                
            comparison['planetary_comparisons'].append({
                "planet": planet_name,
                "vedic_longitude": vedic_longitude,
                "our_longitude": our_longitude,
                "difference_degrees": diff_degrees,
                "vedic_sign": vedic_sign,
                "our_sign": our_sign,
                "vedic_house": vedic_house,
                "our_house": our_house,
                "accuracy": accuracy,
                "accuracy_color": accuracy_color
            })
            
        return comparison
        
    async def generate_comparison_report(self):
        """Generate comprehensive comparison report"""
        # Load test cases
        test_cases = []
        for test_file in TEST_DATA_DIR.glob("collected_*.json"):
            with open(test_file, 'r') as f:
                test_cases.append(json.load(f))
                
        logger.info(f"Found {len(test_cases)} test cases")
        
        # Process each test case
        for vedic_data in test_cases:
            logger.info(f"Processing: {vedic_data['test_case']['name']}")
            
            # Create person
            person_id = await self.create_person(vedic_data['test_case'])
            if not person_id:
                continue
                
            # Get our chart data
            our_data = await self.get_chart_data(person_id)
            if not our_data:
                continue
                
            # Compare and store results
            comparison = self.compare_planetary_positions(our_data, vedic_data)
            self.results.append(comparison)
            
        # Generate report
        self.create_html_report()
        self.create_markdown_report()
        self.create_json_report()
        
    def create_html_report(self):
        """Create HTML comparison report"""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Josi API vs VedicAstroAPI Comparison Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #333; }
        .summary { background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .test-case { margin-bottom: 40px; border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
        .person-info { background-color: #f9f9f9; padding: 10px; margin-bottom: 15px; border-left: 4px solid #2196F3; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #2196F3; color: white; }
        .excellent { color: #4CAF50; font-weight: bold; }
        .good { color: #FF9800; font-weight: bold; }
        .fair { color: #FF5722; font-weight: bold; }
        .poor { color: #F44336; font-weight: bold; }
        .diff-small { background-color: #E8F5E9; }
        .diff-medium { background-color: #FFF3E0; }
        .diff-large { background-color: #FFEBEE; }
        .stats { display: flex; justify-content: space-around; margin-bottom: 20px; }
        .stat-box { text-align: center; padding: 15px; background-color: #f0f0f0; border-radius: 5px; }
        .stat-number { font-size: 2em; font-weight: bold; color: #2196F3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔮 Josi API vs VedicAstroAPI Comparison Report</h1>
        <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">""" + str(len(self.results)) + """</div>
                    <div>Test Cases</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">""" + str(sum(len(r['planetary_comparisons']) for r in self.results)) + """</div>
                    <div>Comparisons</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">""" + f"{self.calculate_overall_accuracy():.2f}%" + """</div>
                    <div>Overall Accuracy</div>
                </div>
            </div>
        </div>
        """
        
        for result in self.results:
            html_content += f"""
        <div class="test-case">
            <h2>{result['person_name']}</h2>
            <div class="person-info">
                <strong>Birth:</strong> {result['birth_datetime']} | 
                <strong>Place:</strong> {result['place']}
            </div>
            
            <table>
                <tr>
                    <th>Planet</th>
                    <th>VedicAstroAPI Position</th>
                    <th>Our API Position</th>
                    <th>Difference (°)</th>
                    <th>VedicAstro Sign</th>
                    <th>Our Sign</th>
                    <th>Accuracy</th>
                </tr>
            """
            
            for comp in result['planetary_comparisons']:
                diff_class = ''
                if comp['difference_degrees'] < 0.01:
                    diff_class = 'diff-small'
                elif comp['difference_degrees'] < 0.1:
                    diff_class = 'diff-medium'
                else:
                    diff_class = 'diff-large'
                    
                html_content += f"""
                <tr class="{diff_class}">
                    <td><strong>{comp['planet']}</strong></td>
                    <td>{comp['vedic_longitude']:.6f}°</td>
                    <td>{comp['our_longitude']:.6f}°</td>
                    <td>{comp['difference_degrees']:.6f}°</td>
                    <td>{comp['vedic_sign']}</td>
                    <td>{comp['our_sign']}</td>
                    <td class="{comp['accuracy'].lower()}">{comp['accuracy']}</td>
                </tr>
                """
                
            html_content += """
            </table>
        </div>
            """
            
        html_content += """
    </div>
</body>
</html>
        """
        
        # Save HTML report
        report_path = REPORTS_DIR / f"api_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path.write_text(html_content)
        logger.info(f"HTML report saved to: {report_path}")
        
    def create_markdown_report(self):
        """Create Markdown comparison report"""
        md_content = f"""# Josi API vs VedicAstroAPI Comparison Report

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Executive Summary

- **Total Test Cases**: {len(self.results)}
- **Total Comparisons**: {sum(len(r['planetary_comparisons']) for r in self.results)}
- **Overall Accuracy**: {self.calculate_overall_accuracy():.2f}%

## Accuracy Criteria

- **EXCELLENT**: < 0.01° difference (36 arcseconds)
- **GOOD**: < 0.1° difference (6 arcminutes)
- **FAIR**: < 1.0° difference
- **POOR**: ≥ 1.0° difference

## Detailed Results by Test Case
"""
        
        for result in self.results:
            md_content += f"\n### {result['person_name']}\n\n"
            md_content += f"**Birth**: {result['birth_datetime']} | **Place**: {result['place']}\n\n"
            
            # Create table
            headers = ["Planet", "VedicAstroAPI (°)", "Our API (°)", "Difference (°)", "Accuracy"]
            rows = []
            
            for comp in result['planetary_comparisons']:
                rows.append([
                    comp['planet'],
                    f"{comp['vedic_longitude']:.6f}",
                    f"{comp['our_longitude']:.6f}",
                    f"{comp['difference_degrees']:.6f}",
                    comp['accuracy']
                ])
                
            md_content += tabulate(rows, headers=headers, tablefmt="pipe") + "\n"
            
            # Add sign comparison
            md_content += "\n#### Sign Positions\n\n"
            sign_headers = ["Planet", "VedicAstroAPI Sign", "Our API Sign", "Match"]
            sign_rows = []
            
            for comp in result['planetary_comparisons']:
                match = "✅" if comp['vedic_sign'] == comp['our_sign'] else "❌"
                sign_rows.append([
                    comp['planet'],
                    comp['vedic_sign'],
                    comp['our_sign'],
                    match
                ])
                
            md_content += tabulate(sign_rows, headers=sign_headers, tablefmt="pipe") + "\n"
            
        # Add statistics
        md_content += self.generate_statistics_section()
        
        # Save Markdown report
        report_path = REPORTS_DIR / f"api_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.write_text(md_content)
        logger.info(f"Markdown report saved to: {report_path}")
        
    def create_json_report(self):
        """Create JSON comparison report"""
        report = {
            "report_generated": datetime.now().isoformat(),
            "summary": {
                "total_test_cases": len(self.results),
                "total_comparisons": sum(len(r['planetary_comparisons']) for r in self.results),
                "overall_accuracy_percentage": self.calculate_overall_accuracy(),
                "accuracy_by_planet": self.calculate_accuracy_by_planet()
            },
            "detailed_results": self.results
        }
        
        # Save JSON report
        report_path = REPORTS_DIR / f"api_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"JSON report saved to: {report_path}")
        
    def calculate_overall_accuracy(self) -> float:
        """Calculate overall accuracy percentage"""
        total_excellent = 0
        total_comparisons = 0
        
        for result in self.results:
            for comp in result['planetary_comparisons']:
                if comp['accuracy'] == 'EXCELLENT':
                    total_excellent += 1
                total_comparisons += 1
                
        return (total_excellent / total_comparisons * 100) if total_comparisons > 0 else 0
        
    def calculate_accuracy_by_planet(self) -> Dict:
        """Calculate accuracy statistics by planet"""
        planet_stats = {}
        
        for result in self.results:
            for comp in result['planetary_comparisons']:
                planet = comp['planet']
                if planet not in planet_stats:
                    planet_stats[planet] = {
                        'total': 0,
                        'excellent': 0,
                        'good': 0,
                        'fair': 0,
                        'poor': 0,
                        'avg_difference': 0,
                        'differences': []
                    }
                    
                planet_stats[planet]['total'] += 1
                planet_stats[planet][comp['accuracy'].lower()] += 1
                planet_stats[planet]['differences'].append(comp['difference_degrees'])
                
        # Calculate averages
        for planet, stats in planet_stats.items():
            if stats['differences']:
                stats['avg_difference'] = sum(stats['differences']) / len(stats['differences'])
                del stats['differences']  # Remove raw data from final report
                
        return planet_stats
        
    def generate_statistics_section(self) -> str:
        """Generate statistics section for markdown report"""
        stats = self.calculate_accuracy_by_planet()
        
        md = "\n## Statistical Analysis\n\n"
        md += "### Accuracy by Planet\n\n"
        
        headers = ["Planet", "Total Tests", "Excellent", "Good", "Fair", "Poor", "Avg Difference (°)"]
        rows = []
        
        for planet, data in sorted(stats.items()):
            rows.append([
                planet,
                data['total'],
                data['excellent'],
                data['good'],
                data['fair'],
                data['poor'],
                f"{data['avg_difference']:.6f}"
            ])
            
        md += tabulate(rows, headers=headers, tablefmt="pipe") + "\n"
        
        return md

async def main():
    """Main execution function"""
    reporter = ComparisonReporter()
    
    try:
        # Ensure reports directory exists
        REPORTS_DIR.mkdir(exist_ok=True)
        
        # Check API health
        response = await reporter.client.get(f"{OUR_API_BASE}/health/")
        if response.status_code != 200:
            logger.error("API is not healthy")
            return
            
        logger.info("Starting comparison report generation...")
        await reporter.generate_comparison_report()
        
        print("\n" + "="*60)
        print("COMPARISON REPORT GENERATION COMPLETE")
        print("="*60)
        print(f"Reports saved to: {REPORTS_DIR}")
        print("\nGenerated files:")
        for file in sorted(REPORTS_DIR.glob("api_comparison_report_*.html")):
            print(f"  - {file.name}")
        for file in sorted(REPORTS_DIR.glob("api_comparison_report_*.md")):
            print(f"  - {file.name}")
        for file in sorted(REPORTS_DIR.glob("api_comparison_report_*.json")):
            print(f"  - {file.name}")
        print("="*60)
        
    finally:
        await reporter.close()

if __name__ == "__main__":
    asyncio.run(main())