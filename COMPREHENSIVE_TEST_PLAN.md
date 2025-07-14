# Comprehensive Test Plan for Astrow API

## Overview
This document outlines a systematic approach to test and fix all API endpoints, starting with the most critical issues.

## Priority Order

### Phase 1: Fix Critical Bugs (Immediate)
1. **Vedic Chart Calculation Error**
   - Error: "function takes at most 7 arguments (8 given)"
   - Impact: All Vedic charts failing
   - Priority: CRITICAL

### Phase 2: Core CRUD Operations (High Priority)
2. **Person Management Tests**
   - List, Update, Delete, Restore operations
   - Bulk operations
   - Search and pagination

3. **Chart Management Tests**
   - Get, Update, Delete chart operations
   - Divisional charts
   - Progressions

### Phase 3: Calculation Features (Medium Priority)
4. **Compatibility Analysis**
   - Synastry calculations
   - Composite charts

5. **Transit Analysis**
   - Current transits
   - Personal transits

6. **Dasha Periods**
   - Dasha calculations
   - Current dasha
   - Timeline

### Phase 4: Auxiliary Features (Low Priority)
7. **Predictions**
   - Daily, Monthly, Yearly

8. **Remedies**
   - Gemstones, Mantras, Yantras, Rituals

9. **Panchang**
   - Daily panchang
   - Date-specific panchang

10. **Location Services**
    - Search, Geocoding, Timezones

## Test Implementation Strategy

For each endpoint group, we will:
1. Create test cases with expected behavior
2. Implement the tests
3. Run tests to identify failures
4. Fix any bugs found
5. Verify tests pass
6. Document any issues or edge cases

## Test Structure

Each test file will follow this structure:
```python
"""
Test suite for [Feature Name]
Tests: [List of endpoints tested]
"""

import pytest
from httpx import AsyncClient
from datetime import datetime
import json

class Test[Feature]API:
    """Test cases for [feature] endpoints."""
    
    @pytest.fixture
    async def setup_data(self):
        """Create test data needed for this feature."""
        pass
    
    async def test_[operation]_success(self):
        """Test successful [operation]."""
        # Arrange
        # Act
        # Assert
        pass
    
    async def test_[operation]_validation(self):
        """Test input validation."""
        pass
    
    async def test_[operation]_error_handling(self):
        """Test error scenarios."""
        pass
```

## Success Criteria

Each endpoint must:
1. Return correct HTTP status codes
2. Validate input parameters
3. Handle errors gracefully
4. Return data in expected format
5. Respect authentication/authorization
6. Work with pagination where applicable
7. Handle edge cases

## Let's Start!

We'll begin with Phase 1: Fixing the Vedic Chart Calculation Error