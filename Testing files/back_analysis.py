import os
import glob
import numpy as np
import PyPDF2
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import gridfs
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('DATABASE_NAME')]
fs = gridfs.GridFS(db)

# Use the syllabus path from environment variable
syllabus_path = os.getenv('SYLLABUS_PATH')

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
CORS(app)  # Enable CORS

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

# Route to upload and process file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save file to MongoDB GridFS
    file_id = fs.put(file, filename=file.filename)
    
    # Save the file locally if needed
    file_path = os.path.join(os.getenv('UPLOAD_FOLDER'), file.filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(file.read())

    # Process the file with your ML model
    ranked_topics = analyze_past_papers(os.getenv('UPLOAD_FOLDER'), syllabus_path)
    
    return jsonify({'file_id': str(file_id), 'ranked_topics': ranked_topics})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
