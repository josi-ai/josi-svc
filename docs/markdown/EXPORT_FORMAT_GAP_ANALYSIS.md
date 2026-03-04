# Export Format Gap Analysis

## Comparison: Original Format vs Current Implementation

### Successfully Implemented ✅

1. **Core Structure**
   - Header with version, name, date/time
   - Ayanamsa and sidereal time
   - Nirayana longitudes with nakshatras
   - Rasi and Navamsa charts
   - Dasa-Bhukti calculations
   - Divisional charts (D2, D3, D9, D10, D12, D30)
   - Shadbala calculations
   - Residential strength
   - Bhava Bala

### Missing or Different ❌

#### 1. **Tamil Calendar Information**
- **Original**: `BAHDANYA KARTHIKA 22 NIGHT`
- **Current**: `[PANCHANG DATA PENDING]`
- **Gap**: Tamil month, paksha, tithi number, day/night indicator

#### 2. **Nakshatra End Times**
- **Original**: `STAR:PUSHYAMI TILL 23:58IST PADA 4`
- **Current**: `STAR:PUSHYAMI [TIME PENDING] PADA 4`
- **Gap**: End time calculation for nakshatras

#### 3. **Panchang Element Timings**
- **Original**: Shows "FROM" times for Tithi, Yoga, Karana
- **Current**: Shows names only
- **Gap**: Transition time calculations

#### 4. **Gulika Display**
- **Original**: `GULI 84:29 PUNARVAS 2 GURU` (with ruler)
- **Current**: `GULI 156:13 UTTRAPHA 1` (missing ruler)
- **Gap**: Nakshatra ruler for Gulika

#### 5. **Dasa Cryptic Lines**
```
ketu dasa------7,8,8,5,10,3,4,11,6
guru bukthi----6,9,8,6,9,8,4,11,6
sani bukthi----7,8,10,7,8,8,4,11,6(1,8,7)
```
- **Gap**: Unknown calculation/reference system

#### 6. **Compressed Dasa Table**
- **Original**: Multi-column format showing multiple bhukti periods per line
- **Current**: Vertical list format
- **Gap**: Compact display format

#### 7. **Bhava Chart Section**
- **Original**: Separate Bhava chart display
- **Original**: Bhava middle and start degrees table with sign/star lords
- **Current**: Missing entirely
- **Gap**: Complete Bhava analysis

#### 8. **Strength Calculations Format**
- **Original**: Decimal format (0.308, 0.731)
- **Current**: Percentage format (30.8%, 73.1%)
- **Gap**: Format preference

#### 9. **Additional Calculations**

##### Ishta/Kashta Bala
```
ISHTA BALA     .14   .65   .34   .74   .35   .19   .26
KASHTA BALA   -.84  -.35  -.63  -.25  -.63  -.76  -.48
NET BALA      -.70   .30  -.28   .49  -.28  -.58  -.22
```

##### Detailed Bhava Bala
- Dikbala, Dhrshti, Adipati components
- Separate calculations for benefic/malefic Mercury

##### Complete Ashtakavarga
- Full 12x7 matrix
- Sarva Ashtakavarga totals
- Pinda calculations (Rasi, Graha, Sodya)

##### Shadbala Variations
- Relative strength values
- Benefic/Malefic Mercury variations

#### 10. **Vargas Format**
- **Original**: Sanskrit sign names in table format
- **Current**: English sign names in list format
- **Gap**: Traditional naming and format

### Priority for Implementation

1. **High Priority**
   - Nakshatra end times
   - Panchang element transition times
   - Bhava chart and calculations
   - Complete Ashtakavarga

2. **Medium Priority**
   - Tamil calendar information
   - Ishta/Kashta Bala
   - Compressed dasa format
   - Vargas Sanskrit names

3. **Low Priority**
   - Cryptic dasa lines
   - Format preferences (decimal vs percentage)
   - Display layout variations

### Technical Requirements

1. **Nakshatra/Panchang Timings**
   - Calculate when Moon will leave current nakshatra
   - Calculate when tithi/yoga/karana will change
   - Convert to local time display

2. **Bhava Calculations**
   - Calculate house cusps using chosen house system
   - Determine bhava madhya (midpoints)
   - Show sign and nakshatra lords

3. **Ashtakavarga**
   - Implement benefic point calculation
   - Create 12x7 matrix for each planet
   - Calculate Sarva Ashtakavarga
   - Implement Pinda calculations

4. **Additional Strength Measures**
   - Ishta/Kashta Bala algorithms
   - Detailed Bhava Bala components
   - Mercury benefic/malefic determination