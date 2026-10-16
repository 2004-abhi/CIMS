import re
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer


# ==========================================
# 1. LOAD THE EMBEDDING MODEL
# ==========================================

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")


# ==========================================
# 2. CONNECT TO CHROMADB
# ==========================================

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="cims_syllabus_v2"
)

print("ChromaDB connected!")
print("Stored chunks:", collection.count())


# ==========================================
# 3. MAT 101 SYLLABUS FROM THE PDF
# ==========================================

MAT101_MODULES = {
    1: {
        "title": "Linear Algebra",
        "hours": 10,
        "topics": [
            "Systems of linear equations",
            "Solution by Gauss elimination",
            "Row echelon form",
            "Finding rank from row echelon form",
            "Fundamental theorem for linear systems",
            "Eigenvalues and eigenvectors",
            "Diagonalization of matrices",
            "Orthogonal transformation",
            "Quadratic forms and their canonical forms"
        ]
    },

    2: {
        "title": "Multivariable Calculus - Differentiation",
        "hours": 8,
        "topics": [
            "Limits and continuity of functions of two variables",
            "Partial derivatives",
            "Differentials",
            "Local linear approximations",
            "Chain rule",
            "Total derivative",
            "Maxima and minima"
        ]
    },

    3: {
        "title": "Multivariable Calculus - Integration",
        "hours": 10,
        "topics": [
            "Evaluation of double integrals in Cartesian coordinates",
            "Change of order of integration in double integrals",
            "Change of coordinates from Cartesian to polar",
            "Finding areas and volumes",
            "Mass and centre of gravity of plane laminas",
            "Triple integrals"
        ]
    },

    4: {
        "title": "Sequences and Series",
        "hours": 8,
        "topics": [
            "Convergence of sequences and series",
            "Geometric series and p-series",
            "Comparison test",
            "Ratio test",
            "Root test",
            "Alternating series and Leibnitz test",
            "Absolute and conditional convergence"
        ]
    },

    5: {
        "title": "Series Representation of Functions",
        "hours": 9,
        "topics": [
            "Taylor series",
            "Binomial series",
            "Series representation of exponential functions",
            "Series representation of trigonometric functions",
            "Series representation of logarithmic functions",
            "Fourier series",
            "Euler formulas",
            "Convergence of Fourier series and Dirichlet's conditions",
            "Half-range sine and cosine series",
            "Parseval's theorem"
        ]
    }
}


MAT101_OUTCOMES = [
    "CO1: Solve systems of linear equations, diagonalize matrices "
    "and characterise quadratic forms.",

    "CO2: Compute partial and total derivatives and maxima and "
    "minima of multivariable functions.",

    "CO3: Compute multiple integrals and apply them to find areas, "
    "volumes, mass and centre of gravity of plane laminas.",

    "CO4: Perform tests to determine whether a series is convergent, "
    "absolutely convergent or conditionally convergent.",

    "CO5: Determine Taylor and Fourier series expansions of functions "
    "and learn their applications."
]


# ==========================================
# 4. COURSE-SPECIFIC SEARCH
# ==========================================

def format_module(number):
    module = MAT101_MODULES[number]

    result = [
        f"MAT 101 - {module['title']}",
        f"Module {number}",
        f"Lecture hours: {module['hours']}",
        "",
        "Topics:"
    ]

    for topic in module["topics"]:
        result.append(f"- {topic}")

    return "\n".join(result)


def search_mat101(question):
    question_lower = question.lower()

    # Match explicit module references
    module_number = None

    for number in range(1, 6):
        patterns = [
            f"module {number}",
            f"module-{number}",
            f"module{number}",
            f"module {number_in_words(number)}"
        ]

        if any(pattern in question_lower for pattern in patterns):
            module_number = number
            break

    if module_number is not None:
        return format_module(module_number)

    # Return all five modules for a full syllabus question
    syllabus_keywords = [
        "syllabus",
        "all modules",
        "all topics",
        "course contents",
        "full syllabus",
        "complete syllabus"
    ]

    mathematics_keywords = [
        "mat 101",
        "mat101",
        "engineering mathematics",
        "linear algebra and calculus",
        "linear algebra & calculus"
    ]

    is_math_question = any(
        keyword in question_lower
        for keyword in mathematics_keywords
    )

    asks_full_syllabus = any(
        keyword in question_lower
        for keyword in syllabus_keywords
    )

    if is_math_question and asks_full_syllabus:
        sections = [
            "MAT 101 - LINEAR ALGEBRA AND CALCULUS",
            "Course outcomes:",
            *MAT101_OUTCOMES,
            "",
            "MODULE SYLLABUS"
        ]

        for number in range(1, 6):
            sections.append("")
            sections.append(format_module(number))

        sections.append("")
        sections.append(
            "Total scheduled lecture hours: 45"
        )

        return "\n".join(sections)

    # Match questions about course outcomes
    if (
        is_math_question
        and (
            "course outcome" in question_lower
            or "learning outcome" in question_lower
        )
    ):
        return (
            "MAT 101 - Course Outcomes\n\n"
            + "\n".join(MAT101_OUTCOMES)
        )

    return None


