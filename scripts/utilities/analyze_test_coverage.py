#!/usr/bin/env python3
"""
Analyze test coverage for core astrology calculation modules.
"""
import os
import sys
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple

sys.path.append('src')

class CoverageAnalyzer(ast.NodeVisitor):
    """Analyze Python files to find functions and methods."""
    
    def __init__(self):
        self.functions = []
        self.classes = {}
        self.current_class = None
    
    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.classes[node.name] = []
        self.generic_visit(node)
        self.current_class = None
    
    def visit_FunctionDef(self, node):
        if self.current_class:
            self.classes[self.current_class].append(node.name)
        else:
            self.functions.append(node.name)
        self.generic_visit(node)

def analyze_module(filepath: Path) -> Dict:
    """Analyze a Python module to find all functions and methods."""
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    analyzer = CoverageAnalyzer()
    analyzer.visit(tree)
    
    return {
        'functions': analyzer.functions,
        'classes': analyzer.classes
    }

def find_test_coverage(module_path: Path, test_path: Path) -> Dict:
    """Find what functions/methods are tested."""
    tested_items = set()
    
    if test_path.exists():
        with open(test_path, 'r') as f:
            content = f.read()
            # Simple heuristic: look for test method names
            for line in content.split('\n'):
                if 'def test_' in line:
                    # Extract what's being tested from the test name
                    test_name = line.strip().split('(')[0].replace('def test_', '')
                    tested_items.add(test_name)
    
    return tested_items

def calculate_coverage_stats(module_info: Dict, tested_items: Set) -> Dict:
    """Calculate coverage statistics."""
    total_items = len(module_info['functions'])
    for class_methods in module_info['classes'].values():
        total_items += len(class_methods)
    
    # Count how many items have tests (simplified)
    tested_count = min(len(tested_items), total_items)  # Can't have more than total
    
    coverage_percent = (tested_count / total_items * 100) if total_items > 0 else 0
    
    return {
        'total_items': total_items,
        'tested_count': tested_count,
        'coverage_percent': coverage_percent,
        'untested_functions': [],  # Would need more sophisticated analysis
        'untested_methods': {}
    }

def main():
    """Analyze test coverage for core astrology modules."""
    print("=== Astrology Module Test Coverage Analysis ===\n")
    
    # Core astrology calculation modules to analyze
    modules_to_analyze = [
        ('astrology_service.py', 'services/astrology_service.py'),
        ('vedic/dasha_service.py', 'services/vedic/dasha_service.py'),
        ('vedic/panchang_service.py', 'services/vedic/panchang_service.py'),
        ('vedic/muhurta_service.py', 'services/vedic/muhurta_service.py'),
        ('vedic/ashtakoota_service.py', 'services/vedic/ashtakoota_service.py'),
        ('chinese/bazi_calculator_service.py', 'services/chinese/bazi_calculator_service.py'),
        ('western/progressions_service.py', 'services/western/progressions_service.py'),
        ('numerology_service.py', 'services/numerology_service.py'),
    ]
    
    total_coverage = []
    
    for module_name, module_path in modules_to_analyze:
        full_module_path = Path(f'src/josi/{module_path}')
        test_path = Path(f'tests/unit/{module_path.replace(".py", "")}.py')
        
        if not full_module_path.exists():
            print(f"❌ Module not found: {module_name}")
            continue
        
        print(f"\n📊 Analyzing: {module_name}")
        print("-" * 50)
        
        try:
            # Analyze module
            module_info = analyze_module(full_module_path)
            
            # Find test coverage
            tested_items = find_test_coverage(full_module_path, test_path)
            
            # Calculate stats
            stats = calculate_coverage_stats(module_info, tested_items)
            
            print(f"Functions: {len(module_info['functions'])}")
            print(f"Classes: {len(module_info['classes'])}")
            
            total_methods = 0
            for class_name, methods in module_info['classes'].items():
                print(f"  - {class_name}: {len(methods)} methods")
                total_methods += len(methods)
            
            print(f"\nTotal items to test: {stats['total_items']}")
            print(f"Test file exists: {'✅' if test_path.exists() else '❌'}")
            
            if test_path.exists():
                print(f"Estimated coverage: ~{stats['coverage_percent']:.1f}%")
                total_coverage.append(stats['coverage_percent'])
            else:
                print("Coverage: 0% (no test file)")
                total_coverage.append(0)
            
        except Exception as e:
            print(f"Error analyzing {module_name}: {e}")
    
    if total_coverage:
        avg_coverage = sum(total_coverage) / len(total_coverage)
        print(f"\n\n📈 Overall Average Coverage: ~{avg_coverage:.1f}%")
        print(f"🎯 Target Coverage: 90%")
        print(f"📊 Gap: {90 - avg_coverage:.1f}%")

    # List critical untested areas
    print("\n\n🔍 Critical Areas Needing Tests:")
    print("-" * 50)
    
    critical_functions = [
        "calculate_vedic_chart",
        "calculate_western_chart", 
        "calculate_divisional_chart",
        "calculate_dasha_periods",
        "calculate_panchang",
        "find_muhurta",
        "calculate_compatibility",
        "calculate_bazi_chart",
        "calculate_progressions",
        "calculate_transits",
        "calculate_solar_return",
        "calculate_lunar_return"
    ]
    
    print("\nCore calculation functions that need comprehensive testing:")
    for func in critical_functions:
        print(f"  - {func}")
    
    print("\n\n📝 Recommendations to Reach 90% Coverage:")
    print("-" * 50)
    print("1. Add comprehensive tests for all planetary calculation methods")
    print("2. Test edge cases (polar regions, historical dates, etc.)")
    print("3. Add tests for all house systems (Placidus, Koch, Equal, etc.)")
    print("4. Test aspect calculations with various orb settings")
    print("5. Add tests for retrograde motion detection")
    print("6. Test timezone and DST handling")
    print("7. Add performance benchmarks for large date ranges")
    print("8. Test error handling for invalid inputs")

if __name__ == "__main__":
    main()