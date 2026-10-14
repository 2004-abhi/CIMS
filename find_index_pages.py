
import json
import re
from pathlib import Path

source = Path("data/pdf_full_text.jsonl")

pattern = re.compile(
    r"SEMESTER\s*(?:[-–:]?\s*)"
    r"(?:I{1,3}|IV|V?I{0,3}|VI{0,2}|VII|VIII|\d+)\b",
    re.IGNORECASE,
)

with source.open("r", encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)
        text = record.get("text", "")
        if pattern.search(text):
            preview = " ".join(text.split())[:220]
            print(f"PDF page {record['pdf_page']}: {preview}")