def number_in_words(number):
    words = {
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five"
    }
    return words[number]


# ==========================================
# 5. CHROMADB SEMANTIC SEARCH
# ==========================================


def search_chromadb(question, top_k=5):

    count = collection.count()

    if count == 0:
        return "No syllabus documents are stored in ChromaDB."

    question_embedding = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        return "Sorry, no syllabus information was found."

    print("\n========== CHROMADB SEARCH RESULTS ==========")

    relevant_documents = []

    for index, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances), start=1
    ):
        metadata = metadata or {}

        print(f"\nResult {index}")
        print(f"Distance: {distance:.4f}")
        print(f"Page: {metadata.get('page', 'unknown')}")
        print(f"Semester: {metadata.get('semester', 'unknown')}")
        print(f"Course codes: {metadata.get('course_codes', 'unknown')}")
        print("Document preview:")
        print((document or "")[:500])
        print("-" * 50)

        relevant_documents.append(document or "")

    return "\n\n".join(relevant_documents)


# ==========================================
# 6. MAIN SEARCH FUNCTION
# ==========================================

def get_cst204_syllabus(question):
    pdf_path = "data/cse_syllabus_2019_s1_s8.pdf"
    reader = PdfReader(pdf_path)

    # Verified PDF pages containing the CST 204 syllabus.
    page_numbers = [334, 337, 338]
    page_texts = []

    for page_number in page_numbers:
        text = reader.pages[page_number - 1].extract_text() or ""
        page_texts.append(text)

    syllabus_text = "\n".join(page_texts)

    # Remove repeated page headers.
    syllabus_text = re.sub(
        r"COMPUTER SCIENCE AND ENGINEERING",
        "",
        syllabus_text,
        flags=re.IGNORECASE
    )

    # Start at Module 1 to exclude preamble and course outcomes.
    first_module = re.search(
        r"\bModule\s*[-]?\s*1\s*:",
        syllabus_text,
        re.IGNORECASE
    )

    if not first_module:
        return "Could not find the CST 204 module syllabus in the PDF."

    syllabus_text = syllabus_text[first_module.start():]

    # Check whether the user requested a particular module.
    module_match = re.search(
        r"\bmodule\s*[-]?\s*(\d+)\b",
        question,
        re.IGNORECASE
    )

    if module_match:
        module_number = int(module_match.group(1))

        if module_number not in range(1, 6):
            return "CST 204 has Modules 1 to 5."

        heading = re.search(
            rf"\bModule\s*[-]?\s*{module_number}\s*:",
            syllabus_text,
            re.IGNORECASE
        )

        if not heading:
            return f"Module {module_number} was not found in CST 204."

        remaining_text = syllabus_text[heading.end():]

        next_heading = re.search(
            r"\bModule\s*[-]?\s*\d+\s*:",
            remaining_text,
            re.IGNORECASE
        )

        textbook_heading = re.search(
            r"\bText\s*Books\s*:?",
            remaining_text,
            re.IGNORECASE
        )

        end_positions = [
            match.start()
            for match in (next_heading, textbook_heading)
            if match is not None
        ]

        end = min(end_positions) if end_positions else len(remaining_text)

        return (
            syllabus_text[heading.start():heading.end()]
            + remaining_text[:end]
        ).strip()

    # For all modules, exclude the textbook section.
    textbook_heading = re.search(
        r"\bText\s*Books\s*:?",
        syllabus_text,
        re.IGNORECASE
    )

    if textbook_heading:
        syllabus_text = syllabus_text[:textbook_heading.start()]

    return syllabus_text.strip()




# ==========================================
# 7. TEST SEARCH INDEPENDENTLY
# ==========================================

def search_syllabus(question, top_k=5):
    question = question.strip()

    if not question:
        return "Please enter a question."

    question_lower = question.lower()

    # 1. CST 204 syllabus
    dbms_keywords = [
        "cst 204",
        "cst204",
        "database management systems",
        "dbms"
    ]

    if any(keyword in question_lower for keyword in dbms_keywords):
        return get_cst204_syllabus(question)

    # 2. MAT 101 syllabus
    mat101_keywords = [
        "mat 101",
        "mat101",
        "linear algebra and calculus",
        "linear algebra & calculus"
    ]

    if any(keyword in question_lower for keyword in mat101_keywords):
        course_answer = search_mat101(question)

        if course_answer is not None:
            print("\nUsing course-specific MAT 101 syllabus.")
            return course_answer

    # 3. Other subjects
    return search_chromadb(question, top_k)
