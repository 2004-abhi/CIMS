
import chromadb

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection(name="cims_syllabus_v2")

for page in [334, 337, 338]:
    result = collection.get(
        where={"page": page},
        include=["documents", "metadatas"]
    )

    print(f"\n{'=' * 20} PDF PAGE {page} {'=' * 20}")
    print("Chunks found:", len(result["documents"]))

    for i, (document, metadata) in enumerate(
        zip(result["documents"], result["metadatas"]), start=1
    ):
        print(f"\nChunk {i}")
        print("Metadata:", metadata)
        print("Text preview:", (document or "")[:250])

print("\nRead-only test complete.")
