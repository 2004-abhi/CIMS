
import csv
import os
import shutil

catalogue_path = "data/course_catalogue_2019.csv"
backup_path = "data/course_catalogue_2019_before_remaining_semesters.csv"

# Semester and category evidence extracted from the PDF.
# Semester VII: pages are after the Semester VII heading (PDF p. 885).
# Semester VIII: pages are after the Semester VIII heading (PDF p. 1074).
evidence = {
    # Courses at the end of the Semester VI section
    "MCN 301": {"semester": "VI", "category": ""},
    "HUT 300": {"semester": "VI", "category": "HSMC"},
    "HUT 310": {"semester": "VI", "category": "HMC"},

    # Semester VII
    "CST 413": {"semester": "VII", "category": "PEC"},
    "CST 423": {"semester": "VII", "category": "PEC"},
    "CST 433": {"semester": "VII", "category": "PEC"},
    "CST 443": {"semester": "VII", "category": "PEC"},
    "CST 463": {"semester": "VII", "category": "PEC"},
    "CST 473": {"semester": "VII", "category": "PEC"},
    "CST 415": {"semester": "VII", "category": "OEC"},
    "CST 425": {"semester": "VII", "category": "OEC"},
    "CST 435": {"semester": "VII", "category": "OEC"},
    "CST 445": {"semester": "VII", "category": "OEC"},
    "CST 455": {"semester": "VII", "category": "OEC"},
    "CSD 481": {"semester": "VII", "category": "PWS"},
    "CST 495": {"semester": "VII", "category": "VAC"},
    "CST 497": {"semester": "VII", "category": "VAC"},
    "CST 499": {"semester": "VII", "category": "VAC"},

    # Semester VIII
    "CST 414": {"semester": "VIII", "category": "PEC"},
    "CST 424": {"semester": "VIII", "category": "PEC"},
    "CST 434": {"semester": "VIII", "category": "PEC"},
    "CST 444": {"semester": "VIII", "category": "PEC"},
    "CST 454": {"semester": "VIII", "category": "PEC"},
    "CST 464": {"semester": "VIII", "category": "PEC"},
    "CST 474": {"semester": "VIII", "category": "PEC"},
    "CST 416": {"semester": "VIII", "category": "PEC"},
    "CST 426": {"semester": "VIII", "category": "PEC"},
    "CST 436": {"semester": "VIII", "category": "PEC"},
    "CST 446": {"semester": "VIII", "category": "PEC"},
    "CST 466": {"semester": "VIII", "category": "PEC"},
    "CST 476": {"semester": "VIII", "category": "PEC"},
    "CST 418": {"semester": "VIII", "category": "PEC"},
    "CST 428": {"semester": "VIII", "category": "PEC"},
    "CST 438": {"semester": "VIII", "category": "PEC"},
    "CST 448": {"semester": "VIII", "category": "PEC"},
    "CST 458": {"semester": "VIII", "category": "PEC"},
    "CST 468": {"semester": "VIII", "category": "PEC"},
    "CST 478": {"semester": "VIII", "category": "PEC"},
    "CSD 482": {"semester": "VIII", "category": "PWS"},
    "CSD 496": {"semester": "VIII", "category": "PWS"},
}

if not os.path.exists(catalogue_path):
    raise SystemExit(f"Catalogue not found: {catalogue_path}")

with open(catalogue_path, "r", newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    courses = list(reader)
    fieldnames = reader.fieldnames

if not courses or not fieldnames:
    raise SystemExit("Catalogue is empty or has no header.")

by_code = {row["course_code"].strip(): row for row in courses}

missing_codes = sorted(set(evidence) - set(by_code))
if missing_codes:
    print("STOP: These codes are missing from the catalogue:")
    for code in missing_codes:
        print("-", code)
    raise SystemExit(1)

# Stop rather than overwrite any existing conflicting values.
conflicts = []

for code, values in evidence.items():
    row = by_code[code]

    old_semester = row.get("semester", "").strip()
    new_semester = values["semester"]

    if old_semester and old_semester != new_semester:
        conflicts.append(
            f"{code}: existing semester {old_semester}, "
            f"proposed semester {new_semester}"
        )

    old_category = row.get("category", "").strip()
    new_category = values["category"]

    if old_category and new_category and old_category != new_category:
        conflicts.append(
            f"{code}: existing category {old_category}, "
            f"PDF category {new_category}"
        )

if conflicts:
    print("STOP: Resolve conflicts before updating:")
    for item in conflicts:
        print("-", item)
    raise SystemExit(1)

if os.path.exists(backup_path):
    print("STOP: Backup already exists:", backup_path)
    print("Rename it before running this script again.")
    raise SystemExit(1)

shutil.copy2(catalogue_path, backup_path)

semester_updates = []
category_updates = []

for code, values in evidence.items():
    row = by_code[code]

    if not row.get("semester", "").strip():
        row["semester"] = values["semester"]
        semester_updates.append(code)

    if (
        values["category"]
        and not row.get("category", "").strip()
    ):
        row["category"] = values["category"]
        category_updates.append(code)

    # Record that semester assignment uses page order and heading evidence.
    old_status = row.get("verification_status", "").strip()
    note = "Semester assigned from PDF page order and heading evidence"

    if note not in old_status:
        row["verification_status"] = (
            f"{old_status}; {note}" if old_status else note
        )

with open(catalogue_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(courses)

print("Catalogue update completed.")
print("Semester fields filled:", len(semester_updates))
print("Category fields filled:", len(category_updates))
print("Backup created:", backup_path)
print("MCN 301 category left blank because its heading was unclear.")
print("Existing course-code discrepancy CST 362 / CSL 362 unchanged.")
print("ChromaDB was not modified.")
