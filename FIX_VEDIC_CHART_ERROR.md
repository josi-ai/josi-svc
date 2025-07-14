# Fix for Vedic Chart Error

## Problem Analysis

There are actually TWO separate errors affecting chart calculations:

### 1. JSON Serialization Error (Western charts for some celebrities)
- **Error**: "Object of type Decimal is not JSON serializable"
- **Cause**: Some calculations return Python Decimal objects which can't be serialized to JSON
- **Affected**: Madonna's Western chart (and possibly others)

### 2. PostgreSQL Function Error (All Vedic charts)
- **Error**: "function takes at most 7 arguments (8 given)"
- **Cause**: Unknown - possibly a database trigger or constraint
- **Affected**: ALL Vedic chart calculations

## Investigation Steps

### Step 1: Check the SQL being generated
Looking at Madonna's error, the SQL INSERT has these columns:
1. person_id
2. chart_type
3. house_system
4. ayanamsa
5. calculated_at
6. calculation_version
7. chart_data (JSON)
8. planet_positions (JSON)
9. house_cusps (JSON)
10. aspects (JSON)
11. divisional_chart_type
12. progression_type
13. is_deleted
14. deleted_at
15. organization_id

That's 15 columns, not 7 or 8.

### Step 2: The "function" error for Vedic charts
This suggests a PostgreSQL function/trigger is being called with wrong arguments.

## Solution Plan

### Fix 1: JSON Serialization
Add a custom JSON encoder to handle Decimal types:

```python
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
```

### Fix 2: Investigate Vedic-specific issue
The error only happens for Vedic charts, suggesting:
1. The `ayanamsa` field might be causing issues
2. There might be a database constraint or trigger
3. The chart_data structure might be different

## Next Steps

1. Add JSON encoder to handle Decimals
2. Check if Vedic charts have different data structure
3. Look for database triggers or functions
4. Test with minimal Vedic chart data