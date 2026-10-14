
import csv
from pathlib import Path

def load_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))

evidence = load_csv("data/sem3_sem4_course_evidence.csv")
catalogue = load_csv("data/course_catalogue_2019.csv")

by_code = {
    row["course_code"].strip().upper(): row
    for row in catalogue
}

report = []

for item in evidence:
    code = item["course_code"].strip().upper()
    existing = by_code.get(code)

    if existing is None:
        action = "MISSING FROM CATALOGUE"
        current_semester = ""
        current_category = ""
    else:
        current_semester = existing.get("semester", "").strip()
        current_category = existing.get("category", "").strip()

        if current_semester and current_semester != item["semester"]:
            action = "REVIEW SEMESTER CONFLICT"
        elif not current_semester:
            action = "POTENTIAL UPDATE"
        else:
            action = "REVIEW CATEGORY"

    row = {
        "course_code": code,
        "course_title_evidence": item["course_title"],
        "semester_current": current_semester,
        "semester_proposed": item["semester"],
        "category_current": current_category,
        "category_confirmed": item["category"],
        "source_pages": item["source_pages"],
        "action": action,
    }
    report.append(row)

    print(
        f"{code}: {action} | "
        f"semester {current_semester or '(blank)'}"
        f" -> {item['semester']} | "
        f"source page {item['source_pages']}"
    )

output = Path("data/sem3_sem4_update_review.csv")

with output.open("w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=report[0].keys())
    writer.writeheader()
    writer.writerows(report)

print("\nEvidence records:", len(evidence))
print("Review report:", output)
print("No files were modified.")
