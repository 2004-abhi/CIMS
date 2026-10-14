
import csv
from pathlib import Path

def load_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))

evidence = load_csv("data/first_year_course_evidence.csv")
catalogue_path = Path("data/course_catalogue_2019.csv")
catalogue = load_csv(catalogue_path)

by_code = {
    row["course_code"].strip().upper(): row
    for row in catalogue
}

report = []

for item in evidence:
    code = item["course_code"].strip().upper()
    existing = by_code.get(code)

    if existing is None:
        report.append({
            "course_code": code,
            "semester_current": "",
            "semester_proposed": item["semester"],
            "category_current": "",
            "category_proposed": item["category"],
            "action": "MISSING FROM CATALOGUE",
        })
        continue

    current_semester = existing.get("semester", "").strip()
    current_category = existing.get("category", "").strip()

    proposed_semester = item["semester"].strip()
    proposed_category = item["category"].strip()

    if current_semester and current_semester != proposed_semester:
        action = "REVIEW SEMESTER CONFLICT"
    elif current_category and proposed_category and current_category != proposed_category:
        action = "REVIEW CATEGORY CONFLICT"
    elif not current_semester or (proposed_category and not current_category):
        action = "POTENTIAL UPDATE"
    else:
        action = "NO CHANGE NEEDED"

    report.append({
        "course_code": code,
        "semester_current": current_semester,
        "semester_proposed": proposed_semester,
        "category_current": current_category,
        "category_proposed": proposed_category,
        "action": action,
    })

output = Path("data/first_year_update_review.csv")

with output.open("w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=report[0].keys())
    writer.writeheader()
    writer.writerows(report)

for row in report:
    print(
        f"{row['course_code']}: {row['action']} | "
        f"semester {row['semester_current'] or '(blank)'}"
        f" -> {row['semester_proposed']} | "
        f"category {row['category_current'] or '(blank)'}"
        f" -> {row['category_proposed'] or '(unconfirmed)'}"
    )

print(f"\nReview report created: {output}")
print("The main catalogue and ChromaDB were not modified.")

