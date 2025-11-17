#!/usr/bin/env python3
"""
Complete example: Scale-based real-world area calculation
Demonstrates the full workflow from detection to actual square footage.
"""

from service.detect import (
    parse_dimension_text_to_inches,
    parse_scale_text,
    compute_actual_sqft_from_drawing
)

print("=" * 80)
print("SCALE-BASED AREA MEASUREMENT - COMPLETE EXAMPLE")
print("=" * 80)
print()

# Scenario: Analyzing a floor plan
print("SCENARIO: Commercial Floor Plan Analysis")
print("-" * 80)
print("Floor plan contains:")
print("  - Dimension annotation: '10'-0\"' (10 feet)")
print("  - Scale: '1/4\" = 1'-0\"'")
print("  - Three rooms detected with pixel areas")
print()

# Step 1: Parse dimension
print("STEP 1: Parse Dimension")
print("-" * 80)
dim_text = "10'-0\""
real_inches = parse_dimension_text_to_inches(dim_text)
print(f"Dimension text: {dim_text}")
print(f"Parsed: {real_inches} inches = {real_inches/12:.1f} feet")
print()

# Step 2: Calibrate (simulated - in API this measures the dimension line)
print("STEP 2: Calibrate Pixels to Inches")
print("-" * 80)
px_length = 2000.0  # Simulated: dimension line measures 2000 pixels
px_per_inch = px_length / real_inches
print(f"Dimension line pixel length: {px_length} px")
print(f"Calibration: {px_per_inch:.2f} pixels per inch")
print()

# Step 3: Parse scale
print("STEP 3: Parse Scale")
print("-" * 80)
scale_text = '1/4" = 1\'-0"'
scale_info = parse_scale_text(scale_text)
scale_ratio = scale_info['ratio']
print(f"Scale text: {scale_text}")
print(f"Parsed:")
print(f"  - Type: {scale_info['type']}")
print(f"  - Ratio: {scale_ratio}")
print(f"  - Meaning: {scale_info['drawing_inches']}\" on drawing = {scale_info['real_inches']}\" in reality")
print(f"  - Or: 1\" on drawing = {scale_ratio}\" ({scale_ratio/12:.1f} feet) in reality")
print()

# Step 4: Convert room areas
print("STEP 4: Convert Room Areas to Actual Square Feet")
print("-" * 80)
rooms = [
    ("Conference Room", 50000),
    ("Office A", 25000),
    ("Lobby", 80000),
]

print(f"{'Room':<20} {'Pixels²':>12} {'Drawing (sq in)':>18} {'Actual (sq ft)':>18}")
print("-" * 80)

total_actual_sqft = 0
for room_name, area_px in rooms:
    # Convert to drawing square inches
    drawing_sq_in = area_px / (px_per_inch ** 2)
    
    # Apply scale and convert to actual square feet
    actual_sq_ft = compute_actual_sqft_from_drawing(area_px, px_per_inch, scale_ratio)
    total_actual_sqft += actual_sq_ft
    
    print(f"{room_name:<20} {area_px:>12,} {drawing_sq_in:>18.2f} {actual_sq_ft:>18.2f}")

print("-" * 80)
print(f"{'TOTAL':<20} {'':<12} {'':<18} {total_actual_sqft:>18.2f}")
print()

# Explanation
print("CALCULATION BREAKDOWN (Conference Room):")
print("-" * 80)
area_px = 50000
drawing_sq_in = area_px / (px_per_inch ** 2)
scaled_sq_in = drawing_sq_in * (scale_ratio ** 2)
actual_sq_ft = scaled_sq_in / 144

print(f"1. Pixel area: {area_px:,} px²")
print(f"2. Drawing area: {area_px:,} ÷ ({px_per_inch:.2f})² = {drawing_sq_in:.2f} sq in")
print(f"3. Apply scale: {drawing_sq_in:.2f} × ({scale_ratio})² = {scaled_sq_in:,.2f} sq in")
print(f"4. Convert to sq ft: {scaled_sq_in:,.2f} ÷ 144 = {actual_sq_ft:.2f} sq ft")
print()

print("=" * 80)
print("✓ Analysis Complete!")
print(f"Total floor area: {total_actual_sqft:,.2f} square feet")
print("=" * 80)
