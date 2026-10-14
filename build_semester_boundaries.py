
import csv
import json
import re
from pathlib import Path

SOURCE = Path("data/pdf_full_text.jsonl")
OUTPUT = Path("data/semester_boundary_review.csv")

SEMESTER_RE = re.compile(
    r"\bSEMESTER\s+(VIII|VII|VI|V|IV|III|II|I|8|7|6|5|4|3|2|1)\b",
    re.IGNORECASE,
)

def normalize_semester(value):
    value = value.upper()

    mapping = {
        "1": "I", "2": "II", "3": "III", "4": "IV",
        "5": "V", "6": "VI", "7": "VII", "8": "VIII",
    }

    return mapping.get(value, value)

rows = []

with SOURCE.open(encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)
        text = record.get("text", "")
        matches = list(SEMESTER_RE.finditer(text))

        if not matches:
            continue

        for match in matches:
            start = max(0, match.start() - 120)
            end = min(len(text), match.end() + 300)
            context = re.sub(r"\s+", " ", text[start:end]).strip()

            rows.append({
                "pdf_page": record["pdf_page"],
                "semester_candidate": normalize_semester(match.group(1)),
                "heading_context": context,
                "review_status": "needs_review",
            })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "pdf_page",
            "semester_candidate",
            "heading_context",
            "review_status",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)

print("Created:", OUTPUT)
print("Semester heading candidates:", len(rows))
print("All records require contextual verification.")
