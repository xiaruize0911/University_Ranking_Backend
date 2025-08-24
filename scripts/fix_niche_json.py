#!/usr/bin/env python3
"""
Script to fix broken JSON file with duplicate keys and improper separation.
This script reads the malformed JSON file, merges duplicate keys by keeping 
the first appearance, and outputs a properly formatted JSON file.
"""

import json
import re
from collections import OrderedDict


def fix_broken_json(input_file_path, output_file_path):
    """
    Fix broken JSON file with duplicate keys and improper structure.
    
    Args:
        input_file_path (str): Path to the broken JSON file
        output_file_path (str): Path to save the fixed JSON file
    """
    print(f"Reading broken JSON from: {input_file_path}")
    
    # Read the entire file content
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()
    
    # Remove the outer braces and split by },{ pattern to separate objects
    # First, remove the leading { and trailing }
    content = content.strip()
    if content.startswith('{'):
        content = content[1:]
    if content.endswith('}'):
        content = content[:-1]
    
    # Split by '},\n{' pattern to get individual object contents
    object_parts = re.split(r'\},\s*\n\s*\{', content)
    
    print(f"Found {len(object_parts)} JSON objects to process")
    
    # Dictionary to store merged data (using OrderedDict to preserve order of first appearance)
    merged_data = OrderedDict()
    
    # Process each object part
    for i, part in enumerate(object_parts):
        try:
            # Add back the braces that were removed during splitting
            if not part.strip().startswith('"'):
                part = '{' + part
            if not part.strip().endswith('}'):
                part = part + '}'
            
            # Handle edge cases for first and last parts
            if i == 0 and not part.startswith('{'):
                part = '{' + part
            if i == len(object_parts) - 1 and not part.endswith('}'):
                part = part + '}'
            
            # Parse the JSON object
            try:
                obj = json.loads(part)
            except json.JSONDecodeError:
                # Try fixing common issues
                part = part.strip()
                if part.startswith('"{') or part.startswith('"}'):
                    # Remove quotes around the object
                    part = part[1:-1] if part.endswith('"') else part[1:]
                if not part.startswith('{'):
                    part = '{' + part
                if not part.endswith('}'):
                    part = part + '}'
                obj = json.loads(part)
            
            # Merge into the main dictionary (keep first appearance of each key)
            for key, value in obj.items():
                if key not in merged_data:
                    merged_data[key] = value
                    print(f"Added new key: {key[:50]}{'...' if len(key) > 50 else ''}")
                else:
                    print(f"Skipped duplicate key: {key[:50]}{'...' if len(key) > 50 else ''}")
                    
        except json.JSONDecodeError as e:
            print(f"Error parsing object {i + 1}: {e}")
            print(f"Problematic content (first 200 chars): {part[:200]}")
            continue
        except Exception as e:
            print(f"Unexpected error processing object {i + 1}: {e}")
            continue
    
    print(f"\nMerged data contains {len(merged_data)} unique keys")
    
    # Write the fixed JSON to output file
    print(f"Writing fixed JSON to: {output_file_path}")
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(merged_data, file, indent=2, ensure_ascii=False)
    
    print("✅ JSON file has been successfully fixed!")
    
    # Print some statistics
    print(f"\n📊 Statistics:")
    print(f"   - Total unique URLs: {len(merged_data)}")
    print(f"   - Total universities across all categories: {sum(len(universities) for universities in merged_data.values())}")
    
    # Show a sample of the data
    print(f"\n📋 Sample of fixed data:")
    for i, (url, universities) in enumerate(merged_data.items()):
        if i >= 3:  # Show only first 3 entries
            break
        print(f"   {url}: {len(universities)} universities")
        print(f"      First few: {', '.join(universities[:3])}{'...' if len(universities) > 3 else ''}")


def main():
    """Main function to run the JSON fixing process."""
    input_file = "/Users/xiaruize/Documents/Code/Software Engineering/University_Ranking/University_Ranking_Backend/data/niche_college_rankings.json"
    output_file = "/Users/xiaruize/Documents/Code/Software Engineering/University_Ranking/University_Ranking_Backend/data/niche_college_rankings_fixed.json"
    
    try:
        fix_broken_json(input_file, output_file)
    except FileNotFoundError:
        print(f"❌ Error: Input file not found: {input_file}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
