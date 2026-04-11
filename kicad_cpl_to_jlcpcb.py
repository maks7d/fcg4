import argparse
import csv
from pathlib import Path


def normalize_layer(layer):
    value = layer.strip().lower()
    if value == "top":
        return "Top"
    if value == "bottom":
        return "Bottom"
    return layer.strip().capitalize()


def normalize_rotation(rotation):
    value = float(rotation.strip()) % 360.0
    if value.is_integer():
        return str(int(value))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def format_mm(value):
    text = value.strip()
    if text.lower().endswith("mm"):
        return text
    return f"{float(text):.4f}mm"


def convert_kicad_to_jlcpcb(input_path, output_path):
    print(f"Converting '{input_path}' to '{output_path}'...")

    rows = []
    with open(input_path, mode="r", newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header.")

        fieldnames = [field.strip() for field in reader.fieldnames]
        reader.fieldnames = fieldnames

        required = ["Ref", "PosX", "PosY", "Rot", "Side"]
        missing = [col for col in required if col not in fieldnames]
        if missing:
            raise ValueError(f"Missing columns {missing}. Found: {fieldnames}")

        for row in reader:
            designator = row["Ref"].strip()
            if not designator:
                continue

            rows.append(
                {
                    "Designator": designator,
                    "Mid X": format_mm(row["PosX"]),
                    "Mid Y": format_mm(row["PosY"]),
                    "Layer": normalize_layer(row["Side"]),
                    "Rotation": normalize_rotation(row["Rot"]),
                }
            )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open(mode="w", newline="", encoding="utf-8") as f_out:
        out_fields = ["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]
        writer = csv.DictWriter(f_out, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully wrote {len(rows)} components.")


def main():
    parser = argparse.ArgumentParser(description="Convert KiCad CPL to JLCPCB CPL format")
    parser.add_argument(
        "input",
        nargs="?",
        default="CAM/assembly/fcg4-all-pos.csv",
        help="KiCad CPL file (default: CAM/assembly/fcg4-top-pos.csv)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="CAM/assembly/fcg4-top-jlcpcb.csv",
        help="Output JLCPCB CPL file (default: CAM/assembly/fcg4-top-jlcpcb.csv)",
    )
    args = parser.parse_args()

    try:
        convert_kicad_to_jlcpcb(args.input, args.output)
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found.")
    except ValueError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
