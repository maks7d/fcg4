import argparse
import csv
from pathlib import Path


def is_excluded(row):
    dnp = row.get("DNP", "").strip()
    exclude_bom = row.get("Exclude from BOM", "").strip().lower()
    return bool(dnp) or "excluded" in exclude_bom


def normalize_footprint(footprint):
    value = footprint.strip()
    if ":" in value:
        return value.split(":", 1)[1]
    return value


def convert_kicad_bom_to_jlcpcb(input_path, output_path):
    print(f"Converting '{input_path}' to '{output_path}'...")

    output_rows = []
    with open(input_path, mode="r", newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header.")

        fieldnames = [field.strip() for field in reader.fieldnames]
        reader.fieldnames = fieldnames

        required = ["Reference", "Value", "Footprint", "LCSC Part Name"]
        missing = [col for col in required if col not in fieldnames]
        if missing:
            raise ValueError(f"Missing columns {missing}. Found: {fieldnames}")

        for row in reader:
            if is_excluded(row):
                continue

            designator = row["Reference"].strip()
            if not designator:
                continue

            output_rows.append(
                {
                    "Comment": row["Value"].strip(),
                    "Designator": designator,
                    "Footprint": normalize_footprint(row["Footprint"]),
                    "JLCPCB Part #（optional）": row["LCSC Part Name"].strip(),
                }
            )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open(mode="w", newline="", encoding="utf-8") as f_out:
        out_fields = ["Comment", "Designator", "Footprint", "JLCPCB Part #（optional）"]
        writer = csv.DictWriter(f_out, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Successfully wrote {len(output_rows)} BOM lines.")


def main():
    parser = argparse.ArgumentParser(description="Convert KiCad BOM CSV to JLCPCB BOM CSV")
    parser.add_argument(
        "input",
        nargs="?",
        default="fcg4.csv",
        help="KiCad BOM CSV (default: fcg4.csv)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="CAM/assembly/fcg4-bom-jlcpcb.csv",
        help="Output JLCPCB BOM CSV (default: CAM/assembly/fcg4-bom-jlcpcb.csv)",
    )
    args = parser.parse_args()

    try:
        convert_kicad_bom_to_jlcpcb(args.input, args.output)
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found.")
    except ValueError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()