#!/usr/bin/env python3
"""
Run test coverage analysis for core astrology modules.
"""
import subprocess
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

# Define the core astrology modules we want to test
CORE_MODULES = [
    "josi.services.astrology_service",
    "josi.services.vedic.dasha_service",
    "josi.services.vedic.panchang_service",
    "josi.services.vedic.muhurta_service",
    "josi.services.vedic.ashtakoota_service",
    "josi.services.chinese.bazi_calculator_service",
    "josi.services.western.progressions_service",
    "josi.services.numerology_service"
]

# Test files to run
TEST_FILES = [
    "tests/unit/services/test_astrology_service.py",
    "tests/unit/services/vedic/test_dasha_service.py",
    "tests/unit/services/vedic/test_panchang_service.py",
    "tests/unit/services/vedic/test_muhurta_service.py",
    "tests/unit/services/vedic/test_ashtakoota_service.py",
    "tests/unit/services/chinese/test_bazi_calculator_service.py",
    "tests/unit/services/western/test_progressions_service.py",
    "tests/unit/services/test_numerology_service.py"
]

def main():
    """Run coverage analysis."""
    print("=== Test Coverage Analysis for Core Astrology Modules ===\n")
    
    # Build coverage command
    cov_modules = ",".join(CORE_MODULES)
    existing_tests = [f for f in TEST_FILES if os.path.exists(f)]
    
    if not existing_tests:
        print("❌ No test files found!")
        return
    
    print(f"Running tests for {len(existing_tests)} test files...\n")
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        *existing_tests,
        f"--cov={cov_modules}",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
        # Generate coverage report
        print("\n=== Coverage Summary ===")
        subprocess.run([sys.executable, "-m", "coverage", "report", "--show-missing"])
        
        print("\n✅ HTML coverage report generated in htmlcov/index.html")
        
    except Exception as e:
        print(f"❌ Error running coverage: {e}")
        
        # Try running without conftest
        print("\nTrying direct test execution...")
        for test_file in existing_tests:
            if os.path.exists(test_file):
                print(f"\n📊 Testing {test_file}...")
                subprocess.run([sys.executable, test_file])

if __name__ == "__main__":
    main()