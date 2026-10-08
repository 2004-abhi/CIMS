import json
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# Load intents.json
with open("intent/intents.json", "r", encoding="utf-8") as file:
    data = json.load(file)


# Create lists for training
sentences = []
labels = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        sentences.append(pattern)
        labels.append(intent["tag"])


print("Training sentences:", len(sentences))
print("Intents:", set(labels))


# Convert text into numerical features
vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(sentences)

print("TF-IDF shape:", X.shape)


# Create the Logistic Regression model
model = LogisticRegression(max_iter=1000)


# Train the model
model.fit(X, labels)

print("Model training completed!")


# Save the trained model
joblib.dump(model, "intent/model/intent_model.pkl")

# Save the TF-IDF vectorizer
joblib.dump(vectorizer, "intent/model/tfidf_vectorizer.pkl")

print("Model and vectorizer saved successfully!")