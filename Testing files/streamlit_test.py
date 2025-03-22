import os
import glob
import numpy as np
import PyPDF2
import nltk
import re
import streamlit as st
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    return filtered_words

def load_extracted_text(destination_folder):
    all_texts = []
    for file_path in glob.glob(os.path.join(destination_folder, '*_extracted.txt')):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read().strip()
            if text:
                all_texts.append(text)
            else:
                st.warning(f"Skipping empty file: {file_path}")
    if not all_texts:
        st.warning("No text files found!")
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
    return similarity_matrix, topic_names

def rank_topics(all_texts, syllabus_dict, similarity_matrix):
    topic_counts = {topic: 0 for topic in syllabus_dict}
    for i, text in enumerate(all_texts):
        most_similar_topic_idx = np.argmax(similarity_matrix[i])
        most_similar_topic = list(syllabus_dict.keys())[most_similar_topic_idx]
        topic_counts[most_similar_topic] += 1
    ranked_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    return ranked_topics

def analyze_past_papers(destination_folder, syllabus_path):
    all_texts = load_extracted_text(destination_folder)
    syllabus_dict = extract_topic_names(syllabus_path)
    similarity_matrix, topic_names = match_text_to_topics(all_texts, syllabus_dict)
    ranked_topics = rank_topics(all_texts, syllabus_dict, similarity_matrix)    
    return ranked_topics

# Streamlit UI
st.title("Past Papers Analysis")

# File uploader for syllabus (PDF)
syllabus_file = st.file_uploader("Upload Syllabus PDF", type=["zip"])
# File uploader for extracted text files (TXT)
uploaded_files = st.file_uploader("Upload Extracted Text Files", type=["pdf"], accept_multiple_files=True)

if syllabus_file and uploaded_files:
    # Save the syllabus file temporarily
    syllabus_path = "syllabus.pdf"
    with open(syllabus_path, "wb") as f:
        f.write(syllabus_file.getbuffer())

    # Save uploaded text files temporarily
    destination_folder = "uploads"
    os.makedirs(destination_folder, exist_ok=True)
    for uploaded_file in uploaded_files:
        with open(os.path.join(destination_folder, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())

    st.success("Files uploaded successfully!")

    # Analyze past papers
    ranked_topics = analyze_past_papers(destination_folder, syllabus_path)

    # Display ranked topics
    st.subheader("Ranked Topics")
    for topic, count in ranked_topics:
        st.write(f"{topic}: {count}")