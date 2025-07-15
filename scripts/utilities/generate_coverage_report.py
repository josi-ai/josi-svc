#!/usr/bin/env python3
"""
Generate comprehensive test coverage report for core astrology modules.
Target: 90% coverage for all core calculation logic.
"""
import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

# Define core astrology modules to measure
CORE_MODULES = {
    "astrology_service": "src/josi/services/astrology_service.py",
    "vedic.dasha_service": "src/josi/services/vedic/dasha_service.py",
    "vedic.panchang_service": "src/josi/services/vedic/panchang_service.py",
    "vedic.muhurta_service": "src/josi/services/vedic/muhurta_service.py",
    "vedic.ashtakoota_service": "src/josi/services/vedic/ashtakoota_service.py",
    "chinese.bazi_calculator_service": "src/josi/services/chinese/bazi_calculator_service.py",
    "western.progressions_service": "src/josi/services/western/progressions_service.py",
    "numerology_service": "src/josi/services/numerology_service.py"
}

# Test files created for comprehensive coverage
NEW_TEST_FILES = [
    "tests/unit/services/test_astrology_service_comprehensive.py",
    "tests/unit/services/vedic/test_comprehensive_vedic.py",
    "tests/unit/services/test_chinese_western_comprehensive.py",
    "tests/unit/services/test_astronomical_edge_cases.py",
    "tests/unit/services/test_performance_benchmarks.py"
]

# Existing test files
EXISTING_TEST_FILES = [
    "tests/unit/services/test_astrology_service.py",
    "tests/unit/services/vedic/test_dasha_service.py",
    "tests/unit/services/vedic/test_panchang_service.py",
    "tests/unit/services/vedic/test_muhurta_service.py",
    "tests/unit/services/vedic/test_ashtakoota_service.py",
    "tests/unit/services/chinese/test_bazi_calculator_service.py",
    "tests/unit/services/western/test_progressions_service.py",
    "tests/unit/services/test_numerology_service.py"
]

