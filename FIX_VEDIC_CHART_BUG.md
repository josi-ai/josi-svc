# Vedic Chart Bug Investigation Results

## Summary
The error "function takes at most 7 arguments (8 given)" occurs ONLY when creating Vedic charts through the API, but NOT when:
1. Calculating Vedic charts directly with AstrologyCalculator
2. Inserting Vedic chart data directly into the database

## Evidence

### What Works ✅
1. **Direct calculation**: `calc.calculate_vedic_chart()` works perfectly
2. **Direct DB insert**: Both Western and Vedic charts can be inserted directly
3. **Western charts via API**: Work without issues

### What Fails ❌
1. **Vedic charts via API**: Fail with "function takes at most 7 arguments (8 given)"
2. **All Vedic charts**: Regardless of parameters (ayanamsa, house_system)

## Key Finding
The error occurs somewhere between the chart calculation and database insertion, specifically in the API/service layer.

## Hypothesis
The error might be related to:
1. **JSON serialization** of Vedic-specific fields (nakshatra, pada)
2. **Model instantiation** with Vedic-specific data
3. **Repository method** handling Vedic charts differently

## Next Steps
1. Add logging to chart_service.py to trace exactly where the error occurs
2. Check if the error happens during:
   - Chart record creation
   - Planet position records creation
   - JSON field serialization

## Potential Quick Fix
Since the error seems to be in the Python layer, not the database, we might need to:
1. Check how Vedic planet data is being passed to PlanetPosition model
2. Ensure all fields are properly mapped
3. Handle any Vedic-specific fields that might be causing issues