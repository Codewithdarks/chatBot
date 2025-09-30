import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

# --- CONFIGURE THE INDEX ---
INDEX_NAME = "pyos-index"
# ---------------------------

def main():
    """One-time script to create or confirm a Pinecone index."""
    if not PINECONE_API_KEY:
        raise RuntimeError("PINECONE_API_KEY is not set. Please add it to backend/.env")
    if not PINECONE_ENVIRONMENT:
        raise RuntimeError("PINECONE_ENVIRONMENT (region, e.g., us-east-1) is not set in backend/.env")

    print("Initializing Pinecone client...")
    # Initialize the Pinecone client
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Check if the index already exists
    if INDEX_NAME in pc.list_indexes().names():
        print(f"Index '{INDEX_NAME}' already exists. No action taken.")
        return

    # Create a new index if it doesn't exist
    print(f"Creating index '{INDEX_NAME}'...")

    # Create the index with Serverless specification
    pc.create_index(
        name=INDEX_NAME,
        dimension=768,  # IMPORTANT: Must match your embedding model
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region=PINECONE_ENVIRONMENT  # Use the environment/region from your .env file
        )
    )

    print("Index created successfully.")
    print("--- Pinecone Setup Complete ---")

if __name__ == "__main__":
    main()