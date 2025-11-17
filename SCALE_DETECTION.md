# Scale Detection and Real-World Area Calculation

## Overview
The API now automatically detects scale annotations on floor plans and calculates **actual real-world square footage** by applying the scale ratio to the measured areas.

## How It Works

### Complete Workflow

1. **Dimension Detection** → Extract dimension line (e.g., "6'- 3 3/4\"")
2. **Pixel Calibration** → Calculate `px_per_inch` from dimension line
3. **Scale Detection** → Find and parse scale text (e.g., "1/4\" = 1'-0\"")
4. **Area Conversion** → Convert pixel areas to real-world square feet

### Formula

```
Drawing Area (sq in) = Pixel Area / (px_per_inch)²
Real-World Area (sq in) = Drawing Area × (scale_ratio)²
Real-World Area (sq ft) = Real-World Area (sq in) / 144
```

## Supported Scale Formats

### Architectural Scales
- `1/4" = 1'-0"` → ratio = 48 (1 drawing inch = 48 real inches)
- `1/8" = 1'-0"` → ratio = 96 (1 drawing inch = 96 real inches)
- `1/2" = 1'-0"` → ratio = 24
- `3/8" = 1'-0"` → ratio = 32
- `1/4 = 1-0` (no quotes)

### Numeric Scales
- `Scale: 1:100` → ratio = 100
- `1:50` → ratio = 50
- `Scale: 1:200` → ratio = 200

### No Scale
- `Scale: NOT TO SCALE` → ratio = None
- `NTS` → ratio = None
- `N.T.S` → ratio = None

## API Response

### With Scale Detected

```json
{
  "shapes": [
    {
      "path": "M100,200L150,200L150,280L100,280Z",
      "area": 10000.0,
      "area_sq_in": 100.0,
      "actual_sq_ft": 1600.0,
      "color": "#3F5EFB"
    }
  ],
  "dimension_calibration": {
    "text": "6'- 3 3/4\"",
    "px_length": 1212.5,
    "real_inches": 75.75,
    "px_per_inch": 16.0
  },
  "scale_info": {
    "ratio": 48.0,
    "type": "architectural",
    "text": "1/4\" = 1'-0\"",
    "drawing_inches": 0.25,
    "real_inches": 12.0
  }
}
```

### Field Descriptions

- `area`: Original pixel area
- `area_sq_in`: Drawing area in square inches (before scale)
- `actual_sq_ft`: **Real-world area in square feet** (after applying scale)
- `scale_info.ratio`: Scale ratio (real_inches / drawing_inches)
- `scale_info.type`: 
  - `"architectural"` - e.g., 1/4" = 1'-0"
  - `"numeric"` - e.g., 1:100
  - `"none"` - NOT TO SCALE

## Example Calculation

### Scenario
- Floor plan image with:
  - Dimension line: "6'-0\"" (72 inches)
  - Scale: "1/4\" = 1'-0\""
  - Room contour: 10,000 pixels²

### Step-by-Step

1. **Measure dimension line in pixels**
   - OCR extracts: "6'-0\""
   - Parse to inches: 72 inches
   - Measure pixel length: 1200 pixels
   - Calculate: `px_per_inch = 1200 / 72 = 16.67 px/inch`

2. **Parse scale**
   - OCR extracts: "1/4\" = 1'-0\""
   - Parse: drawing = 0.25", real = 12"
   - Calculate: `scale_ratio = 12 / 0.25 = 48`

3. **Convert room area**
   - Pixel area: 10,000 px²
   - Drawing area: `10,000 / (16.67)² = 36 sq in`
   - Apply scale: `36 × (48)² = 82,944 sq in`
   - Convert to sq ft: `82,944 / 144 = 576 sq ft`

### Result
- **Drawing measurement**: 36 sq in
- **Actual real-world area**: 576 sq ft

## Common Architectural Scales

| Scale | Ratio | Meaning |
|-------|-------|---------|
| 1/4" = 1'-0" | 48 | 1 drawing inch = 4 feet |
| 1/8" = 1'-0" | 96 | 1 drawing inch = 8 feet |
| 1/2" = 1'-0" | 24 | 1 drawing inch = 2 feet |
| 3/8" = 1'-0" | 32 | 1 drawing inch = 2.67 feet |
| 3/16" = 1'-0" | 64 | 1 drawing inch = 5.33 feet |
| 1" = 1'-0" | 12 | 1 drawing inch = 1 foot |

## Area Scaling

When scale ratio is applied, **area scales by the square of the linear scale**:

- If `1 drawing inch = 48 real inches` (linear)
- Then `1 sq in (drawing) = 48² = 2,304 sq in (real)`

Example:
- 100 sq in on drawing
- Scale 1/4" = 1'-0" (ratio = 48)
- Real area = 100 × 48² = 230,400 sq in = 1,600 sq ft

## New Functions

### `parse_scale_text(scale_text: str) -> dict`
Parse scale annotations and return scale information.

**Returns:**
```python
{
    "ratio": 48.0,
    "type": "architectural",  # or "numeric" or "none"
    "text": "1/4\" = 1'-0\"",
    "drawing_inches": 0.25,
    "real_inches": 12.0
}
```

### `apply_scale_to_area(area_sq_in: float, scale_ratio: float) -> float`
Apply scale ratio to convert drawing area to real-world area.

### `compute_actual_sqft_from_drawing(area_px, px_per_inch, scale_ratio) -> float`
Complete conversion from pixels to actual square feet using calibration and scale.

## Integration

The API automatically:
1. Scans all detections for scale text
2. Tries OCR on each detection
3. Attempts to parse scale using `parse_scale_text()`
4. If valid scale found, adds `actual_sq_ft` to all shapes

## Error Handling

- If no scale detected → shapes only have `area` and `area_sq_in`
- If scale is "NOT TO SCALE" → no `actual_sq_ft` added
- If scale parsing fails → continues without scale conversion
- If no dimension detected → no calibration, areas remain in pixels

## Testing

```python
from service.detect import parse_scale_text, compute_actual_sqft_from_drawing

# Parse scale
scale_info = parse_scale_text('1/4" = 1\'-0"')
# Returns: {'ratio': 48.0, 'type': 'architectural', ...}

# Calculate actual area
area_px = 10000
px_per_inch = 10.0
scale_ratio = 48.0

actual_sq_ft = compute_actual_sqft_from_drawing(area_px, px_per_inch, scale_ratio)
# Returns: 1600.0 sq ft
```

## Notes

- **Architectural scales** are most common in floor plans
- **Numeric scales** (1:100) are common in international/metric drawings
- Scale detection uses OCR, so text quality affects accuracy
- If multiple scales detected, first valid scale is used
- Scale ratio represents: `real_world_units / drawing_units`
