import csv
import sys
import os

def convert_kicad_to_jlcpcb(input_path, output_path):
    print(f"Converting '{input_path}' to '{output_path}'...")

    try:
        # 1. Read input rows efficiently
        rows = []
        with open(input_path, mode='r', newline='', encoding='utf-8') as f_in:
            # Detect format (comma separated, maybe quoted)
            # We trust standard csv reader handles quotes automatically
            reader = csv.DictReader(f_in)
            
            # Normalize field names (strip whitespace)
            fieldnames = [field.strip() for field in reader.fieldnames]
            reader.fieldnames = fieldnames
            
            # Check required columns
            required = ['Ref', 'PosX', 'PosY', 'Rot', 'Side']
            missing = [col for col in required if col not in fieldnames]
            
            if missing:
                print(f"Error: Missing columns {missing}. Found: {fieldnames}")
                return

            for row in reader:
                # 2. Extract and transform data
                # Strip whitespace from values just in case
                designator = row['Ref'].strip()
                mid_x = row['PosX'].strip()
                mid_y = row['PosY'].strip()
                rotation = row['Rot'].strip()
                
                # Check layer case: 'top' -> 'Top'
                layer = row['Side'].strip().capitalize()
                
                rows.append({
                    'Designator': designator,
                    'Mid X': mid_x,
                    'Mid Y': mid_y,
                    'Layer': layer,
                    'Rotation': rotation
                })

        # 3. Write output file
        with open(output_path, mode='w', newline='', encoding='utf-8') as f_out:
            fieldnames = ['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation']
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(rows)
            
        print(f"Successfully wrote {len(rows)} components to clean file.")

    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Default paths matching the user request
    input_file = "CAM/assembly/fcg4-top-pos.csv"
    output_file = "CAM/assembly/fcg4-top-clean.csv"
    
    # Allow overriding via command line
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        
    convert_kicad_to_jlcpcb(input_file, output_file)
