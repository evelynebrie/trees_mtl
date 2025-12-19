#!/usr/bin/env python3
"""
Script to combine multiple tree CSV files and convert to JSON for Mapbox visualization.
Place this script in the same directory as your CSV files (arbres-part-aa.csv through arbres-part-ag.csv)
"""

import csv
import json
import glob
import os
from datetime import datetime

def parse_date(date_string):
    """Parse date string and extract year, handling various formats"""
    if not date_string or date_string.strip() == '':
        return None
    try:
        # Try parsing ISO format
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
    
    # Find all matching CSV files
    csv_files = sorted(glob.glob(pattern))
    
    if not csv_files:
        print(f"No CSV files found matching pattern: {pattern}")
        return
    
    print(f"Found {len(csv_files)} CSV files:")
    for f in csv_files:
        print(f"  - {f}")
    
    # GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    tree_types = set()
    year_range = {'min': float('inf'), 'max': float('-inf')}
    total_trees = 0
    trees_with_dates = 0
    
    # Process each CSV file
    for csv_file in csv_files:
        print(f"\nProcessing {csv_file}...")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                total_trees += 1
                
                # Extract coordinates
                try:
                    longitude = float(row.get('Longitude', 0))
                    latitude = float(row.get('Latitude', 0))
                    
                    # Skip if coordinates are invalid
                    if longitude == 0 or latitude == 0:
                        continue
                    
                except (ValueError, TypeError):
                    continue
                
                # Extract plantation year
                plantation_date = row.get('Date_Plantation', '')
                plantation_year = parse_date(plantation_date)
                
                if plantation_year:
                    trees_with_dates += 1
                    year_range['min'] = min(year_range['min'], plantation_year)
                    year_range['max'] = max(year_range['max'], plantation_year)
                
                # Extract tree type
                tree_type_latin = row.get('Essence_latin', 'Unknown')
                tree_type_french = row.get('Essence_fr', 'Inconnu')
                tree_type_english = row.get('Essence_en', 'Unknown')
                tree_types.add(tree_type_english)
                
                # Create GeoJSON feature
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "properties": {
                        "id": row.get('No_Civiq', ''),
                        "arrondissement": row.get('Arrond', ''),
                        "rue": row.get('Rue', '').strip(),
                        "emplacement": row.get('Emplacement', '').strip(),
                        "type_emplacement": row.get('Type_Emplacement', '').strip(),
                        "tree_type_latin": tree_type_latin,
                        "tree_type_french": tree_type_french,
                        "tree_type_english": tree_type_english,
                        "diameter": row.get('DHP', ''),
                        "plantation_date": plantation_date,
                        "plantation_year": plantation_year,
                        "inventory_date": row.get('Date_Releve', ''),
                        "location_code": row.get('Code_Parc', ''),
                        "position": row.get('Localisation', ''),
                        "sigle": row.get('Sigle', ''),
                        "longitude": longitude,
                        "latitude": latitude
                    }
                }
                
                geojson["features"].append(feature)
    
    # Add metadata
    geojson["metadata"] = {
        "total_trees": len(geojson["features"]),
        "trees_processed": total_trees,
        "trees_with_dates": trees_with_dates,
        "year_range": {
            "min": year_range['min'] if year_range['min'] != float('inf') else None,
            "max": year_range['max'] if year_range['max'] != float('-inf') else None
        },
        "tree_types": sorted(list(tree_types)),
        "generated_at": datetime.now().isoformat()
    }
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Successfully created {output_file}")
    print(f"  Total trees with valid coordinates: {len(geojson['features'])}")
    print(f"  Trees with plantation dates: {trees_with_dates}")
    print(f"  Year range: {year_range['min']} - {year_range['max']}")
    print(f"  Unique tree types: {len(tree_types)}")
    print(f"\n  Tree types found:")
    for tree_type in sorted(list(tree_types))[:10]:
        print(f"    - {tree_type}")
    if len(tree_types) > 10:
        print(f"    ... and {len(tree_types) - 10} more")

if __name__ == '__main__':
    print("Montreal Tree Data Combiner")
    print("=" * 50)
    combine_csv_files()
    print("\nDone! You can now use trees_combined.json with the HTML visualization.")
