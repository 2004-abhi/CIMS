
import csv
from pathlib import Path

path = Path("data/sem3_sem4_course_evidence.csv")

categories = {
    "MAT 203": "BSC",
    "CST 201": "PCC",
    "CST 203": "PCC",
    "CST 205": "PCC",
    "CSL 201": "PCC",
    "CSL 203": "PCC",
    "CST 281": "MINOR",
    "CST 283": "MINOR",
    "CST 285": "MINOR",
    "MAT 206": "BSC",
    "CST 202": "PCC",
    "CST 204": "PCC",
    "CST 206": "PCC",
    "CSL 202": "PCC",
    "CSL 204": "PCC",
    "CST 282": "MINOR",
    "CST 284": "VAC",
    "CST 286": "MINOR",
    "CST 294": "VAC",
    "CST 296": "HONOURS",
}

with path.open("r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    fields = reader.fieldnames
    rows = list(reader)

updated = 0

for row in rows:
    code = row["course_code"].strip().upper()
    if code in categories:
        row["category"] = categories[code]
        updated += 1

with path.open("w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("Category evidence saved:", updated)
print("Categories remain blank for MCN 201, MCN 202 and HUT 200.")
print("Only the evidence file was modified.")
