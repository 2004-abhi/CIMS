
import csv
from pathlib import Path

catalogue_path = Path("data/course_catalogue_2019.csv")
candidates_path = Path("data/course_heading_review_v3.csv")


def load_csv(path, code_columns):
    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        headers = reader.fieldnames or []

        code_column = next(
            (column for column in code_columns if column in headers),
            None
        )

        if code_column is None:
            raise ValueError(
                f"No supported course-code column in {path}. "
                f"Available columns: {headers}"
            )

        return rows, code_column


catalogue, catalogue_code_column = load_csv(
    catalogue_path, ["course_code", "course_code_candidate"]
)

candidates, candidate_code_column = load_csv(
    candidates_path, ["course_code_candidate", "course_code"]
)


def extract_codes(rows, column):
    return {
        row[column].strip().upper()
        for row in rows
        if row.get(column, "").strip()
    }


catalogue_codes = extract_codes(catalogue, catalogue_code_column)
candidate_codes = extract_codes(candidates, candidate_code_column)

missing_from_catalogue = sorted(candidate_codes - catalogue_codes)
not_in_candidates = sorted(catalogue_codes - candidate_codes)

print(f"Catalogue records: {len(catalogue)}")
print(f"Unique catalogue codes: {len(catalogue_codes)}")
print(f"Candidate rows: {len(candidates)}")
print(f"Unique candidate codes: {len(candidate_codes)}")

print("\n--- Candidate codes absent from catalogue ---")
if missing_from_catalogue:
    for code in missing_from_catalogue:
        print(code)
else:
    print("None")

print("\n--- Catalogue codes absent from candidate file ---")
if not_in_candidates:
    for code in not_in_candidates:
        print(code)
else:
    print("None")

print("\nInspection only. No files were modified.")
