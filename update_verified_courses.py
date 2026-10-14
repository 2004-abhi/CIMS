
import csv
import shutil
from pathlib import Path

catalogue = Path("data/course_catalogue_2019.csv")
backup = Path("data/course_catalogue_2019_backup.csv")

# Never overwrite an existing backup.
if not backup.exists():
    shutil.copy2(catalogue, backup)

verified_courses = {
    "CST 401": {
        "semester": "VII",
        "category": "PCC",
    },
    "CSL 411": {
        "semester": "VII",
        "category": "PCC",
    },
    "CSQ 413": {
        "semester": "VII",
        "category": "PWS",
    },
    "CSD 415": {
        "semester": "VII",
        "category": "PWS",
    },
    "CST 402": {
        "semester": "VIII",
        "category": "PCC",
    },
    "CST 404": {
        "semester": "VIII",
        "category": "PCC",
    },
    "CSD 416": {
        "semester": "VIII",
        "category": "PWS",
    },
}

with catalogue.open("r", newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    rows = list(reader)

if not fieldnames or not {
    "course_code", "semester", "category"
}.issubset(fieldnames):
    raise ValueError("Catalogue is missing required columns.")

updated = []

for row in rows:
    code = row["course_code"].strip()

    if code in verified_courses:
        details = verified_courses[code]
        row["semester"] = details["semester"]
        row["category"] = details["category"]
        row["verification_status"] = "Verified from syllabus page"
        updated.append(code)

missing = set(verified_courses) - set(updated)

if missing:
    raise ValueError(
        f"These course codes were not found: {sorted(missing)}"
    )

with catalogue.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Updated course records:", len(updated))
print("Backup saved to:", backup)
print("ChromaDB was not modified.")
