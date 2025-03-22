import nltk
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
import time

def calculate_importance(sentences):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)
    tfidf_scores = tfidf_matrix.sum(axis=1).A1  

    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(sentences)
    cosine_similarities = util.pytorch_cos_sim(embeddings, embeddings)

    combined_scores = (tfidf_scores + cosine_similarities.mean(axis=1).numpy()) / 2

    ranked_sentences = sorted(zip(sentences, combined_scores), key=lambda x: x[1], reverse=True)
    
    return ranked_sentences

def generate_questions(sentences):
    questions_and_answers = []
    API_URL = "https://api-inference.huggingface.co/models/valhalla/t5-small-qg-hl"
    headers = {"Authorization": "Bearer -"}  

    for sentence in sentences:
        payload = {"inputs": f"Make a sensible question from this sentence: {sentence}"}
        
        response = requests.post(API_URL, headers=headers, json=payload)
        time.sleep(1)  

        if response.status_code == 200:
            try:
                generated_question = response.json()[0]['generated_text'].strip()
                questions_and_answers.append((generated_question, sentence.strip()))
            except (IndexError, KeyError, TypeError):
                questions_and_answers.append(("Error: Unexpected API response format", sentence.strip()))
        else:
            questions_and_answers.append((f"Error: {response.status_code}", sentence.strip()))

    return questions_and_answers


def main():
    text = """Sleep is a vital function that allows the body and mind to recharge, leaving you refreshed and alert when you wake up. A good night’s sleep helps improve memory, learning, and decision-making. It also plays a crucial role in maintaining physical health by supporting immune function and regulating metabolism.

Lack of sleep has been linked to various health problems, including an increased risk of heart disease, obesity, and depression. Experts recommend that adults get between 7 to 9 hours of sleep per night to function optimally. Establishing a consistent sleep schedule, avoiding screens before bedtime, and creating a relaxing bedtime routine can help improve sleep quality.

Caffeine and heavy meals before bed can interfere with sleep, making it harder to fall and stay asleep. Additionally, exposure to natural sunlight during the day can help regulate the body's sleep-wake cycle, promoting better sleep at night.

"""

    sentences = nltk.sent_tokenize(text)
    num_sentences = 5
    importance_scores = calculate_importance(sentences)
    selected_sentences = [sentence for sentence, _ in importance_scores[:num_sentences]]

    questions_and_answers = generate_questions(selected_sentences)

    print("\nGenerated Questions and Answers:")
    for q, a in questions_and_answers:
        print(f"- Q: {q}\n  A: {a}\n")

if __name__ == "__main__":
    main()
