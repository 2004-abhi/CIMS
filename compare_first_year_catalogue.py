
import csv
from pathlib import Path

evidence_file = Path("data/first_year_course_evidence.csv")
catalogue_file = Path("data/course_catalogue_2019.csv")

def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))

evidence = read_csv(evidence_file)
catalogue = read_csv(catalogue_file)

catalogue_by_code = {
    row["course_code"].strip().upper(): row
    for row in catalogue
}

print("FIRST-YEAR CATALOGUE COMPARISON")
print("=" * 70)

matched = 0
missing = 0

for item in evidence:
    code = item["course_code"].strip().upper()
    existing = catalogue_by_code.get(code)

    if existing:
        matched += 1
        differences = []

        for field in ("course_title", "semester", "category"):
            expected = item[field].strip()
            current = existing.get(field, "").strip()

            if expected and current and expected.upper() != current.upper():
                differences.append(
                    f"{field}: catalogue={current!r}, evidence={expected!r}"
                )

        status = "MATCH" if not differences else "REVIEW"
        print(f"\n{code}: {status}")

        for difference in differences:
            print("  -", difference)

        if not differences:
            print("  Existing catalogue record found.")
    else:
        missing += 1
        print(f"\n{code}: MISSING FROM CATALOGUE")

print("\n" + "=" * 70)
print("Evidence records:", len(evidence))
print("Found in catalogue:", matched)
print("Missing from catalogue:", missing)
print("\nNo files were modified.")
