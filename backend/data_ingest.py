import os
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from langchain_pinecone import Pinecone as LangChainPinecone
from langchain_huggingface import HuggingFaceEmbeddings

# Initialize embeddings model once to be reused across the application
embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


def process_and_embed_document(file_path: str, index_name: str):
    """
    Loads a document, splits it into chunks, creates embeddings,
    and upserts them into the specified Pinecone index.
    Returns a tuple of (message, status_code).
    """
    print(f"Processing file for index '{index_name}': {file_path}")
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load()

    # Split documents into chunks using appropriate strategies
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "H1"), ("##", "H2")])

    chunks = []
    for doc in docs:
        if file_path.endswith(".md"):
            header_splits = md_splitter.split_text(doc.page_content)
            splits = text_splitter.split_documents(header_splits)
            chunks.extend(splits)
        else:
            chunks.extend(text_splitter.split_documents([doc]))

    if not chunks:
        message = f"Warning: No text chunks were generated from {os.path.basename(file_path)}."
        print(message)
        return message, 400

    print(f"Generated {len(chunks)} chunks. Embedding and uploading to '{index_name}'...")
    LangChainPinecone.from_documents(chunks, embeddings_model, index_name=index_name)

    success_message = f"Successfully ingested file '{os.path.basename(file_path)}' into index '{index_name}'."
    print(success_message)
    return success_message, 200
