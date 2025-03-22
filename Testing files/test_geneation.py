import spacy
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline 

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

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

# Question Generation
def generate_questions(sentences):
    # Load the question generation model
    question_generator = pipeline("text2text-generation", model="valhalla/t5-base-qa-qg-hl")
    
    questions = []
    for sentence in sentences:
        # Generate questions for each sentence
        generated_questions = question_generator(f"generate question: {sentence}", max_length=50, num_return_sequences=1)
        questions.append(generated_questions[0]['generated_text'])
    
    return questions

def main():
    text = """Complementarity of Values and Skills
Skills are only a means to achieve a given purpose. While skills are required to
achieve a particular purpose in an effective and efficient manner, it is not within the
scope of technology, management, medicine, etc. to decide the purpose. This decision
lies outside its scope. It thus becomes important to identify our purpose as human beings. Without this decision, skills can be aimless, directionless and can therefore, be put to any use – for constructive or destructive purposes.
For instance, students of technology will be studying, creating and implementing
technologies. If they are getting trained on technology without deciding the purpose
of human being, their technical skills could even prove counterproductive when used
to dominate, exploit or harm others. We developed technology for harnessing atomic
energy or nuclear energy. Now, how much of it has been used for welfare purpose and
how much of it has been used for destructive purposes? It seems that we have
generated enough nuclear weapons to destroy this Earth 30 times (needless to say that
one cannot destroy the Earth more than once).
As explained above, values and skills have to go hand in hand. There is an essential
complementarity between the two for the success of any human endeavour towards
the goal of living a fulfilling life."""
    
    sentences = nltk.sent_tokenize(text)
    
    print("\nSentences extracted:")
    for sentence in sentences:
        print(f"- {sentence.strip()}")

    num_sentences = 5
    
    importance_scores = calculate_importance(sentences)

    selected_sentences = importance_scores[:num_sentences]

    print("\nSentences ranked by importance:")
    for sentence, score in selected_sentences:
        print(f"Score: {score:.4f} - Sentence: {sentence.strip()}")

    # Generate questions from the extracted sentences
    questions = generate_questions([sentence for sentence, _ in selected_sentences])

    # Display the generated questions
    print("\nGenerated Questions:")
    for q in questions:
        print(f"- {q}")

if _name_ == '_main_':
    main()