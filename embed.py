
import re
import chromadb

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


# ==========================================
# 1. READ THE PDF PAGE BY PAGE
# ==========================================

pdf_path = "data/cse_syllabus_2019_s1_s8.pdf"

print("Reading syllabus PDF...")

reader = PdfReader(pdf_path)

print("Total PDF pages:", len(reader.pages))


# ==========================================
# 2. CREATE CHUNKS WITH PAGE INFORMATION
# ==========================================

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)

chunks = []
metadatas = []
chunk_ids = []

for page_number, page in enumerate(reader.pages, start=1):

    page_text = page.extract_text()

    if not page_text or not page_text.strip():
        continue

    page_chunks = text_splitter.split_text(page_text)

    for chunk in page_chunks:

        if not chunk.strip():
            continue

        # Detect semester only when mentioned in this chunk
        semester_match = re.search(
            r"\bSEMESTER\s*[-:]?\s*(I{1,3}|IV|V?I{0,3}|[1-8])\b",
            chunk,
            re.IGNORECASE
        )

        semester = (
            semester_match.group(1).upper()
            if semester_match
            else "unknown"
        )

        # Detect course codes when present
        course_codes = re.findall(
            r"\b[A-Z]{2,4}\s*\d{3}\b",
            chunk.upper()
        )

        course_codes = sorted(set(
            " ".join(code.split())
            for code in course_codes
        ))

        chunk_id = f"page_{page_number}_chunk_{len(chunks)}"

        chunks.append(chunk)
        chunk_ids.append(chunk_id)

        metadatas.append({
            "source": pdf_path,
            "page": page_number,
            "semester": semester,
            "course_codes": ", ".join(course_codes) or "unknown"
        })


print("Total chunks created:", len(chunks))

if not chunks:
    raise RuntimeError("No text chunks were extracted from the PDF.")


# ==========================================
# 3. LOAD THE EMBEDDING MODEL
# ==========================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ==========================================
# 4. CONNECT TO CHROMADB
# ==========================================

client = chromadb.PersistentClient(path="chroma_db")

# Keep the original collection unchanged
collection = client.get_or_create_collection(
    name="cims_syllabus_v2",
    metadata={"hnsw:space": "cosine"}
)

print("New collection: cims_syllabus_v2")


# ==========================================
# 5. CREATE EMBEDDINGS AND SAVE
# ==========================================

print("Creating embeddings and saving chunks...")

batch_size = 100

for start in range(0, len(chunks), batch_size):

    end = min(start + batch_size, len(chunks))

    batch_chunks = chunks[start:end]

    embeddings = embedding_model.encode(
        batch_chunks,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    collection.upsert(
        ids=chunk_ids[start:end],
        documents=batch_chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadatas[start:end]
    )

    print(f"Saved {end}/{len(chunks)} chunks")


print("\nIngestion completed successfully!")
print("New collection document count:", collection.count())
print("Original cims_syllabus collection has not been deleted.")
