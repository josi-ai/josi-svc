#!/usr/bin/env python3
"""
Verify the correctness of astrology calculations implementation.
This tool checks for common implementation issues and validates calculations.
"""
import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple

class ImplementationChecker:
    """Check implementation correctness of astrology modules."""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.validations = []
    
    def check_file(self, filepath: Path) -> Dict:
        """Check a Python file for implementation issues."""
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            self.issues.append(f"Syntax error in {filepath}: {e}")
            return {"errors": 1}
        
        # Run checks
        self.check_swiss_ephemeris_usage(content, filepath)
        self.check_mathematical_constants(content, filepath)
        self.check_coordinate_systems(content, filepath)
        self.check_time_handling(content, filepath)
        self.check_calculation_methods(tree, filepath)
        self.check_error_handling(tree, filepath)
        self.check_formula_implementation(content, filepath)
        
        return {
            "issues": len(self.issues),
            "warnings": len(self.warnings),
            "validations": len(self.validations)
        }
    
    def check_swiss_ephemeris_usage(self, content: str, filepath: Path):
        """Check Swiss Ephemeris usage patterns."""
        # Check if ephemeris path is set
        if "swisseph" in content or "swe" in content:
            if "set_ephe_path" not in content:
                self.warnings.append(
                    f"{filepath}: Swiss Ephemeris path not set - calculations may fail"
                )
            
            # Check for proper coordinate system
            if "swe.calc_ut" in content or "swisseph.calc_ut" in content:
                if "SEFLG_SWIEPH" not in content and "SEFLG_JPLEPH" not in content:
                    self.warnings.append(
                        f"{filepath}: No ephemeris flag specified - using default"
                    )
    
    def check_mathematical_constants(self, content: str, filepath: Path):
        """Check mathematical constants are correct."""
        # Check for common constants
        constants_to_check = [
            (r"DEGREES_PER_SIGN\s*=\s*(\d+)", 30, "degrees per zodiac sign"),
            (r"MINUTES_PER_DEGREE\s*=\s*(\d+)", 60, "minutes per degree"),
            (r"SECONDS_PER_MINUTE\s*=\s*(\d+)", 60, "seconds per minute"),
            (r"TROPICAL_YEAR\s*=\s*([\d.]+)", 365.24219, "days in tropical year"),
        ]
        
        for pattern, expected, desc in constants_to_check:
            match = re.search(pattern, content)
            if match:
                value = float(match.group(1))
                if abs(value - expected) > 0.001:
                    self.issues.append(
                        f"{filepath}: Incorrect {desc}: {value} (expected {expected})"
                    )
    
    def check_coordinate_systems(self, content: str, filepath: Path):
        """Check coordinate system conversions."""
        # Look for coordinate conversions
        if "longitude" in content and "latitude" in content:
            # Check for proper range validation
            if not re.search(r"longitude.*[<>]=?\s*-?180", content):
                self.warnings.append(
                    f"{filepath}: Missing longitude range validation (-180 to 180)"
                )
            
            if not re.search(r"latitude.*[<>]=?\s*-?90", content):
                self.warnings.append(
                    f"{filepath}: Missing latitude range validation (-90 to 90)"
                )
        
        # Check for ecliptic/equatorial conversions
        if "ecliptic" in content or "equatorial" in content:
            if "obliquity" not in content:
                self.warnings.append(
                    f"{filepath}: Coordinate conversion without obliquity consideration"
                )
    
    def check_time_handling(self, content: str, filepath: Path):
        """Check time and timezone handling."""
        # Check for timezone awareness
        if "datetime" in content:
            if "timezone" not in content and "tzinfo" not in content and "pytz" not in content:
                self.warnings.append(
                    f"{filepath}: Datetime usage without timezone handling"
                )
        
        # Check for Julian Day conversions
        if "julian" in content.lower() or "jd" in content:
            if "utc" not in content.lower():
                self.warnings.append(
                    f"{filepath}: Julian Day calculation should use UTC"
                )
    
    def check_calculation_methods(self, tree: ast.AST, filepath: Path):
        """Check calculation method implementations."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for TODO/FIXME comments
                if node.body and isinstance(node.body[0], ast.Expr):
                    if isinstance(node.body[0].value, ast.Str):
                        docstring = node.body[0].value.s
                        if "TODO" in docstring or "FIXME" in docstring:
                            self.warnings.append(
                                f"{filepath}: {node.name} has TODO/FIXME in docstring"
                            )
                
                # Check for stub implementations
                if len(node.body) == 1:
                    if isinstance(node.body[0], ast.Pass):
                        self.issues.append(
                            f"{filepath}: {node.name} is not implemented (only contains pass)"
                        )
                    elif isinstance(node.body[0], ast.Return):
                        if isinstance(node.body[0].value, ast.Dict) and not node.body[0].value.keys:
                            self.issues.append(
                                f"{filepath}: {node.name} returns empty dict"
                            )
    
    def check_error_handling(self, tree: ast.AST, filepath: Path):
        """Check error handling in calculations."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_try_except = any(isinstance(n, ast.Try) for n in ast.walk(node))
                
                # Critical calculation methods should have error handling
                critical_methods = [
                    "calculate", "compute", "convert", "transform",
                    "get_position", "find_"
                ]
                
                if any(cm in node.name.lower() for cm in critical_methods):
                    if not has_try_except and "raise" not in ast.dump(node):
                        self.warnings.append(
                            f"{filepath}: {node.name} lacks error handling"
                        )
    
    def check_formula_implementation(self, content: str, filepath: Path):
        """Check for correct formula implementations."""
        # Check house calculation formulas
        if "calculate_houses" in content or "house" in content.lower():
            if "placidus" in content.lower():
                # Placidus requires iterative calculation
                if "while" not in content and "for" not in content:
                    self.warnings.append(
                        f"{filepath}: Placidus houses may need iterative calculation"
                    )
        
        # Check aspect calculations
        if "aspect" in content:
            # Should handle 0/360 degree wrap
            if "% 360" not in content and "modulo" not in content:
                self.warnings.append(
                    f"{filepath}: Aspect calculations should handle 360° wraparound"
                )
        
        # Check ayanamsa
        if "ayanamsa" in content or "sidereal" in content:
            if "23." not in content and "24." not in content:
                self.warnings.append(
                    f"{filepath}: Ayanamsa values seem incorrect (should be ~23-24°)"
                )


