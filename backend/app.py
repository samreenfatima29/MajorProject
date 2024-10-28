# import requests
# from flask import Flask, request, render_template,jsonify
# from langchain_community.llms import Ollama
# from langchain_community.vectorstores import Chroma
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
# from langchain_community.document_loaders import PDFPlumberLoader
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains import create_retrieval_chain
# from langchain.prompts import PromptTemplate
# from transformers import pipeline
# from langchain_huggingface import HuggingFaceEmbeddings

# # Use a CPU-friendly embedding model
# embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")



# app = Flask(__name__)

# folder_path = "db"

# # Endpoint for Ollama's local embedding service
# ollama_endpoint = "http://127.0.0.1:11434/api/embeddings"

# cached_llm = Ollama(model="phi3")

# # embedding = Ollama(model="all-minilm")
# # embedding_model = Ollama(model="nomic-embed-text") 
# # data chunking
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
# )

# # ollama endpoint api generation
# '''
# # Function to generate embeddings using Ollama's API
# def generate_embeddings(chunk_texts):
#     embeddings = []
#     for text in chunk_texts:
#         payload = {
#             "model": "all-minilm",  # Assuming this is your local model name
#             "prompt": text
#         }
#         try:
#             response = requests.post(ollama_endpoint, json=payload)
#             response.raise_for_status()
#             response_data = response.json()
#             embeddings.append(response_data['embedding'])
#         except requests.exceptions.RequestException as e:
#             print(f"Request error: {e}")
#         except requests.exceptions.JSONDecodeError as e:
#             print(f"JSON decode error: {e}")
#             print("Response content:", response.content)
#     return embeddings
# '''
# # sending the prompt to the model input is the input and context is from the db
# raw_prompt = PromptTemplate.from_template(
#     """ 
#     <s>[INST] You are a technical assistant good at searching docuemnts. If you do not have an answer from the provided information say so. [/INST] </s>
#     [INST] {input}
#            Context: {context} 
#            Answer:
#     [/INST]
# """
# )

# @app.route("/")
# def index():
#     return render_template("index.html")

# # the api end point for taking the query input 
# @app.route("/ai", methods=["POST"])
# def aiPost():
#     print("Post /ai called")
#     json_content = request.json
#     query = json_content.get("query")

#     print(f"query: {query}")

#     # response = cached_llm.invoke(query)
#     response="This endpoint is working fine"

#     print(response)

#     response_answer = {"answer": response}
#     return response_answer

# # asking questions from these pdfs

# @app.route("/ask_pdf", methods=["POST"])
# def askPDFPost():
#     print("Post /ask_pdf called")
#     json_content = request.json
#     query = json_content.get("query")

#     print(f"query: {query}")

#     print("Loading vector store")
#     vector_store = Chroma(persist_directory=folder_path, embedding_function=embedding)
#     # creating retreiver
#     print("Creating chain")
#     retriever = vector_store.as_retriever(
#         search_type="similarity_score_threshold",
#         search_kwargs={
#             "k": 20, # picking 20 most similar chunks
#             "score_threshold": 0.1,
#         },
#     )

#     document_chain = create_stuff_documents_chain(cached_llm, raw_prompt)
#     chain = create_retrieval_chain(retriever, document_chain)

#     result = chain.invoke({"input": query})

#     print(result)

#     sources = []
#     for doc in result["context"]:
#         sources.append(
#             {"source": doc.metadata["source"], "page_content": doc.page_content}
#         )

#     response_answer = {"answer": result["answer"], "sources": sources}
#     return response_answer

# # uploading files to the pdf directory 
# @app.route("/pdf", methods=["POST"])
# def pdfPost():
#     file = request.files["file"]
#     file_name = file.filename
#     save_file = "pdf/" + file_name
#     file.save(save_file)
#     print(f"filename: {file_name}")
#     # check if its saved in the pdf directory
#     '''
#     response ={"status":"successfully uploaded","file_name":file_name}
#     print(response)
#     return response
#     '''
   
#     loader = PDFPlumberLoader(save_file)
#     docs = loader.load_and_split()
#     print(f"docs len={len(docs)}")

#     chunks = text_splitter.split_documents(docs)
#     print(f"chunks len={len(chunks)}")

#     vector_store = Chroma.from_documents(
#         documents=chunks, embedding=embedding, persist_directory=folder_path
#     )

#     vector_store.persist()

#     response = {
#         "status": "Successfully Uploaded",
#         "filename": file_name,
#         "doc_len": len(docs),
#         "chunks": len(chunks),
#     }
#     return response


# def start_app():
#     app.run(host="0.0.0.0", port=8080, debug=True) # flask app where it is running


# if __name__ == "__main__":
#     start_app()

