
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


def search_syllabus(question, top_k=5):

    question = question.strip()

    if not question:
        return "Please enter a question."

    question_lower = question.lower()

    # 1. Check CST 204 first to prevent incorrect MAT 101 answers.
    dbms_keywords = [
        "cst 204",
        "cst204",
        "database management systems",
        "dbms"
    ]

    if any(keyword in question_lower for keyword in dbms_keywords):

        pages = [334, 337, 338]

        result = collection.get(
            where={"page": {"$in": pages}},
            include=["documents", "metadatas"]
        )

        documents = result.get("documents", [])
        metadatas = result.get("metadatas", [])

        relevant_sections = []

        for document, metadata in zip(documents, metadatas):
            metadata = metadata or {}
            text = document or ""
            page = metadata.get("page")

            if page == 334:
                if (
                    "CST 204" in text
                    or "Database Management" in text
                ):
                    relevant_sections.append(text)

            elif page in [337, 338]:
                if "Module" in text or "module" in text.lower():
                    relevant_sections.append(text)

        
        if relevant_sections:

            # If the user asks for one specific module,
            # return only that module.
            import re

            module_match = re.search(
                r"\bmodule\s*[-]?\s*(\d+)\b",
                question_lower
            )

            if module_match:
                module_number = int(module_match.group(1))

                all_text = "\n".join(relevant_sections)

                module_pattern = (
                    rf"Module\s*[-]?\s*{module_number}\s*:"
                )

                match = re.search(
                    module_pattern,
                    all_text,
                    re.IGNORECASE
                )

                if match:
                    start = match.start()

                    next_module = re.search(
                        r"Module\s*[-]?\s*\d+\s*:",
                        all_text[match.end():],
                        re.IGNORECASE
                    )

                    end = (
                        match.end() + next_module.start()
                        if next_module
                        else len(all_text)
                    )

                    return all_text[start:end].strip()

                return (
                    f"Module {module_number} was not found "
                    "in the retrieved CST 204 syllabus."
                )

            return "\n\n".join(relevant_sections)


        return (
            "CST 204 was identified, but its syllabus text "
            "was not retrieved."
        )

    # 2. Handle MAT 101 only when explicitly identified.
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

    # 3. Use semantic search for other subjects.
    return search_chromadb(question, top_k)



# ==========================================
# 7. TEST SEARCH INDEPENDENTLY
# ==========================================

if __name__ == "__main__":

    print("\nCIMS Syllabus Search")
    print("-------------------")

    while True:

        question = input(
            "\nEnter your syllabus question (or type 'exit'): "
        ).strip()

        if question.lower() == "exit":
            print("Search closed.")
            break

        answer = search_syllabus(question)

        print("\n========== RETRIEVED SYLLABUS ==========")
        print(answer)
