#!/usr/bin/env python3
"""
Regenerate the detailed reports from already collected data.
"""
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent))

from collect_and_analyze_vedicastro import generate_detailed_report

# Paths
TEST_DATA_DIR = Path("test_data/vedicastro_api")

def main():
    """Regenerate all reports"""
    print("Regenerating detailed reports...")
    
    # Find all collected data files
    collected_files = list(TEST_DATA_DIR.glob("collected_*.json"))
    
    for file_path in collected_files:
        print(f"Processing: {file_path.name}")
        
        # Load the data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Generate report
        generate_detailed_report(data['test_case'], data)
    
    print(f"\nRegenerated {len(collected_files)} reports!")

if __name__ == "__main__":
    main()