#!/usr/bin/env python3
"""
Montreal Tree Data Combiner - Combines 7 CSV files into one GeoJSON
"""

import csv
import json
import glob
import os
import sys
from datetime import datetime

def parse_date(date_string):
    """Parse date and return year between 1850-2025, or None"""
    if not date_string or date_string.strip() == '':
        return None
    try:
        date_obj = datetime.fromisoformat(date_string.replace('T00:00:00', ''))
        year = date_obj.year
        return year if 1850 <= year <= 2025 else None
    except:
        return None

def combine_csv_files(pattern='arbres-part-*.csv', output_file='trees_combined.json'):
    """Combine all CSV files and create GeoJSON"""
    
    print(f"\nCurrent directory: {os.getcwd()}")
    print(f"Looking for: {pattern}\n")
    
    csv_files = sorted(glob.glob(pattern))
    
    if not csv_files:
        print(f"❌ ERROR: No CSV files found!")
        print(f"Files in directory:")
        for f in os.listdir('.')[:20]:
            print(f"  - {f}")
        sys.exit(1)
    
    print(f"✓ Found {len(csv_files)} CSV files\n")
    
    geojson = {"type": "FeatureCollection", "features": []}
    tree_types = set()
    year_range = {'min': float('inf'), 'max': float('-inf')}
    
    total_rows = 0
    total_valid = 0
    total_skipped = 0
    trees_with_dates = 0
    
    # Process each file
    for i, csv_file in enumerate(csv_files, 1):
        print(f"[{i}/{len(csv_files)}] Processing {csv_file}...")
        
        try:
            file_rows = 0
            file_valid = 0
            file_skipped = 0
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    file_rows += 1
                    total_rows += 1
                    
                    # Get coordinates
                    try:
                        lon = float(row.get('Longitude', 0))
                        lat = float(row.get('Latitude', 0))
                        
                        if lon == 0 or lat == 0 or abs(lon) < 10 or abs(lat) < 10:
                            file_skipped += 1
                            total_skipped += 1
                            continue
                            
                    except (ValueError, TypeError):
                        file_skipped += 1
                        total_skipped += 1
                        continue
                    
                    # Parse year
                    year = parse_date(row.get('Date_Plantation', ''))
                    if year:
                        trees_with_dates += 1
                        year_range['min'] = min(year_range['min'], year)
                        year_range['max'] = max(year_range['max'], year)
                    
                    # Tree types
                    tree_type_latin = row.get('Essence_latin', 'Unknown') or 'Unknown'
                    tree_type_french = row.get('Essence_fr', 'Inconnu') or 'Inconnu'
                    tree_type_english = row.get('Essence_en', 'Unknown') or 'Unknown'
                    tree_types.add(tree_type_english)
                    
                    # Create feature
                    geojson["features"].append({
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [lon, lat]
                        },
                        "properties": {
                            "arrondissement": row.get('Arrond', '') or '',
                            "rue": (row.get('Rue', '') or '').strip(),
                            "emplacement": (row.get('Emplacement', '') or '').strip(),
                            "tree_type_latin": tree_type_latin,
                            "tree_type_french": tree_type_french,
                            "tree_type_english": tree_type_english,
                            "diameter": row.get('DHP', '') or '',
                            "plantation_year": year if year else 0,
                        }
                    })
                    
                    file_valid += 1
                    total_valid += 1
            
            print(f"    Rows: {file_rows:,} | Valid: {file_valid:,} | Skipped: {file_skipped:,}")
            
        except Exception as e:
            print(f"    ❌ ERROR: {e}")
            continue
    
    # Add metadata
    geojson["metadata"] = {
        "total_trees": len(geojson["features"]),
        "trees_with_dates": trees_with_dates,
        "year_range": {
            "min": year_range['min'] if year_range['min'] != float('inf') else None,
            "max": year_range['max'] if year_range['max'] != float('-inf') else None
        },
        "tree_types": sorted(list(tree_types)),
        "generated_at": datetime.now().isoformat()
    }
    
    # Write JSON (compact format)
    print(f"\n📝 Writing {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, separators=(',', ':'))
    
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS!")
    print(f"{'='*60}")
    print(f"Output file:     {output_file}")
    print(f"File size:       {file_size_mb:.2f} MB")
    print(f"")
    print(f"CSV rows read:   {total_rows:,}")
    print(f"Trees mapped:    {total_valid:,} ({total_valid/total_rows*100:.1f}%)")
    print(f"Trees skipped:   {total_skipped:,} (no valid coordinates)")
    print(f"Trees w/ dates:  {trees_with_dates:,}")
    print(f"Year range:      {year_range['min']} - {year_range['max']}")
    print(f"Tree species:    {len(tree_types)}")
    print(f"{'='*60}\n")
    
    if total_valid < 100000:
        print(f"⚠️  WARNING: Only {total_valid:,} trees found. Expected 300,000+")
        print(f"   Check if all 7 CSV files were processed correctly.\n")

if __name__ == '__main__':
    print("=" * 60)
    print("Montreal Tree Data Combiner")
    print("=" * 60)
    try:
        combine_csv_files()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