# hard coded response code 

import os
from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from langchain_community.llms import Ollama
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate
from transformers import pipeline
# Initialize the app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure random key
CORS(app)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

# Prescription model
class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

folder_path="db"
# Use a CPU-friendly embedding model
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Cached LLM for testing
cached_llm = Ollama(model="phi3")

# Data chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
)

@app.route("/")
def index():
    return render_template("index.html")

# Registration endpoint
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists."}), 400

    # Store the user with plain text password
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully."}), 201

# Login endpoint
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.password == password:  # Check plain text password
        return jsonify({"message": "Login successful."}), 200

    return jsonify({"message": "Invalid credentials."}), 401

# Prescription generation endpoint
@app.route("/prescription", methods=["POST"])
def generate_prescription():
    data = request.json
    user_id = data.get("user_id")  # Ensure you send user ID with the request
    prescription_content = data.get("prescription")

    new_prescription = Prescription(user_id=user_id, content=prescription_content)
    db.session.add(new_prescription)
    db.session.commit()

    return jsonify({"message": "Prescription generated successfully.", "data": prescription_content}), 200
'''
# Endpoint for testing the model
@app.route("/ask_pdf", methods=["POST"])
def aiPost():
    json_content = request.json
    query = json_content.get("query")

    response = "This is a hardcoded response. The model is working fine."
    return {"answer": response}

# Uploading files to the PDF directory
@app.route("/pdf", methods=["POST"])
def pdfPost():
    file = request.files["file"]
    file_name = file.filename
    save_file = "pdf/" + file_name
    file.save(save_file)

    response = {
        "status": "Successfully Uploaded",
        "filename": file_name,
        "doc_len": 0,
        "chunks": 0,
    }
    return response
'''

# sending the prompt to the model input is the input and context is from the db
raw_prompt = PromptTemplate.from_template(
    """ 
    <s>[INST] You are a technical assistant good at searching docuemnts. If you do not have an answer from the provided information say so. [/INST] </s>
    [INST] {input}
           Context: {context} 
           Answer:
    [/INST]
"""
)

# the api end point for taking the query input 
@app.route("/ai", methods=["POST"])
def aiPost():
    print("Post /ai called")
    json_content = request.json
    query = json_content.get("query")

    print(f"query: {query}")

    # response = cached_llm.invoke(query)
    response="This endpoint is working fine"

    print(response)

    response_answer = {"answer": response}
    return response_answer

# asking questions from these pdfs

@app.route("/ask_pdf", methods=["POST"])
def askPDFPost():
    print("Post /ask_pdf called")
    json_content = request.json
    query = json_content.get("query")

    print(f"query: {query}")

    print("Loading vector store")
    vector_store = Chroma(persist_directory=folder_path, embedding_function=embedding)
    # creating retreiver
    print("Creating chain")
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 20, # picking 20 most similar chunks
            "score_threshold": 0.1,
        },
    )

    document_chain = create_stuff_documents_chain(cached_llm, raw_prompt)
    chain = create_retrieval_chain(retriever, document_chain)

    result = chain.invoke({"input": query})

    print(result)

    sources = []
    for doc in result["context"]:
        sources.append(
            {"source": doc.metadata["source"], "page_content": doc.page_content}
        )

    response_answer = {"answer": result["answer"], "sources": sources}
    return response_answer

# uploading files to the pdf directory 
@app.route("/pdf", methods=["POST"])
def pdfPost():
    file = request.files["file"]
    file_name = file.filename
    save_file = "pdf/" + file_name
    file.save(save_file)
    print(f"filename: {file_name}")
    # check if its saved in the pdf directory
    '''
    response ={"status":"successfully uploaded","file_name":file_name}
    print(response)
    return response
    '''
   
    loader = PDFPlumberLoader(save_file)
    docs = loader.load_and_split()
    print(f"docs len={len(docs)}")

    chunks = text_splitter.split_documents(docs)
    print(f"chunks len={len(chunks)}")

    vector_store = Chroma.from_documents(
        documents=chunks, embedding=embedding, persist_directory=folder_path
    )

    vector_store.persist()

    response = {
        "status": "Successfully Uploaded",
        "filename": file_name,
        "doc_len": len(docs),
        "chunks": len(chunks),
    }
    return response

def start_app():
    app.run(host="0.0.0.0", port=8080, debug=True)

if __name__ == "__main__":
    start_app()



# based on patient names retreival (trial)

# import os
# import re
# from datetime import datetime, timedelta
# import spacy
# from flask import Flask, request, render_template, jsonify
# from langchain_community.llms import Ollama
# from langchain_community.vectorstores import Chroma
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import PDFPlumberLoader
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains import create_retrieval_chain
# from langchain.prompts import PromptTemplate
# from transformers import pipeline
# from langchain_huggingface import HuggingFaceEmbeddings
# # Load SpaCy NLP model for entity extraction
# nlp = spacy.load("en_core_web_sm")

