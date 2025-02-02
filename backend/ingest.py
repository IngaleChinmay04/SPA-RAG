# backend/ingest.py
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FastEmbedEmbeddings
import os
from config import config

def create_collection_if_not_exists(client):
    collections = client.get_collections().collections
    if config.COLLECTION_NAME not in [col.name for col in collections]:
        client.create_collection(
            collection_name=config.COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.DOT)
        )
        print(f"Collection `{config.COLLECTION_NAME}` created successfully.")
    else:
        print(f"Collection `{config.COLLECTION_NAME}` already exists.")

def process_pdf(pdf_file, client, embeddings, text_splitter):
    try:
        pdf_file_path = os.path.join('data', pdf_file)
        docs = PyPDFLoader(file_path=pdf_file_path).load()
        chunks = text_splitter.split_documents(docs)
        vector_store = QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=config.COLLECTION_NAME,
            url=config.QDRANT_URL,
            api_key=config.QDRANT_API_KEY,
            force_recreate=True
        )
        print(f"Document {pdf_file} ingested successfully.")
    except Exception as e:
        print(f"Failed to process {pdf_file}: {e}")

def ingest():
    client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
    create_collection_if_not_exists(client)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=200)
    embeddings = FastEmbedEmbeddings()

    data_folder = "data"
    for pdf_file in os.listdir(data_folder):
        if pdf_file.endswith(".pdf"):
            process_pdf(pdf_file, client, embeddings, text_splitter)

if __name__ == "__main__":
    ingest()