def run_coverage_analysis():
    """Run pytest with coverage for all test files."""
    print("=" * 80)
    print("ASTROLOGY MODULE TEST COVERAGE REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Coverage: 90%")
    print("=" * 80)
    print()
    
    # Combine all test files
    all_test_files = []
    for test_file in NEW_TEST_FILES + EXISTING_TEST_FILES:
        if os.path.exists(test_file):
            all_test_files.append(test_file)
    
    print(f"Found {len(all_test_files)} test files")
    print()
    
    # Build coverage command
    coverage_modules = "josi.services.astrology_service,"
    coverage_modules += "josi.services.vedic.dasha_service,"
    coverage_modules += "josi.services.vedic.panchang_service,"
    coverage_modules += "josi.services.vedic.muhurta_service,"
    coverage_modules += "josi.services.vedic.ashtakoota_service,"
    coverage_modules += "josi.services.chinese.bazi_calculator_service,"
    coverage_modules += "josi.services.western.progressions_service,"
    coverage_modules += "josi.services.numerology_service"
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=" + coverage_modules,
        "--cov-report=term-missing:skip-covered",
        "--cov-report=json:coverage.json",
        "--cov-report=html:htmlcov",
        "--cov-fail-under=90",  # Fail if under 90%
        "-v",
        "--tb=short"
    ] + all_test_files
    
    print("Running tests with coverage...")
    print("-" * 80)
    
    try:
        # Run tests
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Parse coverage.json for detailed analysis
        if os.path.exists("coverage.json"):
            with open("coverage.json", "r") as f:
                coverage_data = json.load(f)
            
            print("\n" + "=" * 80)
            print("DETAILED COVERAGE BY MODULE")
            print("=" * 80)
            
            total_covered = 0
            total_statements = 0
            module_results = []
            
            for module_name, module_path in CORE_MODULES.items():
                full_path = os.path.abspath(module_path)
                
                # Find module in coverage data
                module_coverage = None
                for file_path, file_data in coverage_data.get("files", {}).items():
                    if file_path.endswith(module_path.replace("src/", "")):
                        module_coverage = file_data
                        break
                
                if module_coverage:
                    covered = module_coverage["summary"]["covered_lines"]
                    total = module_coverage["summary"]["num_statements"]
                    percent = module_coverage["summary"]["percent_covered"]
                    missing = module_coverage["summary"]["missing_lines"]
                    
                    total_covered += covered
                    total_statements += total
                    
                    status = "✅" if percent >= 90 else "❌"
                    module_results.append({
                        "name": module_name,
                        "percent": percent,
                        "covered": covered,
                        "total": total,
                        "missing": missing,
                        "status": status
                    })
                    
                    print(f"\n{status} {module_name}")
                    print(f"   Coverage: {percent:.1f}% ({covered}/{total} statements)")
                    if missing > 0 and percent < 90:
                        print(f"   Missing: {missing} lines")
                        # Show specific missing lines if available
                        if "missing_lines" in module_coverage:
                            missing_lines = module_coverage["missing_lines"][:10]  # First 10
                            print(f"   Lines: {', '.join(map(str, missing_lines))}")
                            if len(module_coverage["missing_lines"]) > 10:
                                print(f"   ... and {len(module_coverage['missing_lines']) - 10} more")
            
            # Overall summary
            overall_percent = (total_covered / total_statements * 100) if total_statements > 0 else 0
            
            print("\n" + "=" * 80)
            print("OVERALL SUMMARY")
            print("=" * 80)
            print(f"Total Coverage: {overall_percent:.1f}%")
            print(f"Total Statements: {total_statements}")
            print(f"Covered Statements: {total_covered}")
            print(f"Missing Statements: {total_statements - total_covered}")
            
            if overall_percent >= 90:
                print("\n🎉 SUCCESS: Target coverage of 90% achieved!")
            else:
                print(f"\n❌ FAILED: Coverage {overall_percent:.1f}% is below 90% target")
                print("\nModules needing improvement:")
                for module in sorted(module_results, key=lambda x: x["percent"]):
                    if module["percent"] < 90:
                        gap = 90 - module["percent"]
                        needed = int((0.9 * module["total"]) - module["covered"])
                        print(f"  - {module['name']}: {module['percent']:.1f}% (need {needed} more lines)")
        
        # Generate recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        
        if overall_percent < 90:
            print("To achieve 90% coverage:")
            print("1. Focus on untested methods in modules below 90%")
            print("2. Add tests for edge cases and error conditions")
            print("3. Test all public methods and their parameters")
            print("4. Consider integration tests for complex calculations")
            print("5. Use mocking to test external dependencies")
        else:
            print("✅ Excellent coverage achieved!")
            print("Consider:")
            print("1. Adding more edge case tests")
            print("2. Performance benchmarking")
            print("3. Integration tests with real ephemeris data")
            print("4. Fuzz testing for input validation")
        
        print("\n" + "=" * 80)
        print("ARTIFACTS GENERATED")
        print("=" * 80)
        print("1. HTML Report: htmlcov/index.html")
        print("2. JSON Report: coverage.json")
        print("3. Console Output: Above")
        
        # Return success based on coverage
        return overall_percent >= 90
        
    except Exception as e:
        print(f"\n❌ Error running coverage: {e}")
        return False

def generate_coverage_badge():
    """Generate a coverage badge for README."""
    if os.path.exists("coverage.json"):
        with open("coverage.json", "r") as f:
            coverage_data = json.load(f)
        
        percent = coverage_data.get("totals", {}).get("percent_covered", 0)
        
        # Determine color
        if percent >= 90:
            color = "brightgreen"
        elif percent >= 80:
            color = "green"
        elif percent >= 70:
            color = "yellow"
        elif percent >= 60:
            color = "orange"
        else:
            color = "red"
        
        badge_url = f"https://img.shields.io/badge/coverage-{percent:.0f}%25-{color}"
        
        print(f"\nCoverage Badge URL: {badge_url}")
        
        # Save to file
        with open("coverage_badge.txt", "w") as f:
            f.write(badge_url)

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("src/josi"):
        print("❌ Error: Must run from project root directory")
        sys.exit(1)
    
    # Run coverage analysis
    success = run_coverage_analysis()
    
    # Generate badge
    generate_coverage_badge()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)