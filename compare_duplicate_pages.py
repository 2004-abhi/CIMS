
import json
import re
from pathlib import Path
from difflib import SequenceMatcher

source = Path("data/pdf_full_text.jsonl")
report = Path("data/course_duplicate_report.csv")

with source.open("r", encoding="utf-8") as file:
    pages = {
        item["pdf_page"]: item["text"]
        for item in map(json.loads, file)
    }

def normalize(text):
    text = text.upper()
    return re.sub(r"\s+", " ", text).strip()

import csv

with report.open("r", encoding="utf-8-sig", newline="") as file:
    duplicates = list(csv.DictReader(file))

for item in duplicates:
    page_numbers = [
        int(number.strip())
        for number in item["source_pages"].split(",")
    ]

    if len(page_numbers) != 2:
        continue

    page1, page2 = page_numbers
    text1 = normalize(pages.get(page1, ""))
    text2 = normalize(pages.get(page2, ""))

    similarity = SequenceMatcher(
        None, text1, text2
    ).ratio() * 100

    print(
        f"{item['course_code']}: "
        f"pages {page1} and {page2} "
        f"-> {similarity:.1f}% text similarity"
    )
