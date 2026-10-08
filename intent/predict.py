import joblib


# Load the trained model
model = joblib.load("intent/model/intent_model.pkl")

# Load the TF-IDF vectorizer
vectorizer = joblib.load("intent/model/tfidf_vectorizer.pkl")


# Test sentences
test_sentences = [
    "Hello there",
    "Can you help me?",
    "Thank you so much",
    "Search the uploaded documents",
    "I want to know something",
    "Bye, see you later"
]


# Convert sentences into TF-IDF vectors
X_test = vectorizer.transform(test_sentences)


# Predict intents
predictions = model.predict(X_test)


# Display results
for sentence, prediction in zip(test_sentences, predictions):
    print(f"Message: {sentence}")
    print(f"Predicted Intent: {prediction}")
    print("-" * 40)