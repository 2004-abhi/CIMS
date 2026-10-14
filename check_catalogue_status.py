
import csv
from collections import Counter

path = "data/course_catalogue_2019.csv"

with open(path, "r", encoding="utf-8-sig", newline="") as file:
    rows = list(csv.DictReader(file))

print("Total catalogue records:", len(rows))
print("\nVerification status counts:")

for status, count in Counter(
    row.get("verification_status", "").strip() or "(blank)"
    for row in rows
).most_common():
    print(f"{status}: {count}")

print("\nMissing semester:", sum(
    not row.get("semester", "").strip() for row in rows
))

print("Missing category:", sum(
    not row.get("category", "").strip() for row in rows
))

print("\nNo files were modified.")
