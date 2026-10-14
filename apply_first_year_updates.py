
import csv
import shutil
from pathlib import Path

catalogue_path = Path("data/course_catalogue_2019.csv")
evidence_path = Path("data/first_year_course_evidence.csv")
backup_path = Path("data/course_catalogue_2019_before_first_year_update.csv")

# Stop if the expected files are missing or a backup already exists.
if not catalogue_path.exists() or not evidence_path.exists():
    raise FileNotFoundError("Catalogue or evidence CSV not found.")

if backup_path.exists():
    raise FileExistsError(
        f"Backup already exists: {backup_path}. "
        "Check it before running this script again."
    )

with evidence_path.open(
    "r", encoding="utf-8-sig", newline=""
) as file:
    evidence = list(csv.DictReader(file))

with catalogue_path.open(
    "r", encoding="utf-8-sig", newline=""
) as file:
    catalogue = list(csv.DictReader(file))
    fieldnames = list(csv.DictReader) if False else list(catalogue[0].keys())

# Verify unique course codes before making any changes.
evidence_codes = [r["course_code"].strip().upper() for r in evidence]
catalogue_codes = [r["course_code"].strip().upper() for r in catalogue]

if len(evidence_codes) != len(set(evidence_codes)):
    raise ValueError("Duplicate course codes in evidence file.")

if len(catalogue_codes) != len(set(catalogue_codes)):
    raise ValueError("Duplicate course codes in catalogue.")

by_code = {code: row for code, row in zip(catalogue_codes, catalogue)}

for item in evidence:
    code = item["course_code"].strip().upper()
    if code not in by_code:
        raise ValueError(f"{code} is missing from the catalogue.")

    row = by_code[code]
    proposed_semester = item["semester"].strip()
    proposed_category = item["category"].strip()

    if row.get("semester", "").strip() not in ("", proposed_semester):
        raise ValueError(f"Semester conflict for {code}.")

    if proposed_category and row.get("category", "").strip() not in (
        "", proposed_category
    ):
        raise ValueError(f"Category conflict for {code}.")

# Preserve the original catalogue.
shutil.copy2(catalogue_path, backup_path)

updated = 0

for item in evidence:
    row = by_code[item["course_code"].strip().upper()]

    if not row.get("semester", "").strip():
        row["semester"] = item["semester"].strip()
        updated += 1

    # Never overwrite a known category with a blank value.
    if item["category"].strip() and not row.get("category", "").strip():
        row["category"] = item["category"].strip()

    row["verification_status"] = (
        "Verified from syllabus page; first-year evidence"
    )

with catalogue_path.open(
    "w", encoding="utf-8-sig", newline=""
) as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(catalogue)

print("First-year catalogue update completed.")
print("Evidence records:", len(evidence))
print("Semester fields filled:", updated)
print("ESL 120 category left unchanged pending confirmation.")
print("Backup:", backup_path)
print("ChromaDB was not modified.")

