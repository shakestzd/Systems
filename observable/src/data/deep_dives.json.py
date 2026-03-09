"""Data loader: deep_dives.csv → JSON for the homepage article grid."""
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).parents[3]  # Systems/
csv_path = ROOT / "research" / "deep_dives.csv"

dives = []
with csv_path.open() as f:
    for row in csv.DictReader(f):
        if row["Status"] == "Archived":
            continue
        dives.append({
            "id":       row["ID"],
            "focus":    row["Focus Area"],
            "topic":    row["Topic"],
            "question": row["Core Question"],
            "status":   row["Status"],
            "url":      row["url"] or None,
            "arc":      row["arc"].split("→") if row["arc"] else [],
        })

print(json.dumps(dives, indent=2))
