import os
import glob
import numpy as np
import PyPDF2
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
nltk.download('punkt')
nltk.download('stopwords')

def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    return filtered_words

def load_extracted_text(destination_folder):
    print(f"Looking for extracted files in: {destination_folder}")
    all_texts = []
    for file_path in glob.glob(f"{destination_folder}/*_extracted.txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read().strip()
            if text:
                all_texts.append(text)
            else:
                print(f"Skipping empty file: {file_path}")
    if not all_texts:
        print("No text files found!")
    return all_texts


def extract_topic_names(syllabus_path):
    syllabus_dict = {}
    syllabus_text = ""
    with open(syllabus_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            syllabus_text += page.extract_text() or ""
    syllabus_text = re.sub(r'\s+', ' ', syllabus_text.strip())
    topic_pattern = re.compile(r'(Unit \d+:.*?)(?=Unit \d+:|$)', re.DOTALL)
    matches = topic_pattern.findall(syllabus_text)
    for match in matches:
        topic_name, content = match.split(":", 1)
        topic_name = topic_name.strip()  
        content = content.strip()  
        syllabus_dict[topic_name] = content
    return syllabus_dict


def match_text_to_topics(all_texts, syllabus_dict):
    vectorizer = TfidfVectorizer(stop_words='english')
    text_vectors = vectorizer.fit_transform(all_texts)
    similarity_matrix = np.zeros((len(all_texts), len(syllabus_dict)))
    topic_names = list(syllabus_dict.keys())
    topic_contents = list(syllabus_dict.values())
    for i, topic_content in enumerate(topic_contents):
        topic_vector = vectorizer.transform([topic_content])
        similarity_matrix[:, i] = cosine_similarity(text_vectors, topic_vector).flatten()
    print(topic_names)
    print("Similarity Matrix:")
    print(similarity_matrix)
    
    return similarity_matrix, topic_names

def rank_topics(all_texts, syllabus_dict, similarity_matrix):
    topic_counts = {topic: 0 for topic in syllabus_dict}
    for i, text in enumerate(all_texts):
        most_similar_topic_idx = np.argmax(similarity_matrix[i])
        most_similar_topic = list(syllabus_dict.keys())[most_similar_topic_idx]
        topic_counts[most_similar_topic] += 1
    ranked_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    ls=[ls[0] for ls in ranked_topics]
    return ls

def analyze_past_papers(destination_folder, syllabus_path):
    all_texts = load_extracted_text(destination_folder)
    syllabus_dict = extract_topic_names(syllabus_path)
    similarity_matrix, topic_names = match_text_to_topics(all_texts, syllabus_dict)
    ranked_topics = rank_topics(all_texts, syllabus_dict, similarity_matrix)    
    return ranked_topics