from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import nltk
from nltk.tokenize import sent_tokenize
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
import time
import zipfile
import io
import PyPDF2

app = FastAPI()

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust for production as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to calculate sentence importance using TF-IDF and embeddings
def calculate_importance(sentences):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)
    tfidf_scores = tfidf_matrix.sum(axis=1).A1  # Sum of TF-IDF scores for each sentence

    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(sentences)
    cosine_similarities = util.pytorch_cos_sim(embeddings, embeddings)

    # Combine the scores: average of TF-IDF and cosine similarities
    combined_scores = (tfidf_scores + cosine_similarities.mean(axis=1).numpy()) / 2
    ranked_sentences = sorted(zip(sentences, combined_scores), key=lambda x: x[1], reverse=True)
    
    # Return top 10 ranked sentences
    return [sentence for sentence, score in ranked_sentences[:10]]

# Function to generate questions from sentences using Hugging Face API
def generate_questions(sentences):
    questions_and_answers = []
    API_URL = "https://api-inference.huggingface.co/models/valhalla/t5-small-qg-hl"
    headers = {"Authorization": "Bearer YOUR_HUGGINGFACE_API_KEY"}  # Replace with your Hugging Face API key

    for sentence in sentences:
        payload = {"inputs": f"Make a sensible question from this sentence: {sentence}"}
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            time.sleep(1)

            if response.status_code == 200:
                generated_question = response.json()[0]['generated_text'].strip()
                questions_and_answers.append({
                    "question": generated_question,
                    "answer": sentence.strip()
                })
        except Exception as e:
            print(f"Error generating question: {e}")
            continue

    return questions_and_answers

# Endpoint to handle file uploads
@app.post("/upload/")
async def upload_file(papers: UploadFile = File(...)):
    try:
        # Read the content of the uploaded file
        content = await papers.read()

        if papers.filename.endswith('.zip'):
            # Process ZIP file containing PDFs
            zip_contents = io.BytesIO(content)
            all_flashcards = []
            
            with zipfile.ZipFile(zip_contents, 'r') as zip_ref:
                for filename in zip_ref.namelist():
                    if filename.endswith('.pdf'):
                        with zip_ref.open(filename) as pdf_file:
                            pdf_content = io.BytesIO(pdf_file.read())
                            text = extract_text_from_pdf(pdf_content)
                            if not text.strip():  # Check if text extraction worked
                                continue
                            sentences = sent_tokenize(text)
                            important_sentences = calculate_importance(sentences)
                            flashcards = generate_questions(important_sentences)
                            

                            all_flashcards.append({
                                "filename": filename,
                                "flashcards": flashcards
                            })
            
            if not all_flashcards:
                return {"error": "No valid flashcards were generated from the ZIP files."}
            
            return {"flashcards": all_flashcards}
        
        elif papers.filename.endswith('.pdf'):
            # Process single PDF file
            pdf_content = io.BytesIO(content)
            text = extract_text_from_pdf(pdf_content)
            if not text.strip():  # Check if text extraction worked
                return {"error": "Text extraction failed for the PDF."}
            
            sentences = sent_tokenize(text)
            important_sentences = calculate_importance(sentences)
            flashcards = generate_questions(important_sentences)
            
            if not flashcards:
                return {"error": "No valid flashcards generated from the PDF."}
            
            return {"flashcards": [{
                "filename": papers.filename,
                "flashcards": flashcards
            }]}

        else:
            return {"error": "Unsupported file format"}
            
    except Exception as e:
        return {"error": str(e)}

