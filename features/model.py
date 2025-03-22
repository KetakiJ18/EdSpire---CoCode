import nltk
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
import time

def calculate_importance(sentences):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)
    tfidf_scores = tfidf_matrix.sum(axis=1).A1  # Sum of TF-IDF scores per sentence

    # Use SentenceTransformer to calculate sentence embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(sentences)
    
    # Calculate cosine similarities between sentences
    cosine_similarities = util.pytorch_cos_sim(embeddings, embeddings)
    
    # Combine TF-IDF scores and cosine similarities
    combined_scores = (tfidf_scores + cosine_similarities.mean(axis=1).numpy()) / 2
    
    # Sort sentences by the combined score in descending order
    ranked_sentences = sorted(zip(sentences, combined_scores), key=lambda x: x[1], reverse=True)
    print(f'Ranked Sentences: {ranked_sentences}\n')
    return [sentence for sentence, _ in ranked_sentences]  # Return only ranked sentences

def generate_questions(sentences):
    questions_and_answers = []  # Use list to store question-answer pairs
    API_URL = "https://api-inference.huggingface.co/models/valhalla/t5-small-qg-hl"
    headers = {"Authorization": "Bearer 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"}  # Replace with your own token

    for sentence in sentences:
        payload = {"inputs": f"Make a sensible question from this sentence: {sentence}"}

        # Call the Hugging Face API to generate the question
        response = requests.post(API_URL, headers=headers, json=payload)
        time.sleep(1)  # Sleep to avoid rate-limiting issues
        
        if response.status_code == 200:
            try:
                # Extract generated question from the response
                generated_question = response.json()[0]['generated_text'].strip()
                questions_and_answers.append({
                    "question": generated_question,
                    "answer": sentence.strip()
                })
            except (IndexError, KeyError, TypeError) as e:
                print(f"Error processing API response: {e}")
                questions_and_answers.append({
                    "question": "Error: Unexpected API response format",
                    "answer": sentence.strip()
                })
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            questions_and_answers.append({
                "question": f"Error: {response.status_code}",
                "answer": sentence.strip()
            })

    return questions_and_answers
