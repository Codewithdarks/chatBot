import os
from pinecone import Pinecone as PineconeClient, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")


def create_pinecone_index(index_name: str):
    """
    Creates a new Pinecone index if it doesn't already exist.
    """
    if not PINECONE_API_KEY or not PINECONE_ENVIRONMENT:
        raise ValueError("Pinecone API Key and Environment must be set in .env file.")

    pinecone_client = PineconeClient(api_key=PINECONE_API_KEY)

    if index_name in pinecone_client.list_indexes().names():
        return f"Index '{index_name}' already exists."

    print(f"Creating new index: '{index_name}'...")
    pinecone_client.create_index(
        name=index_name,
        dimension=768,  # Must match the embeddings model (all-mpnet-base-v2)
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region=PINECONE_ENVIRONMENT)
    )
    return f"Index '{index_name}' created successfully."


def list_pinecone_indexes():
    """Lists all available Pinecone indexes."""
    if not PINECONE_API_KEY:
        raise ValueError("Pinecone API Key must be set in .env file.")

    pinecone_client = PineconeClient(api_key=PINECONE_API_KEY)
    return pinecone_client.list_indexes().names()


# --- DELETE DB ---
def delete_pinecone_index(index_name: str):
    """
    Deletes a Pinecone index if it exists.
    """
    if not PINECONE_API_KEY:
        raise ValueError("Pinecone API Key must be set in .env file.")

    pinecone_client = PineconeClient(api_key=PINECONE_API_KEY)

    if index_name not in pinecone_client.list_indexes().names():
        return f"Index '{index_name}' not found.", 404

    try:
        pinecone_client.delete_index(name=index_name)
        return f"Index '{index_name}' deleted successfully.", 200
    except Exception as e:
        return f"An error occurred while deleting the index: {e}", 500
# --- END ---

