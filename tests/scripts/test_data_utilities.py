#!/usr/bin/env python3
"""
Utilities for working with VedicAstroAPI test data.
Provides easy access to stored test results and analysis functions.
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

class TestDataManager:
    """Manager for accessing and analyzing test data"""
    
    def __init__(self, base_path: str = "test_data/vedicastro_api"):
        self.base_path = Path(base_path)
        self.raw_responses_dir = self.base_path / "raw_responses"
        self.processed_data_dir = self.base_path / "processed_data"
        self.validation_results_dir = self.base_path / "validation_results"
    
    def list_test_cases(self) -> List[str]:
        """List all available test cases"""
        test_files = list(self.base_path.glob("collected_*.json"))
        return [f.stem.replace("collected_", "") for f in test_files]
    
    def get_test_case_data(self, test_case_name: str) -> Optional[Dict]:
        """Get complete data for a specific test case"""
        file_path = self.base_path / f"collected_{test_case_name}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    
    def get_planetary_positions(self, test_case_name: Optional[str] = None) -> List[Dict]:
        """Get planetary positions, optionally filtered by test case"""
        file_path = self.processed_data_dir / "planetary_positions.json"
        if not file_path.exists():
            return []
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if test_case_name:
            return [p for p in data if p['test_case'] == test_case_name]
        return data
    
    def get_ascendants(self) -> List[Dict]:
        """Get all ascendant data"""
        file_path = self.processed_data_dir / "ascendants.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return []
    
    def get_latest_validation_report(self) -> Optional[Dict]:
        """Get the most recent validation report"""
        report_files = list(self.validation_results_dir.glob("validation_report_*.json"))
        if not report_files:
            return None
        
        # Sort by filename (which includes timestamp)
        latest_file = sorted(report_files)[-1]
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    def get_validation_history(self) -> List[Dict]:
        """Get all validation reports with summary info"""
        report_files = list(self.validation_results_dir.glob("validation_report_*.json"))
        history = []
        
        for report_file in sorted(report_files):
            with open(report_file, 'r') as f:
                report = json.load(f)
            
            history.append({
                "filename": report_file.name,
                "date": report.get("validation_date", ""),
                "total_tests": report["summary"]["total_tests"],
                "passed": report["summary"]["passed"],
                "failed": report["summary"]["failed"],
                "accuracy": report["summary"]["accuracy_percentage"]
            })
        
        return history
    
    def analyze_discrepancies(self) -> Dict[str, List[Dict]]:
        """Analyze discrepancies from latest validation report"""
        report = self.get_latest_validation_report()
        if not report:
            return {}
        
        discrepancies = report.get("discrepancies", [])
        
        # Group by type
        grouped = {
            "planetary": [],
            "ascendant": [],
            "house": [],
            "panchang": []
        }
        
        for disc in discrepancies:
            if "planet" in disc:
                grouped["planetary"].append(disc)
            elif "ascendant" in disc.get("test_case", "").lower():
                grouped["ascendant"].append(disc)
            elif "house" in disc:
                grouped["house"].append(disc)
            else:
                grouped["panchang"].append(disc)
        
        return grouped
    
    def export_to_csv(self, output_dir: str = "test_data_exports"):
        """Export processed data to CSV files for analysis"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Export planetary positions
        planets = self.get_planetary_positions()
        if planets:
            df = pd.DataFrame(planets)
            df.to_csv(output_path / "planetary_positions.csv", index=False)
            print(f"Exported {len(planets)} planetary positions")
        
        # Export ascendants
        ascendants = self.get_ascendants()
        if ascendants:
            df = pd.DataFrame(ascendants)
            df.to_csv(output_path / "ascendants.csv", index=False)
            print(f"Exported {len(ascendants)} ascendants")
        
        # Export validation history
        history = self.get_validation_history()
        if history:
            df = pd.DataFrame(history)
            df.to_csv(output_path / "validation_history.csv", index=False)
            print(f"Exported {len(history)} validation reports")
    
    def print_summary(self):
        """Print summary of available test data"""
        print("=== Test Data Summary ===")
        
        # Test cases
        test_cases = self.list_test_cases()
        print(f"\nTest Cases: {len(test_cases)}")
        for tc in test_cases[:5]:
            print(f"  - {tc}")
        if len(test_cases) > 5:
            print(f"  ... and {len(test_cases) - 5} more")
        
        # Latest validation
        latest = self.get_latest_validation_report()
        if latest:
            print(f"\nLatest Validation:")
            print(f"  Date: {latest['validation_date'][:10]}")
            print(f"  Accuracy: {latest['summary']['accuracy_percentage']:.2f}%")
            print(f"  Tests: {latest['summary']['total_tests']} (Passed: {latest['summary']['passed']}, Failed: {latest['summary']['failed']})")
        
        # Data files
        print(f"\nData Files:")
        for category in ["planetary_positions", "ascendants", "house_cusps", "panchang_elements"]:
            file_path = self.processed_data_dir / f"{category}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                print(f"  - {category}: {len(data)} entries")

def main():
    """Example usage of test data utilities"""
    manager = TestDataManager()
    
    # Print summary
    manager.print_summary()
    
    # Analyze discrepancies
    print("\n=== Discrepancy Analysis ===")
    discrepancies = manager.analyze_discrepancies()
    for category, items in discrepancies.items():
        if items:
            print(f"\n{category.title()} Discrepancies: {len(items)}")
            for item in items[:3]:
                if "planet" in item:
                    print(f"  - {item['test_case']}/{item['planet']}: diff={item['difference']:.4f}°")
                else:
                    print(f"  - {item}")
    
    # Export to CSV
    print("\n=== Exporting Data ===")
    manager.export_to_csv()

if __name__ == "__main__":
    main()