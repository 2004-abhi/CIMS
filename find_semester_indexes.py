
import json
import re

with open("data/pdf_full_text.jsonl", encoding="utf-8") as file:
    pages = {
        item["pdf_page"]: item["text"]
        for item in map(json.loads, file)
    }

for number, text in pages.items():
    upper = text.upper()

    # Look for semester-wise course tables
    has_course_codes = bool(
        re.search(r"\bCST\s*\d{3}\b|\bMAT\s*\d{3}\b|\bEST\s*\d{3}\b", upper)
    )

    has_table_headers = (
        "CATEGORY" in upper
        and ("PAGE NO" in upper or "COURSE CODE" in upper)
    )

    has_semester = bool(
        re.search(
            r"SEMESTER\s+(?:I{1,3}|IV|V|VI|VII|VIII)\b",
            upper
        )
    )

    if has_course_codes and has_table_headers and has_semester:
        print(f"\nPDF PAGE: {number}")
        print(text[:1000])
        print("-" * 50)
