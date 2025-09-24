# /backend/ingest_api.py

import os
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import
from langchain_pinecone import Pinecone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

# --- CONFIGURE YOUR API ENDPOINT ---
API_ENDPOINT = os.getenv("INGEST_API_ENDPOINT", "https://www.atcuality.com/llms.txt")  # Updated with your endpoint
# -----------------------------------

# --- CONFIGURE THE DATABASE ---
INDEX_NAME = "rag-index" 
# ------------------------------

def fetch_data_from_api(url, headers={}):
    """Fetches data from the specified API endpoint."""
    print(f"Fetching data from API: {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        print("API data fetched successfully.")
        
        # Try to parse as JSON first, if it fails, return as text
        try:
            return response.json()
        except ValueError:
            # If JSON parsing fails, return the text content
            print("Data is not JSON format, treating as plain text.")
            return response.text
            
    except requests.RequestException as e:
        print(f"Error fetching data from API {url}: {e}")
        return None

def process_api_data(api_data):
    """Processes the raw data from the API into a list of text documents."""
    if not api_data: 
        return []
    
    documents = []
    print("Processing API data into text documents...")
    
    # Handle JSON data (list of objects)
    if isinstance(api_data, list):
        for item in api_data:
            if isinstance(item, dict):
                title = item.get("title", "")
                content = item.get("content", "")
                if content:
                    full_text = f"Title: {title}\n\nContent: {content}"
                    documents.append(full_text)
    
    # Handle JSON data (single object)
    elif isinstance(api_data, dict):
        title = api_data.get("title", "")
        content = api_data.get("content", "")
        if content:
            full_text = f"Title: {title}\n\nContent: {content}"
            documents.append(full_text)
    
    # Handle plain text data
    elif isinstance(api_data, str):
        # Split text into chunks by paragraphs or sections if it's very long
        text_sections = api_data.strip().split('\n\n')
        for i, section in enumerate(text_sections):
            if section.strip():  # Only add non-empty sections
                documents.append(f"Section {i+1}:\n\n{section.strip()}")
    
    print(f"Created {len(documents)} documents from API data.")
    return documents


def main():
    """Main function to ingest API data into Pinecone."""
    if API_ENDPOINT.startswith("https://api.example.com"):
        print(
            "WARNING: API_ENDPOINT is still the placeholder. Set INGEST_API_ENDPOINT in backend/.env or edit ingest_api.py.")
    if not PINECONE_API_KEY:
        print("ERROR: PINECONE_API_KEY is not set. Add it to backend/.env.")
        return
    raw_data = fetch_data_from_api(API_ENDPOINT)
    if not raw_data:
        print("No data fetched; exiting ingestion.")
        return

    docs = process_api_data(raw_data)
    if not docs:
        print("No documents created from API data; exiting ingestion.")
        return

    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.create_documents(docs)
    print(f"Split into {len(chunks)} text chunks.")

    print("Initializing embedding model...")
    # This model produces 768-dimensional vectors to match your Pinecone index.
    model_name = "sentence-transformers/all-mpnet-base-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    print(f"Adding documents to Pinecone index '{INDEX_NAME}'...")
    print("This may take several minutes for large datasets...")

    # Process in smaller batches to show progress
    batch_size = 100
    total_batches = (len(chunks) + batch_size - 1) // batch_size

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...")

        if i == 0:
            # Create new index with first batch
            Pinecone.from_documents(batch, embeddings, index_name=INDEX_NAME)
        else:
            # Add to existing index
            vectorstore = Pinecone.from_existing_index(index_name=INDEX_NAME, embedding=embeddings)
            vectorstore.add_documents(batch)

    print("Documents added to Pinecone successfully.")
    print("--- Ingestion Complete ---")


if __name__ == "__main__":
    main()