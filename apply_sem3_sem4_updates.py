
import csv
import shutil
from pathlib import Path

catalogue_path = Path("data/course_catalogue_2019.csv")
evidence_path = Path("data/sem3_sem4_course_evidence.csv")
backup_path = Path("data/course_catalogue_2019_before_sem3_sem4_update.csv")

if not catalogue_path.exists() or not evidence_path.exists():
    raise FileNotFoundError("Catalogue or evidence file is missing.")

if backup_path.exists():
    raise FileExistsError(
        f"Backup already exists: {backup_path}. "
        "Inspect it before running this script again."
    )

def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        return reader.fieldnames, rows

fields, catalogue = read_csv(catalogue_path)
_, evidence = read_csv(evidence_path)

by_code = {
    row["course_code"].strip().upper(): row
    for row in catalogue
}

evidence_codes = [r["course_code"].strip().upper() for r in evidence]

if len(evidence_codes) != len(set(evidence_codes)):
    raise ValueError("Duplicate course codes in evidence file.")

# Validate every record before writing anything.
for item in evidence:
    code = item["course_code"].strip().upper()

    if code not in by_code:
        raise ValueError(f"{code} is missing from the catalogue.")

    current = by_code[code].get("semester", "").strip()
    proposed = item["semester"].strip()

    if current not in ("", proposed):
        raise ValueError(
            f"Semester conflict for {code}: {current} vs {proposed}"
        )

# Back up the catalogue before changing it.
shutil.copy2(catalogue_path, backup_path)

updated = 0

for item in evidence:
    code = item["course_code"].strip().upper()
    row = by_code[code]

    if not row.get("semester", "").strip():
        row["semester"] = item["semester"].strip()
        row["verification_status"] = (
            "Semester assigned from syllabus page evidence; category pending"
        )
        updated += 1

with catalogue_path.open(
    "w", encoding="utf-8-sig", newline=""
) as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(catalogue)

print("Semester III/IV update completed.")
print("Records updated:", updated)
print("Categories and course titles were not changed.")
print("Backup:", backup_path)
print("ChromaDB was not modified.")
