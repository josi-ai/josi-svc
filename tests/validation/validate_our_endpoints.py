#!/usr/bin/env python3
"""
Comprehensive validation script to test our API endpoints against VedicAstroAPI data.
This script uses the exact same inputs that were used to collect data from VedicAstroAPI
to ensure a true 1-to-1 comparison.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
import httpx
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.josi.core.config import settings

console = Console()

# Our API configuration
API_BASE_URL = "http://localhost:8001/v1"
API_KEY = os.getenv("JOSI_API_KEY", "test-api-key")

# Test data directory
TEST_DATA_DIR = project_root / "test_data" / "vedicastro_api"

# Tolerance levels for comparison
PLANET_POSITION_TOLERANCE = 1.0  # degrees
ASCENDANT_TOLERANCE = 1.0  # degrees
HOUSE_TOLERANCE = 1.0  # degrees
TIME_TOLERANCE = 300  # seconds (5 minutes) for dasha periods


class EndpointValidator:
    """Validates our API endpoints against VedicAstroAPI reference data."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=API_BASE_URL,
            headers={"X-API-Key": API_KEY},
            timeout=30.0
        )
        self.validation_results = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        
    def load_test_data(self, person_name: str) -> Dict[str, Any]:
        """Load collected test data for a person."""
        file_path = TEST_DATA_DIR / f"collected_{person_name.replace(' ', '_')}.json"
        with open(file_path, 'r') as f:
            return json.load(f)
            
    async def create_person(self, test_data: Dict[str, Any]) -> str:
        """Create a person in our API and return the person_id."""
        person_data = {
            "name": test_data["name"],
            "birth_date": test_data["date_of_birth"],
            "birth_time": test_data["time_of_birth"],
            "birth_place": test_data["place_of_birth"],
            "latitude": test_data["latitude"],
            "longitude": test_data["longitude"],
            "timezone": test_data["timezone"]
        }
        
        response = await self.client.post("/persons", json=person_data)
        response.raise_for_status()
        result = response.json()
        return result["data"]["person_id"]
        
    async def validate_planetary_positions(self, person_id: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate planetary positions against reference data."""
        # Get chart from our API
        response = await self.client.get(f"/charts/{person_id}/vedic")
        response.raise_for_status()
        our_data = response.json()["data"]
        
        # Reference data from VedicAstroAPI
        ref_positions = test_data["planet_positions"]
        
        validation_result = {
            "endpoint": "planetary_positions",
            "status": "passed",
            "failures": [],
            "comparisons": []
        }
        
        # Compare each planet
        for planet_name, ref_data in ref_positions.items():
            our_planet = None
            
            # Find matching planet in our data
            for p in our_data.get("planets", []):
                if p["name"].lower() == planet_name.lower():
                    our_planet = p
                    break
                    
            if not our_planet:
                validation_result["failures"].append(f"Planet {planet_name} not found in our API response")
                validation_result["status"] = "failed"
                continue
                
            # Compare longitude
            ref_longitude = ref_data["longitude"]
            our_longitude = our_planet["longitude"]
            diff = abs(ref_longitude - our_longitude)
            
            comparison = {
                "planet": planet_name,
                "reference_longitude": ref_longitude,
                "our_longitude": our_longitude,
                "difference": diff,
                "within_tolerance": diff <= PLANET_POSITION_TOLERANCE
            }
            
            validation_result["comparisons"].append(comparison)
            
            if diff > PLANET_POSITION_TOLERANCE:
                validation_result["failures"].append(
                    f"{planet_name}: difference {diff:.2f}° exceeds tolerance {PLANET_POSITION_TOLERANCE}°"
                )
                validation_result["status"] = "failed"
                
        return validation_result
        
    async def validate_houses(self, person_id: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate house calculations against reference data."""
        # Get chart from our API
        response = await self.client.get(f"/charts/{person_id}/vedic")
        response.raise_for_status()
        our_data = response.json()["data"]
        
        # Reference data from VedicAstroAPI
        ref_houses = test_data.get("houses", {})
        
        validation_result = {
            "endpoint": "houses",
            "status": "passed",
            "failures": [],
            "comparisons": []
        }
        
        # Check ascendant
        ref_ascendant = test_data.get("ascendant_degree", 0)
        our_ascendant = our_data.get("ascendant", {}).get("degree", 0)
        asc_diff = abs(ref_ascendant - our_ascendant)
        
        validation_result["comparisons"].append({
            "house": "Ascendant",
            "reference_degree": ref_ascendant,
            "our_degree": our_ascendant,
            "difference": asc_diff,
            "within_tolerance": asc_diff <= ASCENDANT_TOLERANCE
        })
        
        if asc_diff > ASCENDANT_TOLERANCE:
            validation_result["failures"].append(
                f"Ascendant: difference {asc_diff:.2f}° exceeds tolerance {ASCENDANT_TOLERANCE}°"
            )
            validation_result["status"] = "failed"
            
        # Compare house cusps if available
        our_houses = our_data.get("houses", [])
        for house_num in range(1, 13):
            ref_house = ref_houses.get(str(house_num), {})
            our_house = next((h for h in our_houses if h["number"] == house_num), None)
            
            if ref_house and our_house:
                ref_degree = ref_house.get("degree", 0)
                our_degree = our_house.get("degree", 0)
                diff = abs(ref_degree - our_degree)
                
                validation_result["comparisons"].append({
                    "house": f"House {house_num}",
                    "reference_degree": ref_degree,
                    "our_degree": our_degree,
                    "difference": diff,
                    "within_tolerance": diff <= HOUSE_TOLERANCE
                })
                
                if diff > HOUSE_TOLERANCE:
                    validation_result["failures"].append(
                        f"House {house_num}: difference {diff:.2f}° exceeds tolerance {HOUSE_TOLERANCE}°"
                    )
                    validation_result["status"] = "failed"
                    
        return validation_result
        
    async def validate_dasha(self, person_id: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Vimshottari Dasha calculations against reference data."""
        # Get dasha from our API
        response = await self.client.get(f"/charts/{person_id}/dasha")
        response.raise_for_status()
        our_data = response.json()["data"]
        
        # Reference data from VedicAstroAPI
        ref_mahadasha = test_data.get("mahadasha", [])
        
        validation_result = {
            "endpoint": "vimshottari_dasha",
            "status": "passed",
            "failures": [],
            "comparisons": []
        }
        
        # Compare mahadasha periods
        our_mahadasha = our_data.get("vimshottari", {}).get("mahadasha", [])
        
        for i, ref_period in enumerate(ref_mahadasha[:5]):  # Compare first 5 periods
            if i >= len(our_mahadasha):
                validation_result["failures"].append(f"Missing mahadasha period {i+1}")
                validation_result["status"] = "failed"
                continue
                
            our_period = our_mahadasha[i]
            
            # Compare planet
            ref_planet = ref_period["planet"]
            our_planet = our_period.get("planet", "")
            
            if ref_planet.lower() != our_planet.lower():
                validation_result["failures"].append(
                    f"Mahadasha {i+1}: planet mismatch - expected {ref_planet}, got {our_planet}"
                )
                validation_result["status"] = "failed"
                
            # Compare dates (if available)
            comparison = {
                "period": f"Mahadasha {i+1}",
                "reference_planet": ref_planet,
                "our_planet": our_planet,
                "planets_match": ref_planet.lower() == our_planet.lower()
            }
            
            validation_result["comparisons"].append(comparison)
            
        return validation_result
        
    async def validate_dosha(self, person_id: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate dosha analysis against reference data."""
        validation_result = {
            "endpoint": "dosha_analysis",
            "status": "passed",
            "failures": [],
            "comparisons": []
        }
        
        # Get Manglik dosha from our API
        try:
            response = await self.client.get(f"/charts/{person_id}/manglik-dosha")
            response.raise_for_status()
            our_manglik = response.json()["data"]
            
            # Reference data
            ref_manglik = test_data.get("mangal_dosha", {})
            
            # Compare Manglik dosha presence
            ref_has_manglik = ref_manglik.get("has_dosha", False)
            our_has_manglik = our_manglik.get("has_dosha", False)
            
            validation_result["comparisons"].append({
                "dosha": "Manglik",
                "reference_present": ref_has_manglik,
                "our_present": our_has_manglik,
                "matches": ref_has_manglik == our_has_manglik
            })
            
            if ref_has_manglik != our_has_manglik:
                validation_result["failures"].append(
                    f"Manglik dosha mismatch - reference: {ref_has_manglik}, ours: {our_has_manglik}"
                )
                validation_result["status"] = "failed"
                
        except Exception as e:
            validation_result["failures"].append(f"Error validating Manglik dosha: {str(e)}")
            validation_result["status"] = "failed"
            
        # Get Kaal Sarp dosha from our API
        try:
            response = await self.client.get(f"/charts/{person_id}/kaalsarp-dosha")
            response.raise_for_status()
            our_kaalsarp = response.json()["data"]
            
            # Reference data
            ref_kaalsarp = test_data.get("kaalsarp_dosha", {})
            
            # Compare Kaal Sarp dosha presence
            ref_has_kaalsarp = ref_kaalsarp.get("present", False)
            our_has_kaalsarp = our_kaalsarp.get("present", False)
            
            validation_result["comparisons"].append({
                "dosha": "Kaal Sarp",
                "reference_present": ref_has_kaalsarp,
                "our_present": our_has_kaalsarp,
                "matches": ref_has_kaalsarp == our_has_kaalsarp
            })
            
            if ref_has_kaalsarp != our_has_kaalsarp:
                validation_result["failures"].append(
                    f"Kaal Sarp dosha mismatch - reference: {ref_has_kaalsarp}, ours: {our_has_kaalsarp}"
                )
                validation_result["status"] = "failed"
                
        except Exception as e:
            validation_result["failures"].append(f"Error validating Kaal Sarp dosha: {str(e)}")
            validation_result["status"] = "failed"
            
        return validation_result
        
    async def validate_person(self, person_name: str) -> Dict[str, Any]:
        """Run all validations for a person."""
        console.print(f"\n[bold cyan]Validating: {person_name}[/bold cyan]")
        
        # Load test data
        test_data = self.load_test_data(person_name)
        
        # Create person in our API
        person_id = await self.create_person(test_data)
        console.print(f"Created person with ID: {person_id}")
        
        person_results = {
            "name": person_name,
            "person_id": person_id,
            "validations": []
        }
        
        # Run validations
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Planetary positions
            task = progress.add_task("Validating planetary positions...", total=None)
            result = await self.validate_planetary_positions(person_id, test_data)
            person_results["validations"].append(result)
            progress.remove_task(task)
            
            # Houses
            task = progress.add_task("Validating houses...", total=None)
            result = await self.validate_houses(person_id, test_data)
            person_results["validations"].append(result)
            progress.remove_task(task)
            
            # Dasha
            task = progress.add_task("Validating Vimshottari Dasha...", total=None)
            result = await self.validate_dasha(person_id, test_data)
            person_results["validations"].append(result)
            progress.remove_task(task)
            
            # Dosha
            task = progress.add_task("Validating dosha analysis...", total=None)
            result = await self.validate_dosha(person_id, test_data)
            person_results["validations"].append(result)
            progress.remove_task(task)
            
        return person_results
        
    def print_validation_summary(self, results: List[Dict[str, Any]]):
        """Print a summary of all validation results."""
        console.print("\n[bold]Validation Summary[/bold]")
        
        # Overall statistics
        total_tests = 0
        passed_tests = 0
        
        for person_result in results:
            person_name = person_result["name"]
            
            # Create table for this person
            table = Table(title=f"\n{person_name}", show_header=True, header_style="bold magenta")
            table.add_column("Endpoint", style="cyan", width=25)
            table.add_column("Status", width=10)
            table.add_column("Details", width=50)
            
            for validation in person_result["validations"]:
                total_tests += 1
                status = validation["status"]
                if status == "passed":
                    passed_tests += 1
                    status_display = "[green]PASSED[/green]"
                else:
                    status_display = "[red]FAILED[/red]"
                    
                # Create details
                details = []
                if validation["failures"]:
                    details.extend(validation["failures"][:2])  # Show first 2 failures
                    if len(validation["failures"]) > 2:
                        details.append(f"... and {len(validation['failures']) - 2} more")
                else:
                    details.append(f"{len(validation['comparisons'])} comparisons passed")
                    
                table.add_row(
                    validation["endpoint"],
                    status_display,
                    "\n".join(details)
                )
                
            console.print(table)
            
        # Overall summary
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary_panel = Panel(
            f"[bold]Total Tests:[/bold] {total_tests}\n"
            f"[bold]Passed:[/bold] [green]{passed_tests}[/green]\n"
            f"[bold]Failed:[/bold] [red]{total_tests - passed_tests}[/red]\n"
            f"[bold]Success Rate:[/bold] {success_rate:.1f}%",
            title="Overall Results",
            expand=False
        )
        console.print("\n", summary_panel)
        
    def save_detailed_report(self, results: List[Dict[str, Any]]):
        """Save detailed validation report."""
        report_path = TEST_DATA_DIR / "validation_results" / f"endpoint_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        console.print(f"\n[green]Detailed report saved to:[/green] {report_path}")
        
        # Also save a markdown report
        md_path = report_path.with_suffix('.md')
        self.save_markdown_report(results, md_path)
        console.print(f"[green]Markdown report saved to:[/green] {md_path}")
        
    def save_markdown_report(self, results: List[Dict[str, Any]], path: Path):
        """Save results as a markdown report."""
        with open(path, 'w') as f:
            f.write("# API Endpoint Validation Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary
            total_tests = sum(len(p["validations"]) for p in results)
            passed_tests = sum(1 for p in results for v in p["validations"] if v["status"] == "passed")
            
            f.write("## Summary\n\n")
            f.write(f"- Total Tests: {total_tests}\n")
            f.write(f"- Passed: {passed_tests}\n")
            f.write(f"- Failed: {total_tests - passed_tests}\n")
            f.write(f"- Success Rate: {passed_tests/total_tests*100:.1f}%\n\n")
            
            # Detailed results
            f.write("## Detailed Results\n\n")
            
            for person_result in results:
                f.write(f"### {person_result['name']}\n\n")
                
                for validation in person_result["validations"]:
                    f.write(f"#### {validation['endpoint']}\n\n")
                    f.write(f"Status: **{validation['status'].upper()}**\n\n")
                    
                    if validation["failures"]:
                        f.write("Failures:\n")
                        for failure in validation["failures"]:
                            f.write(f"- {failure}\n")
                        f.write("\n")
                        
                    if validation["comparisons"]:
                        f.write("Comparisons:\n")
                        f.write("| Item | Reference | Our Value | Difference | Status |\n")
                        f.write("|------|-----------|-----------|------------|--------|\n")
                        
                        for comp in validation["comparisons"][:10]:  # Show first 10
                            if "difference" in comp:
                                status = "✓" if comp.get("within_tolerance", True) else "✗"
                                f.write(f"| {comp.get('planet', comp.get('house', comp.get('period', 'Unknown')))} | "
                                       f"{comp.get('reference_longitude', comp.get('reference_degree', 'N/A')):.2f} | "
                                       f"{comp.get('our_longitude', comp.get('our_degree', 'N/A')):.2f} | "
                                       f"{comp.get('difference', 0):.2f} | {status} |\n")
                            else:
                                status = "✓" if comp.get('matches', comp.get('planets_match', False)) else "✗"
                                f.write(f"| {comp.get('dosha', comp.get('period', 'Unknown'))} | "
                                       f"{comp.get('reference_planet', comp.get('reference_present', 'N/A'))} | "
                                       f"{comp.get('our_planet', comp.get('our_present', 'N/A'))} | "
                                       f"- | {status} |\n")
                                       
                        f.write("\n")


async def main():
    """Run the validation process."""
    console.print(Panel("API Endpoint Validation", style="bold blue"))
    
    # Test cases to validate
    test_cases = [
        "Panneerselvam Chandrasekaran",
        "Valarmathi Kannappan", 
        "Janaki Panneerselvam",
        "Govindarajan Panneerselvam"
    ]
    
    results = []
    
    async with EndpointValidator() as validator:
        for person_name in test_cases:
            try:
                person_results = await validator.validate_person(person_name)
                results.append(person_results)
            except Exception as e:
                console.print(f"[red]Error validating {person_name}: {str(e)}[/red]")
                import traceback
                traceback.print_exc()
                
        # Print summary
        validator.print_validation_summary(results)
        
        # Save detailed report
        validator.save_detailed_report(results)


if __name__ == "__main__":
    asyncio.run(main())