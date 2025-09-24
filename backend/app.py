# /backend/app.py

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import Pinecone
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

# Basic environment validation
if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set. Please add it to your .env file.")
if not PINECONE_API_KEY:
    print("[WARN] PINECONE_API_KEY is not set. Pinecone operations may fail.", flush=True)

# --- CONFIGURE THE DATABASE ---
INDEX_NAME = "rag-index"
# ------------------------------

# Initialize Flask App and CORS
app = Flask(__name__)
CORS(app)

@app.get('/health')
def health():
    return jsonify({"status": "ok"})

# Initialize LLM and Embeddings
llm = ChatAnthropic(model="claude-3-5-sonnet-latest", api_key=anthropic_api_key)
# This model produces 768-dimensional vectors
model_name = "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

# Connect to the existing Pinecone index
print("Loading vector store from Pinecone...")
try:
    vectorstore = Pinecone.from_existing_index(index_name=INDEX_NAME, embedding=embeddings)
    retriever = vectorstore.as_retriever()
    print("Vector store loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load Pinecone index '{INDEX_NAME}': {e}")
    print(f"[INFO] Make sure to run 'python backend/setup_pinecone.py' first to create the index.")
    print(f"[INFO] Then run 'python backend/ingest_static.py' to add sample data.")
    raise

# Prompt Template
prompt_template = """
You are a helpful assistant for the website.
Your goal is to answer user questions based *only* on the context provided.
If the context does not contain the answer, say "I'm sorry, I don't have enough information to answer that question."
CONTEXT:
{context}
USER QUESTION:
{question}
YOUR ANSWER:
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "Invalid request. 'query' is required."}), 400
        
        user_query = data['query'].strip()
        
        # Validate query input
        if not user_query:
            return jsonify({"error": "Query cannot be empty."}), 400
        
        if len(user_query) > 1000:
            return jsonify({"error": "Query is too long. Maximum 1000 characters allowed."}), 400
        
        retrieved_docs = retriever.get_relevant_documents(user_query)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        if not context:
            return jsonify({"response": "I'm sorry, I couldn't find any relevant information to answer your question."})
        
        formatted_prompt = prompt.format(context=context, question=user_query)
        
        # Call the LLM safely; different versions may return string or a message object
        llm_response = llm.invoke(formatted_prompt) if hasattr(llm, "invoke") else llm(formatted_prompt)
        response_text = getattr(llm_response, "content", None) or (llm_response if isinstance(llm_response, str) else str(llm_response))
        
        return jsonify({"response": response_text})
    except Exception as error:
        print(f"An error occurred: {error}")
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)