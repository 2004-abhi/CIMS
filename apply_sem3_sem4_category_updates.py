
import csv
import os
import shutil

catalogue_path = "data/course_catalogue_2019.csv"
evidence_path = "data/sem3_sem4_course_evidence.csv"
backup_path = "data/course_catalogue_2019_before_sem3_sem4_category_update.csv"

# Categories confirmed from the syllabus pages
verified_categories = {
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

# Read both files
with open(catalogue_path, "r", newline="", encoding="utf-8-sig") as f:
    catalogue = list(csv.DictReader(f))
    fieldnames = list(catalogue[0].keys())

with open(evidence_path, "r", newline="", encoding="utf-8-sig") as f:
    evidence = list(csv.DictReader(f))

catalogue_by_code = {
    row["course_code"].strip(): row for row in catalogue
}

evidence_by_code = {
    row["course_code"].strip(): row for row in evidence
}

# Validate that every expected course exists in both files
missing_catalogue = [
    code for code in verified_categories
    if code not in catalogue_by_code
]
missing_evidence = [
    code for code in verified_categories
    if code not in evidence_by_code
]

if missing_catalogue or missing_evidence:
    print("STOP: Validation failed.")
    print("Missing from catalogue:", missing_catalogue)
    print("Missing from evidence:", missing_evidence)
    raise SystemExit(1)

# Check evidence categories and existing catalogue conflicts
conflicts = []

for code, category in verified_categories.items():
    evidence_category = evidence_by_code[code].get("category", "").strip()
    existing_category = catalogue_by_code[code].get("category", "").strip()

    if evidence_category != category:
        conflicts.append(
            f"{code}: expected evidence {category}, "
            f"found {evidence_category or '(blank)'}"
        )
    elif existing_category and existing_category != category:
        conflicts.append(
            f"{code}: catalogue has {existing_category}, "
            f"evidence says {category}"
        )

if conflicts:
    print("STOP: Resolve these conflicts before updating:")
    for conflict in conflicts:
        print("-", conflict)
    raise SystemExit(1)

# Create a backup before changing the catalogue
if os.path.exists(backup_path):
    print("STOP: Backup already exists:", backup_path)
    print("Rename the existing backup before running again.")
    raise SystemExit(1)

shutil.copy2(catalogue_path, backup_path)

# Apply only the verified category changes
updated = []

for code, category in verified_categories.items():
    row = catalogue_by_code[code]

    if not row.get("category", "").strip():
        row["category"] = category
        updated.append(code)

# Correct the title using the confirmed syllabus heading on PDF page 469
mcn202 = catalogue_by_code.get("MCN 202")

if mcn202:
    old_title = mcn202.get("course_title", "").strip()
    if old_title != "CONSTITUTION OF INDIA":
        mcn202["course_title"] = "CONSTITUTION OF INDIA"
        if "MCN 202 title corrected from syllabus page 469" not in mcn202.get(
            "verification_status", ""
        ):
            old_status = mcn202.get("verification_status", "").strip()
            note = "MCN 202 title corrected from syllabus page 469"
            mcn202["verification_status"] = (
                f"{old_status}; {note}" if old_status else note
            )

# Preserve existing source-page references and add confirmed pages
source_pages_to_add = {
    "MAT 203": ["213"],
    "CST 201": ["224"],
    "CST 203": ["235"],
    "CST 205": ["246"],
    "CSL 201": ["258"],
    "CSL 203": ["266"],
    "CST 281": ["273"],
    "CST 283": ["285"],
    "CST 285": ["296"],
    "MAT 206": ["307"],
    "CST 202": ["322"],
    "CST 204": ["334"],
    "CST 206": ["349"],
    "CSL 202": ["359"],
    "CSL 204": ["364"],
    "CST 282": ["370"],
    "CST 284": ["381"],
    "CST 286": ["396"],
    "CST 294": ["418"],
    "CST 296": ["435"],
    "MCN 201": ["448"],
    "MCN 202": ["469"],
    "HUT 200": ["462", "484"],
}

for code, pages in source_pages_to_add.items():
    row = catalogue_by_code.get(code)
    if not row:
        continue

    existing = [
        p.strip()
        for p in row.get("source_pages", "").split(",")
        if p.strip()
    ]

    for page in pages:
        if page not in existing:
            existing.append(page)

    row["source_pages"] = ",".join(existing)

# Save the updated catalogue
with open(catalogue_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(catalogue)

print("Catalogue update completed successfully.")
print("New categories added:", len(updated))
print("Updated course codes:", ", ".join(updated) if updated else "None")
print("MCN 202 title checked against syllabus page 469.")
print("Source-page references updated where necessary.")
print("Backup created:", backup_path)
print("ChromaDB was not modified.")

