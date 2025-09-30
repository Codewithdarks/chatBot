    # Ingest local TEXT (.txt) and MARKDOWN (.md) documents into Pinecone
    import os
    import argparse
    from typing import List, Set
    from langchain.text_splitter import (
        RecursiveCharacterTextSplitter,
        MarkdownHeaderTextSplitter,
    )
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_pinecone import Pinecone
    from langchain.schema import Document
    from dotenv import load_dotenv
    from pinecone import Pinecone as PineconeClient, PodSpec
    
    # --- Added a check for the unstructured library ---
    try:
        from langchain_community.document_loaders import (
            TextLoader,
            UnstructuredMarkdownLoader,
        )
    except ImportError:
        print("---")
        print("ERROR: The 'unstructured' library is not installed.")
        print("Please install it to process Markdown files by running:")
        print('pip install "unstructured[md]" python-magic-bin pypandoc')
        print("---")
        exit()  # Exit the script if the required loader is missing
    
    # Load environment variables
    load_dotenv()
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    
    # --- CONFIGURE YOUR DOCUMENT SOURCE ---
    DOCUMENTS_PATH = "./documents"
    
    # --- CONFIGURE THE DATABASE ---
    INDEX_NAME = os.getenv("ACTIVE_INDEX", "pyos-index")
    
    
    def get_existing_sources_from_pinecone(index_name: str) -> Set[str]:
        """Connects to Pinecone and fetches all unique 'source' metadata values."""
        print("Connecting to Pinecone to check for existing documents...")
        try:
            pc = PineconeClient(api_key=PINECONE_API_KEY)
            index = pc.Index(index_name)
    
            # This is a way to get all vector IDs. For very large indexes, this might be slow.
            # A common pattern is to query with a "match-all" filter if your index is organized by namespaces.
            # For this general-purpose script, we fetch a large number of vectors to get their metadata.
            response = index.query(
                vector=[0] * 768,  # A dummy vector of the correct dimension
                top_k=10000,  # Fetch up to 10,000 vectors
                include_metadata=True
            )
    
            existing_sources = set()
            for match in response['matches']:
                if 'source' in match['metadata']:
                    existing_sources.add(match['metadata']['source'])
    
            print(f"Found {len(existing_sources)} existing sources in the index.")
            return existing_sources
        except Exception as e:
            print(f"Pinecone index '{index_name}' not found or another error occurred: {e}")
            print("Assuming no existing documents. Will create the index if it doesn't exist.")
            return set()
    
    
    def get_local_filepaths(directory_path: str) -> List[str]:
        """Gets a list of all .txt and .md file paths in the directory."""
        all_files = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith((".md", ".txt")):
                    all_files.append(os.path.join(root, file))
        return all_files
    
    
    def load_specific_documents(file_paths: List[str]) -> List[Document]:
        """Loads only the documents from the provided list of file paths."""
        print(f"Loading {len(file_paths)} new documents...")
        documents = []
    
        for file_path in file_paths:
            try:
                if file_path.endswith(".md"):
                    loader = UnstructuredMarkdownLoader(file_path)
                else:
                    loader = TextLoader(file_path)
                documents.extend(loader.load())
            except Exception as e:
                print(f"Error loading document {file_path}: {e}")
                continue
    
        # Filter out any loaded documents that are empty
        non_empty_docs = [d for d in documents if getattr(d, "page_content", "").strip()]
        empty_count = len(documents) - len(non_empty_docs)
        if empty_count > 0:
            print(f"Filtered out {empty_count} empty or failed-to-load documents.")
    
        return non_empty_docs
    
    
    def main():
        """Load, split, embed and upsert documents into Pinecone."""
        if not PINECONE_API_KEY:
            print("ERROR: PINECONE_API_KEY is not set. Add it to your .env file.")
            return
    
        # 1. Get existing file sources from Pinecone and local directory
        existing_sources = get_existing_sources_from_pinecone(INDEX_NAME)
        all_local_files = get_local_filepaths(DOCUMENTS_PATH)
    
        # 2. Determine which files are new and need to be uploaded
        new_files_to_upload = [
            fp for fp in all_local_files if fp not in existing_sources
        ]
    
        skipped_files_count = len(all_local_files) - len(new_files_to_upload)
        if skipped_files_count > 0:
            print(f"\nSkipping {skipped_files_count} files that are already in the database.")
    
        if not new_files_to_upload:
            print("No new documents to upload. All local files are already in the database.")
            print("--- Ingestion Complete ---")
            return
    
        # 3. Load only the new documents
        docs = load_specific_documents(new_files_to_upload)
        if not docs:
            print("No new documents were loaded successfully; exiting ingestion.")
            return
    
        # 4. Split documents into chunks
        print("\nSplitting new documents into chunks...")
        md_docs = [doc for doc in docs if doc.metadata.get("source", "").endswith(".md")]
        txt_docs = [doc for doc in docs if doc.metadata.get("source", "").endswith(".txt")]
        chunks = []
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    
        if md_docs:
            headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3"), ("####", "Header 4")]
            markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
            for doc in md_docs:
                header_splits = markdown_splitter.split_text(doc.page_content)
                splits = text_splitter.split_documents(header_splits)
                chunks.extend(splits)
        if txt_docs:
            chunks.extend(text_splitter.split_documents(txt_docs))
    
        print(f"Total chunks created from new files: {len(chunks)}.")
        if not chunks:
            print("No chunks created from documents; exiting ingestion.")
            return
    
        # 5. Initialize embedding model
        print("Initializing embedding model...")
        model_name = "sentence-transformers/all-mpnet-base-v2"
        embeddings = HuggingFaceEmbeddings(model_name=model_name)
    
        # 6. Add documents to Pinecone index
        print(f"Adding documents to Pinecone index '{INDEX_NAME}'...")
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i: i + batch_size]
            print(f"Processing batch {i // batch_size + 1}/{(len(chunks) + batch_size - 1) // batch_size}...")
            Pinecone.from_documents(batch, embeddings, index_name=INDEX_NAME)
    
        source_files = sorted(list({
            chunk.metadata.get("source") for chunk in chunks if chunk.metadata.get("source")
        }))
    
        print("\nDocuments added to Pinecone successfully.")
        if source_files:
            print(f"\n--- Uploaded {len(source_files)} New File(s) ---")
            for file_path in source_files:
                file_name = os.path.basename(file_path)
                print(f"  - {file_name}")
            print("------------------------")
    
        print("\n--- Ingestion Complete ---")
    
    
    if __name__ == "__main__":
        main()
    
