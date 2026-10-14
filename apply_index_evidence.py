
import csv
import shutil
from pathlib import Path

catalogue_path = Path("data/course_catalogue_2019.csv")
evidence_path = Path("data/verified_index_evidence.csv")
backup_path = Path("data/course_catalogue_2019_before_index_update.csv")

if not catalogue_path.exists() or not evidence_path.exists():
    raise FileNotFoundError("Catalogue or index evidence file is missing.")

# Create a backup before making changes.
if not backup_path.exists():
    shutil.copy2(catalogue_path, backup_path)

with catalogue_path.open(
    "r", newline="", encoding="utf-8-sig"
) as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames
    catalogue = list(reader)

with evidence_path.open(
    "r", newline="", encoding="utf-8-sig"
) as file:
    evidence = list(csv.DictReader(file))

by_code = {
    row["course_code"].strip(): row
    for row in catalogue
}

updated = []
unmatched = []

for item in evidence:
    code = item["course_code"].strip()

    if code not in by_code:
        unmatched.append(code)
        continue

    row = by_code[code]
    row["semester"] = item["semester"].strip()
    row["category"] = item["category"].strip()
    row["verification_status"] = (
        f"Verified from index PDF page "
        f"{item['evidence_pdf_page']}"
    )
    updated.append(code)

with catalogue_path.open(
    "w", newline="", encoding="utf-8-sig"
) as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(catalogue)

print("Index records updated:", len(updated))
print("Unmatched index codes:", unmatched)
print("Backup:", backup_path)
print("ChromaDB was not modified.")