# # Use a CPU-friendly embedding model
# embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# app = Flask(__name__)

# folder_path = "db"

# # Endpoint for Ollama's local embedding service
# ollama_endpoint = "http://127.0.0.1:11434/api/embeddings"

# cached_llm = Ollama(model="phi3")

# # Data chunking
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
# )

# # Prompt template for model queries
# raw_prompt = PromptTemplate.from_template(
#     """
#     <s>[INST] You are a technical assistant good at searching documents. 
#     If you do not have an answer from the provided information say so. [/INST] </s>
#     [INST] {input}
#            Context: {context} 
#            Answer:
#     [/INST]
#     """
# )

# # Function to extract name and time range from the query
# def extract_name_and_time_from_query(query):
#     doc = nlp(query)
#     patient_name = None
#     years_back = None

#     # Extract patient name (assuming it's a proper noun)
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             patient_name = ent.text
#             break

#     # Extract time range (phrases like "last 5 years")
#     time_match = re.search(r"last (\d+) years", query)
#     if time_match:
#         years_back = int(time_match.group(1))

#     return patient_name, years_back

# # Function to extract metadata from PDF text using regex
# def extract_metadata_from_pdf_text(text):
#     patient_name = None
#     report_date = None

#     # Example regex patterns (adjust these based on your report format)
#     name_match = re.search(r"Patient Name:\s*([A-Za-z\s]+)", text)
#     date_match = re.search(r"Report Date:\s*(\d{4}-\d{2}-\d{2})", text)

#     if name_match:
#         patient_name = name_match.group(1).strip()
#     if date_match:
#         report_date = date_match.group(1)

#     return patient_name, report_date

# # Function to filter reports by patient name and time range
# def filter_reports_by_patient_and_time(vector_store, patient_name, years_back):
#     current_date = datetime.now()
#     threshold_date = current_date - timedelta(days=years_back * 365)

#     filtered_documents = []
#     for doc in vector_store.get_all_documents():
#         report_date_str = doc.metadata.get("report_date")
#         report_date = datetime.strptime(report_date_str, "%Y-%m-%d") if report_date_str else None
#         if doc.metadata.get("patient_name") == patient_name and report_date and report_date >= threshold_date:
#             filtered_documents.append(doc)

#     return filtered_documents

# # Route to handle the main chatbot interface
# @app.route("/")
# def index():
#     return render_template("index.html")

# # Endpoint for handling AI queries
# @app.route("/ai", methods=["POST"])
# def aiPost():
#     json_content = request.json
#     query = json_content.get("query")

#     print(f"Query: {query}")

#     # Extract patient name and time range from query using NLP
#     patient_name, years_back = extract_name_and_time_from_query(query)
#     if not patient_name:
#         return jsonify({"error": "Could not extract patient name from query"}), 400
#     if not years_back:
#         years_back = 5  # Default to 5 years if not provided

#     # Load vector store and filter based on patient and time range
#     vector_store = Chroma(persist_directory=folder_path, embedding_function=embedding)
#     filtered_reports = filter_reports_by_patient_and_time(vector_store, patient_name, years_back)

#     # Create retrieval chain and get response
#     retriever = vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 20, "score_threshold": 0.1})
#     document_chain = create_stuff_documents_chain(cached_llm, raw_prompt)
#     chain = create_retrieval_chain(retriever, document_chain)

#     result = chain.invoke({"input": query})

#     print(result)

#     sources = [{"source": doc.metadata["source"], "page_content": doc.page_content} for doc in result["context"]]

#     response_answer = {"answer": result["answer"], "sources": sources}
#     return jsonify(response_answer)

# # Endpoint for handling PDF uploads and metadata extraction
# @app.route("/pdf", methods=["POST"])
# def pdfPost():
#     file = request.files["file"]
#     file_name = file.filename
#     save_file = f"pdf/{file_name}"
#     file.save(save_file)

#     print(f"Filename: {file_name}")

#     # Load and split the PDF
#     loader = PDFPlumberLoader(save_file)
#     docs = loader.load_and_split()

#     print(f"Docs length: {len(docs)}")

#     # Extract text from first page for metadata extraction (adjust if needed)
#     pdf_text = docs[0].page_content

#     # Try extracting metadata from PDF text using regex
#     patient_name, report_date = extract_metadata_from_pdf_text(pdf_text)

#     # If metadata extraction fails, ask the user to input manually
#     if not patient_name or not report_date:
#         patient_name = request.form.get("patient_name")
#         report_date = request.form.get("report_date")
#         if not patient_name or not report_date:
#             return jsonify({"error": "Please provide patient name and report date"}), 400

