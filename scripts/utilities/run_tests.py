#!/usr/bin/env python3
"""
Test runner script for comprehensive test execution.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def main():
    """Run comprehensive test suite."""
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Ensure dependencies are installed
    if not run_command("poetry install", "Installing dependencies"):
        print("Failed to install dependencies")
        return 1
    
    # Run different test categories
    test_commands = [
        # Unit tests
        ("poetry run pytest tests/unit -v", "Unit Tests"),
        
        # Integration tests
        ("poetry run pytest tests/integration -v", "Integration Tests"),
        
        # Security tests
        ("poetry run pytest tests/security -v", "Security Tests"),
        
        # Test with coverage
        ("poetry run pytest --cov=josi --cov-report=html --cov-report=term-missing", "Full Test Suite with Coverage"),
        
        # Type checking
        ("poetry run mypy src/josi --ignore-missing-imports", "Type Checking"),
        
        # Linting
        ("poetry run flake8 src/josi --max-line-length=120", "Code Linting"),
        
        # Format checking
        ("poetry run black src/josi --check", "Code Format Check"),
    ]
    
    failed_tests = []
    
    for cmd, description in test_commands:
        if not run_command(cmd, description):
            failed_tests.append(description)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    if failed_tests:
        print(f"\n❌ Failed tests: {len(failed_tests)}")
        for test in failed_tests:
            print(f"  - {test}")
        return 1
    else:
        print("\n✅ All tests passed!")
        print("\n📊 Coverage report generated in htmlcov/index.html")
        return 0


if __name__ == "__main__":
    sys.exit(main())