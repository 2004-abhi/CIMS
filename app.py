
from flask import Flask, request, jsonify, render_template
import joblib
import json

# Import the syllabus search function
from search import search_syllabus

app = Flask(__name__)


# ==========================================
# 1. LOAD THE INTENT MODEL
# ==========================================

model = joblib.load("intent/model/intent_model.pkl")
vectorizer = joblib.load("intent/model/tfidf_vectorizer.pkl")


# ==========================================
# 2. LOAD STRUCTURED SUBJECT DATA
# ==========================================

with open("data/subjects.json", "r", encoding="utf-8") as file:
    subjects_data = json.load(file)


# ==========================================
# 3. HOME PAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# 4. CHATBOT PREDICTION
# ==========================================

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "response": "Please enter a question."
        }), 400

    normalized_message = message.lower()


    # ======================================
    # A. SEMESTER 1 SUBJECT QUESTIONS
    # ======================================

    semester_keywords = [
        "semester 1",
        "semester i",
        "first semester",
        "sem 1",
        "s1"
    ]

    subject_keywords = [
        "subject",
        "subjects",
        "course",
        "courses"
    ]

    if (
        any(keyword in normalized_message
            for keyword in semester_keywords)
        and any(keyword in normalized_message
                for keyword in subject_keywords)
    ):

        subjects = subjects_data.get("semester_1", [])

        answer = "Semester 1 subjects:\n" + "\n".join(
            f"{subject['code']} - {subject['name']}"
            for subject in subjects
        )

        return jsonify({
            "message": message,
            "intent": "semester_subject_query",
            "response": answer
        })


    # ======================================
    # B. CLASSIFY THE USER'S QUESTION
    # ======================================

    X = vectorizer.transform([message])
    prediction = model.predict(X)[0]


    # ======================================
    # C. SYLLABUS SEARCH
    # ======================================

    syllabus_keywords = [
        "syllabus",
        "module",
        "course outcome",
        "learning outcome",
        "mat 101",
        "mat101",
        "engineering mathematics",
        "linear algebra",
        "fourier series",
        "taylor series",
        "convergence test",
        "partial derivatives",
        "double integrals",
        "triple integrals"
    ]

    is_syllabus_question = any(
        keyword in normalized_message
        for keyword in syllabus_keywords
    )

    if is_syllabus_question or prediction == "document_query":

        try:
            answer = search_syllabus(message)

            return jsonify({
                "message": message,
                "intent": "syllabus_search",
                "response": answer
            })

        except Exception as error:
            app.logger.exception("Syllabus search failed")

            return jsonify({
                "message": message,
                "intent": "syllabus_search",
                "response": (
                    "Sorry, I couldn't search the syllabus right now. "
                    "Please try again."
                )
            }), 500


    # ======================================
    # D. EXISTING INTENT RESPONSES
    # ======================================

    responses = {
        "greeting": "Hello! How can I help you?",
        "help": "I can help with college information and syllabus questions.",
        "thanks": "You're welcome!",
        "goodbye": "Goodbye! Have a great day!",
        "document_query": "Please ask me a specific syllabus question.",
        "information_query": "Please tell me what college information you need.",
        "unknown": "Sorry, I couldn't understand your question."
    }

    return jsonify({
        "message": message,
        "intent": prediction,
        "response": responses.get(
            prediction,
            "Sorry, I couldn't understand your question."
        )
    })


# ==========================================
# 5. RUN THE APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
