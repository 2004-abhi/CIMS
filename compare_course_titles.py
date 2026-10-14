
import csv
from pathlib import Path
from collections import defaultdict

catalogue_path = Path("data/course_catalogue_2019.csv")
candidates_path = Path("data/course_heading_review_v3.csv")


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


catalogue = read_csv(catalogue_path)
candidates = read_csv(candidates_path)

candidate_titles = defaultdict(set)

for row in candidates:
    code = row.get("course_code_candidate", "").strip().upper()
    title = row.get("title_candidate", "").strip().upper()
    title = title.removeprefix("COURSE NAME").strip()

    if code and title:
        candidate_titles[code].add(" ".join(title.upper().split()))

print("Course-title comparison")
print("-" * 80)

mismatches = 0

for course in catalogue:
    code = course.get("course_code", "").strip().upper()
    catalogue_title = " ".join(
        course.get("course_title", "").upper().split()
    )
    titles = candidate_titles.get(code, set())

    if titles and catalogue_title not in titles:
        mismatches += 1
        print(f"\nCode: {code}")
        print(f"Catalogue title: {catalogue_title}")
        print("Candidate title(s):")
        for title in sorted(titles):
            print(f"  - {title}")

    elif not titles:
        mismatches += 1
        print(f"\nCode: {code}")
        print(f"Catalogue title: {catalogue_title}")
        print("No non-empty candidate title found.")

print("\n" + "-" * 80)
print(f"Records needing title review: {mismatches}")
print("Inspection only. No files were modified.")
