
import csv
import json
import re
from pathlib import Path

SOURCE = Path("data/pdf_full_text.jsonl")
OUTPUT = Path("data/course_heading_review_v2.csv")

CODE_RE = re.compile(
    r"\b(MAT|CST|CSL|CSD|CSQ|EST|ESL|PHT|PHL|CYT|CYL|"
    r"HUN|HUT|MCN|MCT|PEC|PCC|OEC|VAC|UK|ITT)\s*(\d{3})\b",
    re.IGNORECASE,
)

def clean(text):
    return re.sub(r"\s+", " ", text).strip(" :-\n\t")

def normalize_code(match):
    return f"{match.group(1).upper()} {match.group(2)}"

rows = []

with SOURCE.open(encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)
        page = record["pdf_page"]
        text = record.get("text", "")

        # Find the syllabus table heading.
        category = re.search(r"\bCATEGORY\b", text, re.IGNORECASE)
        if not category:
            continue

        # Only inspect codes before CATEGORY.
        # Codes later in outcomes/prerequisites are not course headings.
        heading_area = text[:category.start()]
        matches = list(CODE_RE.finditer(heading_area))

        if not matches:
            continue

        # Use the last code before CATEGORY because course codes and
        # titles may be separated by line breaks in extracted PDF text.
        match = matches[-1]
        code = normalize_code(match)

        # The title is the text between this code and CATEGORY.
        title = clean(heading_area[match.end():])

        # Avoid accepting an empty or excessively long title.
        if not title or len(title) > 180:
            title = ""

        rows.append({
            "pdf_page": page,
            "course_code_candidate": code,
            "title_candidate": title,
            "semester": "",
            "course_category": "",
            "verification_status": "needs_manual_review",
            "source_heading_text": clean(heading_area[-350:]),
        })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=[
        "pdf_page",
        "course_code_candidate",
        "title_candidate",
        "semester",
        "course_category",
        "verification_status",
        "source_heading_text",
    ])
    writer.writeheader()
    writer.writerows(rows)

print("Review v2 created.")
print("Candidate rows:", len(rows))
print("Output:", OUTPUT)
print("Semester and category remain blank until verified.")
