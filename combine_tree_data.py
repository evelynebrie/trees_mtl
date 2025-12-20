#!/usr/bin/env python3
"""
Montreal Tree Data Combiner - Combines 7 CSV files into one GeoJSON
"""

import csv
import json
import glob
import os
import sys
import gzip
from datetime import datetime

# Column names for the CSV files (they don't have headers)
CSV_COLUMNS = [
    'Type_Propriete', 'No_Civique', 'Arrond', 'Arrond_Nom', 
    'Col4', 'Col5', 'Col6', 'Emplacement', 'Essence_code', 
    'Essence_latin', 'Essence_fr', 'Essence_en', 'DHP', 
    'Date_Plantation', 'Date_Releve', 'Col15', 'Col16', 
    'Rue', 'Rue_Nom', 'Col19', 'Col20', 'Col21', 'Col22', 
    'Col23', 'Col24', 'Col25', 'Col26', 'Secteur', 
    'X_Coord', 'Y_Coord', 'Longitude', 'Latitude'
]

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
    
    # Get headers from first file
    first_file_headers = None
    
    # Process each file
    for i, csv_file in enumerate(csv_files, 1):
        print(f"[{i}/{len(csv_files)}] Processing {csv_file}...")
        
        try:
            file_rows = 0
            file_valid = 0
            file_skipped = 0
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                # Read first line to check if it's a header
                first_line = f.readline().strip()
                f.seek(0)  # Reset to beginning
                
                # If this is the first file, check if it has headers
                if i == 1:
                    # If first line contains column names (not just numbers), use it
                    if any(name in first_line for name in ['Arrond', 'Longitude', 'Latitude', 'Essence']):
                        print(f"    ✓ First file has headers - using them for all files")
                        reader = csv.DictReader(f)
                        first_file_headers = reader.fieldnames
                    else:
                        print(f"    ✓ No headers detected - using predefined columns")
                        reader = csv.DictReader(f, fieldnames=CSV_COLUMNS)
                        first_file_headers = CSV_COLUMNS
                else:
                    # For subsequent files, use the same header structure
                    # Skip first line if it looks like data (not a header)
                    if not any(name in first_line for name in ['Arrond', 'Longitude', 'Latitude', 'Essence']):
                        reader = csv.DictReader(f, fieldnames=first_file_headers)
                    else:
                        reader = csv.DictReader(f)
                
                for row in reader:
                    file_rows += 1
                    total_rows += 1
                    
                    # Get coordinates
                    try:
                        lon = float(row.get('Longitude', 0))
                        lat = float(row.get('Latitude', 0))
                        
                        # Skip if coordinates are missing or zero
                        # Montreal coords: lon ≈ -73.6, lat ≈ 45.5
                        if lon == 0 or lat == 0:
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
                    
                    # Create feature - Ultra compact version with short keys
                    geojson["features"].append({
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [lon, lat]
                        },
                        "properties": {
                            "a": row.get('Arrond', '') or '',  # arrondissement
                            "r": (row.get('Rue_Nom', '') or '').strip(),  # rue
                            "e": (row.get('Emplacement', '') or '').strip(),  # emplacement
                            "tl": tree_type_latin,  # tree_type_latin
                            "tf": tree_type_french,  # tree_type_french
                            "te": tree_type_english,  # tree_type_english
                            "d": row.get('DHP', '') or '',  # diameter
                            "y": year if year else 0,  # plantation_year
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
    
    # Also write gzipped version for GitHub
    gzip_file = output_file + '.gz'
    print(f"📝 Writing {gzip_file} (compressed)...")
    with gzip.open(gzip_file, 'wt', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, separators=(',', ':'))
    
    gzip_size_mb = os.path.getsize(gzip_file) / (1024 * 1024)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS!")
    print(f"{'='*60}")
    print(f"JSON file:       {output_file} ({file_size_mb:.2f} MB)")
    print(f"Gzipped file:    {gzip_file} ({gzip_size_mb:.2f} MB)")
    print(f"Compression:     {(1 - gzip_size_mb/file_size_mb)*100:.1f}% smaller")
    print(f"")
    print(f"CSV rows read:   {total_rows:,}")
    print(f"Trees mapped:    {total_valid:,} ({total_valid/total_rows*100:.1f}%)")
    print(f"Trees skipped:   {total_skipped:,} (no valid coordinates)")
    print(f"Trees w/ dates:  {trees_with_dates:,}")
    print(f"Year range:      {year_range['min']} - {year_range['max']}")
    print(f"Tree species:    {len(tree_types)}")
    print(f"{'='*60}\n")
    
    if gzip_size_mb > 100:
        print(f"⚠️  WARNING: Gzipped file is still {gzip_size_mb:.2f} MB")
        print(f"   GitHub limit is 100 MB. Consider further optimization.\n")

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
