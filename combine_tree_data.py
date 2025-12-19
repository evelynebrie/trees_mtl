#!/usr/bin/env python3
"""
Script to combine multiple tree CSV files and convert to JSON for Mapbox visualization.
"""

import csv
import json
import glob
import os
import sys
from datetime import datetime

def parse_date(date_string):
    """Parse date string and extract year, handling various formats"""
    if not date_string or date_string.strip() == '':
        return None
    try:
        date_obj = datetime.fromisoformat(date_string.replace('T00:00:00', ''))
        year = date_obj.year
        # Only return valid years (1850-2025)
        if year < 1850 or year > 2025:
            return None
        return year
    except:
        return None

def combine_csv_files(pattern='arbres-part-*.csv', output_file='trees_combined.json'):
    """
    Combine all CSV files matching the pattern and create a GeoJSON file
    """
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    print(f"Looking for files matching: {pattern}")
    
    # Find all matching CSV files
    csv_files = sorted(glob.glob(pattern))
    
    if not csv_files:
        print(f"ERROR: No CSV files found matching pattern: {pattern}")
        print(f"Files in current directory:")
        for f in os.listdir('.'):
            print(f"  - {f}")
        sys.exit(1)
    
    print(f"Found {len(csv_files)} CSV files:")
    for f in csv_files:
        file_size = os.path.getsize(f) / (1024 * 1024)
        print(f"  - {f} ({file_size:.2f} MB)")
    
    # GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    tree_types = set()
    year_range = {'min': float('inf'), 'max': float('-inf')}
    total_trees = 0
    trees_with_dates = 0
    trees_skipped = 0
    
    # Process each CSV file
    for csv_file in csv_files:
        print(f"\nProcessing {csv_file}...")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                rows_processed = 0
                for row in reader:
                    total_trees += 1
                    rows_processed += 1
                    
                    # Extract coordinates
                    try:
                        longitude = float(row.get('Longitude', 0))
                        latitude = float(row.get('Latitude', 0))
                        
                        # Skip if coordinates are invalid
                        if longitude == 0 or latitude == 0:
                            trees_skipped += 1
                            continue
                        
                    except (ValueError, TypeError):
                        trees_skipped += 1
                        continue
                    
                    # Extract plantation year
                    plantation_date = row.get('Date_Plantation', '')
                    plantation_year = parse_date(plantation_date)
                    
                    if plantation_year:
                        trees_with_dates += 1
                        year_range['min'] = min(year_range['min'], plantation_year)
                        year_range['max'] = max(year_range['max'], plantation_year)
                    
                    # Extract tree type
                    tree_type_latin = row.get('Essence_latin', 'Unknown') or 'Unknown'
                    tree_type_french = row.get('Essence_fr', 'Inconnu') or 'Inconnu'
                    tree_type_english = row.get('Essence_en', 'Unknown') or 'Unknown'
                    tree_types.add(tree_type_english)
                    
                    # Create GeoJSON feature - use 0 instead of null for missing years
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [longitude, latitude]
                        },
                        "properties": {
                            "arrondissement": row.get('Arrond', '') or '',
                            "rue": (row.get('Rue', '') or '').strip(),
                            "emplacement": (row.get('Emplacement', '') or '').strip(),
                            "tree_type_latin": tree_type_latin,
                            "tree_type_french": tree_type_french,
                            "tree_type_english": tree_type_english,
                            "diameter": row.get('DHP', '') or '',
                            "plantation_year": plantation_year if plantation_year else 0,
                        }
                    }
                    
                    geojson["features"].append(feature)
                
                print(f"  ✓ Processed {rows_processed:,} rows")
                
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            continue
    
    # Add metadata
    geojson["metadata"] = {
        "total_trees": len(geojson["features"]),
        "trees_processed": total_trees,
        "trees_with_dates": trees_with_dates,
        "trees_skipped": trees_skipped,
        "year_range": {
            "min": year_range['min'] if year_range['min'] != float('inf') else None,
            "max": year_range['max'] if year_range['max'] != float('-inf') else None
        },
        "tree_types": sorted(list(tree_types)),
        "generated_at": datetime.now().isoformat()
    }
    
    # Write to JSON file (compact format to save space)
    print(f"\nWriting to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, separators=(',', ':'))
    
    file_size = os.path.getsize(output_file) / (1024 * 1024)
    
    print(f"\n{'='*50}")
    print(f"✓ SUCCESS! Created {output_file}")
    print(f"{'='*50}")
    print(f"  File size: {file_size:.2f} MB")
    print(f"  Total trees: {len(geojson['features']):,}")
    print(f"  Trees with dates: {trees_with_dates:,}")
    print(f"  Trees skipped: {trees_skipped:,}")
    print(f"  Year range: {year_range['min']} - {year_range['max']}")
    print(f"  Tree types: {len(tree_types)}")

if __name__ == '__main__':
    print("=" * 50)
    print("Montreal Tree Data Combiner")
    print("=" * 50)
    try:
        combine_csv_files()
        print(f"\n✓ Done! File ready for visualization.")
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
