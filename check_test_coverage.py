#!/usr/bin/env python3
"""
Direct test coverage checker for core astrology modules.
"""
import os
import sys
import importlib.util
import inspect
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

def count_module_coverage(module_path):
    """Count functions/methods in a module."""
    spec = importlib.util.spec_from_file_location("module", module_path)
    if not spec or not spec.loader:
        return None
    
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error loading {module_path}: {e}")
        return None
    
    stats = {
        "functions": 0,
        "methods": 0,
        "classes": 0,
        "private_methods": 0,
        "total": 0
    }
    
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and obj.__module__ == module.__name__:
            if name.startswith('_'):
                stats["private_methods"] += 1
            else:
                stats["functions"] += 1
        elif inspect.isclass(obj) and obj.__module__ == module.__name__:
            stats["classes"] += 1
            for method_name, method in inspect.getmembers(obj):
                if inspect.ismethod(method) or inspect.isfunction(method):
                    if not method_name.startswith('__'):
                        if method_name.startswith('_'):
                            stats["private_methods"] += 1
                        else:
                            stats["methods"] += 1
    
    stats["total"] = stats["functions"] + stats["methods"] + stats["private_methods"]
    return stats

def main():
    """Analyze test coverage needs."""
    print("=" * 80)
    print("ASTROLOGY MODULE ANALYSIS")
    print("=" * 80)
    print()
    
    modules = {
        "astrology_service": "src/josi/services/astrology_service.py",
        "dasha_service": "src/josi/services/vedic/dasha_service.py",
        "panchang_service": "src/josi/services/vedic/panchang_service.py",
        "muhurta_service": "src/josi/services/vedic/muhurta_service.py",
        "ashtakoota_service": "src/josi/services/vedic/ashtakoota_service.py",
        "bazi_calculator": "src/josi/services/chinese/bazi_calculator_service.py",
        "progressions_service": "src/josi/services/western/progressions_service.py",
        "numerology_service": "src/josi/services/numerology_service.py"
    }
    
    total_items = 0
    
    for name, path in modules.items():
        if os.path.exists(path):
            stats = count_module_coverage(path)
            if stats:
                print(f"\n{name}:")
                print(f"  Classes: {stats['classes']}")
                print(f"  Public methods: {stats['methods']}")
                print(f"  Functions: {stats['functions']}")
                print(f"  Private methods: {stats['private_methods']}")
                print(f"  Total items: {stats['total']}")
                total_items += stats['total']
        else:
            print(f"\n{name}: FILE NOT FOUND")
    
    print(f"\n\nTotal items to test: {total_items}")
    print(f"Target coverage (90%): {int(total_items * 0.9)} items")
    
    # List test files
    print("\n\nTest files created:")
    test_files = [
        "tests/unit/services/test_astrology_service_comprehensive.py",
        "tests/unit/services/vedic/test_comprehensive_vedic.py", 
        "tests/unit/services/test_chinese_western_comprehensive.py",
        "tests/unit/services/test_astronomical_edge_cases.py",
        "tests/unit/services/test_performance_benchmarks.py"
    ]
    
    for test_file in test_files:
        exists = "✅" if os.path.exists(test_file) else "❌"
        print(f"  {exists} {test_file}")

if __name__ == "__main__":
    main()