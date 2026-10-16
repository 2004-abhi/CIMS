
import csv
import chromadb
from pathlib import Path

CATALOGUE_FILE = Path("data/course_catalogue_2019.csv")
DB_PATH = "chroma_db"
COLLECTION_NAME = "cims_syllabus_v2"

# Load the existing course catalogue
with CATALOGUE_FILE.open(
    "r", encoding="utf-8-sig", newline=""
) as file:
    catalogue = list(csv.DictReader(file))

print(f"Catalogue records: {len(catalogue)}")

# Connect to ChromaDB without changing any records
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_collection(name=COLLECTION_NAME)

print(f"ChromaDB records: {collection.count()}")

# Check how many records have usable metadata
total = 0
missing_semester = 0
missing_course_code = 0
unknown_semester = 0
unknown_course_code = 0

offset = 0
batch_size = 500

while offset < collection.count():
    result = collection.get(
        limit=batch_size,
        offset=offset,
        include=["metadatas"]
    )

    metadatas = result.get("metadatas") or []

    for metadata in metadatas:
        metadata = metadata or {}
        total += 1

        semester = str(metadata.get("semester", "")).strip()
        course_codes = str(
            metadata.get("course_codes", "")
        ).strip()

        if not semester:
            missing_semester += 1
        elif semester.lower() == "unknown":
            unknown_semester += 1

        if not course_codes:
            missing_course_code += 1
        elif course_codes.lower() == "unknown":
            unknown_course_code += 1

    offset += len(metadatas)

print("\n--- Existing metadata audit ---")
print(f"Records inspected: {total}")
print(f"Blank semester: {missing_semester}")
print(f"Unknown semester: {unknown_semester}")
print(f"Blank course code: {missing_course_code}")
print(f"Unknown course code: {unknown_course_code}")

print("\n--- Catalogue example ---")
for row in catalogue:
    if row["course_code"].strip().upper() == "CST 201":
        print(row)
        break

print("\nAudit complete. No database records were changed.")
