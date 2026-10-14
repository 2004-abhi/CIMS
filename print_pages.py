
import json
import sys
from pathlib import Path

jsonl_path = Path("data/pdf_full_text.jsonl")

pages = {}

with jsonl_path.open("r", encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)
        pages[int(record["pdf_page"])] = record.get("text", "")

requested_pages = [int(arg) for arg in sys.argv[1:]]

if not requested_pages:
    print("Usage: python print_pages.py 490 491")
    sys.exit(1)

for page_number in requested_pages:
    print(f"\n--- PDF PAGE {page_number} ---\n")
    print(pages.get(page_number, "Page not found in JSONL"))
