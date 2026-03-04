# Josi API Traditional Chart Export Implementation Plan

## Overview
This plan outlines the implementation of a standardized traditional Vedic astrology chart export format for the Josi API, based on the professional format analyzed from chart-export-format-*.txt files.

## Goals
1. Extract data from Josi API and map to traditional format
2. Create HTML output that replicates the exact traditional format
3. Use placeholders for any missing data
4. Standardize this as the official Josi export format
5. Update project documentation and instructions

## Implementation Steps

### Phase 1: Data Mapping and Gap Analysis
1. **Map Josi API Response to Traditional Format**
   - Available data:
     - ✓ Birth information (date, time, location)
     - ✓ Planetary positions (longitude, sign, nakshatra, pada)
     - ✓ Ascendant details
     - ✓ Ayanamsa value
     - ✓ House positions (12 houses)
     - ✓ Retrograde status
   
   - Missing data (will use placeholders):
     - ⚠️ Sidereal time
     - ⚠️ Sunrise/Sunset times
     - ⚠️ Tithi, Yoga, Karana details
     - ⚠️ Gulika position
     - ⚠️ Dasa-Bhukti calculations
     - ⚠️ Divisional charts (Vargas)
     - ⚠️ Ashtakavarga calculations
     - ⚠️ Shadbala strengths
     - ⚠️ Bhava strengths
     - ⚠️ Pinda values

### Phase 2: HTML Template Creation
1. **Create CSS-styled HTML template**
   - Monospace font for authentic look
   - Preserve exact spacing and alignment
   - ASCII art charts using HTML entities
   - Print-friendly styling

2. **Template sections**:
   - Header with version
   - Birth information block
   - Astronomical data
   - Panchang information
   - Nirayana longitudes table
   - Retrograde planets
   - RASI and NAVAMSA charts
   - Dasa information
   - Extended calculations

### Phase 3: Implementation Script
1. **Create `generate_josi_traditional_export.py`**
   - Fetch data from Josi API
   - Transform to traditional format
   - Apply formatting rules
   - Generate HTML output

2. **Key transformations**:
   - Convert decimal degrees to DEG:MIN format
   - Map planet names to abbreviations
   - Format nakshatra names
   - Create ASCII chart placements
   - Calculate house positions

### Phase 4: Placeholder Strategy
1. **Smart placeholders for missing data**:
   - Sidereal Time: Calculate approximation or use "XX:XX:XX"
   - Sunrise/Sunset: Use standard approximations based on location
   - Dasa calculations: Show "CALCULATION PENDING"
   - Strengths: Use "---" or "0.000"
   - Mark clearly as placeholders for future implementation

### Phase 5: Standardization
1. **API Integration**
   - Add new endpoint: `/api/v1/charts/{chart_id}/export/traditional`
   - Return HTML or plain text format
   - Include in chart creation response

2. **Documentation Updates**
   - Update CLAUDE.md with export format specification
   - Add to API documentation
   - Create usage examples

### Phase 6: Testing and Validation
1. **Generate exports for all 5 test persons**
2. **Compare with original format**
3. **Validate HTML rendering**
4. **Test browser compatibility**

## Technical Implementation Details

### Data Structure Mapping
```python
# Josi API Response → Traditional Format
{
    "planets": {
        "Sun": {...} → "SURY DEG:MIN NAKSHATRA PADA RULER"
    },
    "ascendant": {...} → "LAGN DEG:MIN NAKSHATRA PADA RULER",
    "houses": [...] → Bhava table and chart placement
}
```

### Placeholder Examples
```
# For missing Dasa calculations:
"DASA CALCULATIONS UNDER DEVELOPMENT"

# For missing strengths:
"SHADBALA: --- --- --- --- --- --- ---"

# For missing divisional charts:
"VARGAS: CALCULATION PENDING"
```

### HTML Structure
```html
<!DOCTYPE html>
<html>
<head>
    <title>Josi Traditional Chart Export - {NAME}</title>
    <style>
        body { font-family: 'Courier New', monospace; }
        .chart-container { white-space: pre; }
        /* Additional styling for authentic look */
    </style>
</head>
<body>
    <div class="chart-container">
        <!-- Traditional format content -->
    </div>
</body>
</html>
```

## Success Criteria
1. ✓ HTML output visually matches traditional format
2. ✓ All available Josi data correctly mapped
3. ✓ Placeholders clearly marked for missing data
4. ✓ Export available for all charts via API
5. ✓ Documentation updated with new standard
6. ✓ Browser-viewable HTML files generated

## Future Enhancements
1. Implement missing calculations (Dasa, Ashtakavarga, etc.)
2. Add PDF export option
3. Support multiple ayanamsa systems
4. Include Tamil/regional language options
5. Add print optimization

## Timeline
- Phase 1-3: Immediate implementation
- Phase 4-5: Documentation and standardization
- Phase 6: Testing and deployment
- Future: Incremental addition of missing calculations

This plan ensures we can immediately provide traditional format exports while clearly marking areas for future enhancement.