def check_specific_calculations():
    """Check specific calculation implementations."""
    print("\n" + "=" * 60)
    print("SPECIFIC CALCULATION CHECKS")
    print("=" * 60)
    
    checks = []
    
    # Check 1: Ascendant calculation
    checks.append({
        "name": "Ascendant Calculation",
        "file": "src/josi/services/astrology_service.py",
        "method": "calculate_houses",
        "validations": [
            "Uses ARMC (Right Ascension of MC)",
            "Accounts for latitude",
            "Handles polar regions",
            "Returns values 0-360°"
        ]
    })
    
    # Check 2: Planetary positions
    checks.append({
        "name": "Planetary Positions",
        "file": "src/josi/services/astrology_service.py",
        "method": "calculate_planets",
        "validations": [
            "Converts to Julian Day",
            "Uses appropriate ephemeris",
            "Returns ecliptic longitude",
            "Includes retrograde flag"
        ]
    })
    
    # Check 3: Dasha calculations
    checks.append({
        "name": "Vimshottari Dasha",
        "file": "src/josi/services/vedic/dasha_service.py",
        "method": "calculate_vimshottari_dasha",
        "validations": [
            "Total cycle = 120 years",
            "Correct year allocation per planet",
            "Proper nakshatra calculation",
            "Accurate date calculations"
        ]
    })
    
    # Check 4: Aspect orbs
    checks.append({
        "name": "Aspect Calculations",
        "file": "src/josi/services/astrology_service.py",
        "method": "calculate_aspects",
        "validations": [
            "Handles 0/360° boundary",
            "Correct angle calculation",
            "Proper orb application",
            "All major aspects detected"
        ]
    })
    
    for check in checks:
        print(f"\n{check['name']}:")
        print(f"  File: {check['file']}")
        print(f"  Method: {check['method']}")
        print("  Required validations:")
        for validation in check['validations']:
            print(f"    - {validation}")


def main():
    """Run implementation correctness checks."""
    print("=" * 60)
    print("ASTROLOGY IMPLEMENTATION CORRECTNESS CHECKER")
    print("=" * 60)
    
    checker = ImplementationChecker()
    
    # Files to check
    files_to_check = [
        "src/josi/services/astrology_service.py",
        "src/josi/services/vedic/dasha_service.py",
        "src/josi/services/vedic/panchang_service.py",
        "src/josi/services/vedic/muhurta_service.py",
        "src/josi/services/vedic/ashtakoota_service.py",
        "src/josi/services/chinese/bazi_calculator_service.py",
        "src/josi/services/western/progressions_service.py",
        "src/josi/services/numerology_service.py"
    ]
    
    total_issues = 0
    total_warnings = 0
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            print(f"\nChecking {filepath}...")
            result = checker.check_file(Path(filepath))
            total_issues += result["issues"]
            total_warnings += result["warnings"]
        else:
            print(f"\n❌ File not found: {filepath}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Issues Found: {len(checker.issues)}")
    print(f"Total Warnings: {len(checker.warnings)}")
    
    if checker.issues:
        print("\n🚨 CRITICAL ISSUES:")
        for issue in checker.issues:
            print(f"  - {issue}")
    
    if checker.warnings:
        print("\n⚠️  WARNINGS:")
        for warning in checker.warnings[:10]:  # First 10
            print(f"  - {warning}")
        if len(checker.warnings) > 10:
            print(f"  ... and {len(checker.warnings) - 10} more warnings")
    
    # Specific calculation checks
    check_specific_calculations()
    
    # Recommendations
    print("\n" + "=" * 60)
    print("VERIFICATION RECOMMENDATIONS")
    print("=" * 60)
    print("1. Compare outputs with established software:")
    print("   - Astro.com for Western calculations")
    print("   - JHora for Vedic calculations")
    print("   - Solar Fire for professional validation")
    print("\n2. Test with known data:")
    print("   - Celebrity charts with verified data")
    print("   - Historical astronomical events")
    print("   - Published ephemeris tables")
    print("\n3. Mathematical verification:")
    print("   - Unit test each formula")
    print("   - Check edge cases")
    print("   - Validate against algorithms")
    print("\n4. Cross-validation:")
    print("   - Multiple calculation methods")
    print("   - Different ephemeris sources")
    print("   - Various coordinate systems")


if __name__ == "__main__":
    main()