#     # Rename PDF with patient name and report date
#     new_file_name = f"{patient_name}_{report_date}.pdf"
#     new_file_path = f"pdf/{new_file_name}"
#     os.rename(save_file, new_file_path)

#     # Add metadata to documents
#     for doc in docs:
#         doc.metadata["patient_name"] = patient_name
#         doc.metadata["report_date"] = report_date

#     # Split the document into chunks
#     chunks = text_splitter.split_documents(docs)
#     print(f"Chunks length: {len(chunks)}")

#     # Persist in ChromaDB with metadata
#     vector_store = Chroma.from_documents(documents=chunks, embedding_function=embedding, persist_directory=folder_path)
#     vector_store.persist()

#     response = {
#         "status": "Successfully Uploaded",
#         "filename": new_file_name,
#         "doc_len": len(docs),
#         "chunks": len(chunks),
#     }
#     return jsonify(response)

# # Function to start the Flask app
# def start_app():
#     app.run(host="0.0.0.0", port=8080, debug=True)

# if __name__ == "__main__":
#     start_app()


# light weight model 


# import requests
# from flask import Flask, request, render_template, jsonify
# from langchain_community.vectorstores import Chroma
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains import create_retrieval_chain
# from langchain.prompts import PromptTemplate
# from transformers import pipeline
# from langchain_huggingface import HuggingFaceEmbeddings

# # Use a CPU-friendly embedding model
# embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# app = Flask(__name__)

# folder_path = "db"

# # Use the GPT-Neo model
# gpt_neo_model = "EleutherAI/gpt-neo-125M"  # Use a smaller model for CPU
# llm = pipeline("text-generation", model=gpt_neo_model)

# # Data chunking
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
# )

# # Sending the prompt to the model
# raw_prompt = PromptTemplate.from_template(
#     """ 
#     <s>[INST] You are a technical assistant good at searching documents. If you do not have an answer from the provided information say so. [/INST] </s>
#     [INST] {input}
#            Context: {context} 
#            Answer:
#     [/INST]
#     """
# )

# @app.route("/")
# def index():
#     return render_template("index.html")

# # The API endpoint for taking the query input 
# @app.route("/ai", methods=["POST"])
# def aiPost():
#     print("Post /ai called")
#     json_content = request.json
#     query = json_content.get("query")

#     print(f"query: {query}")

#     response = llm(query, max_length=100)[0]['generated_text']

#     print(response)

#     response_answer = {"answer": response}
#     return response_answer

# # Asking questions from these PDFs
# @app.route("/ask_pdf", methods=["POST"])
# def askPDFPost():
#     print("Post /ask_pdf called")
#     json_content = request.json
#     query = json_content.get("query")

#     print(f"query: {query}")

#     print("Loading vector store")
#     vector_store = Chroma(persist_directory=folder_path, embedding_function=embedding)

#     # Creating retriever
#     print("Creating chain")
#     retriever = vector_store.as_retriever(
#         search_type="similarity_score_threshold",
#         search_kwargs={
#             "k": 20,  # picking 20 most similar chunks
#             "score_threshold": 0.1,
#         },
#     )

#     document_chain = create_stuff_documents_chain(llm, raw_prompt)
#     chain = create_retrieval_chain(retriever, document_chain)

#     result = chain.invoke({"input": query})

#     print(result)

#     sources = []
#     for doc in result["context"]:
#         sources.append(
#             {"source": doc.metadata["source"], "page_content": doc.page_content}
#         )

#     response_answer = {"answer": result["answer"], "sources": sources}
#     return response_answer

# # Uploading files to the PDF directory 
# @app.route("/pdf", methods=["POST"])
# def pdfPost():
#     file = request.files["file"]
#     file_name = file.filename
#     save_file = "pdf/" + file_name
#     file.save(save_file)
#     print(f"filename: {file_name}")

#     loader = PDFPlumberLoader(save_file)
#     docs = loader.load_and_split()
#     print(f"docs len={len(docs)}")

#     chunks = text_splitter.split_documents(docs)
#     print(f"chunks len={len(chunks)}")

#     vector_store = Chroma.from_documents(
#         documents=chunks, embedding=embedding, persist_directory=folder_path
#     )

#     vector_store.persist()

#     response = {
#         "status": "Successfully Uploaded",
#         "filename": file_name,
#         "doc_len": len(docs),
#         "chunks": len(chunks),
#     }
#     return response

# def start_app():
#     app.run(host="0.0.0.0", port=8080, debug=True)  # Flask app where it is running

# if __name__ == "__main__":
#     start_app()
