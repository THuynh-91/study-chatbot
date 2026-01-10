import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import Optional

CHROMA_DB_PATH = Path("data/chroma_db")
COLLECTION_NAME = "document_chunks"

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

def get_or_create_collection():
     return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Document chunks for RAG system"}
    )

# Converts the text into embeddings
def generate_embedding(text: str) -> list[float]:
    embedding = embedding_model.encode(text)
    return embedding.tolist()

# Store chunks with embeddings in the DB
def store_chunks(chunks: list[dict]) -> None:
    collection = get_or_create_collection()
    
    for i, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk["text"])
        chunk_id = f"{chunk['metadata']['doc_id']}_{chunk['metadata']['page']}_{chunk['metadata']['chunk_index']}"
        
        collection.add(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[chunk["text"]],
            metadatas=[chunk["metadata"]]
        )
    
    print(f"Stored {len(chunks)} chunks in ChromaDB")

# Retrieve the most relevant chunks for a query
def retrieve_chunks(query: str, top_k: int = 5, filter_dict: Optional[dict] = None) -> list[dict]:
    collection = get_or_create_collection()
    query_embedding = generate_embedding(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=filter_dict
    )
    
    retrieved_chunks = []
    for i in range(len(results['ids'][0])):
        retrieved_chunks.append({
            "text": results['documents'][0][i],
            "metadata": results['metadatas'][0][i],
            "distance": results['distances'][0][i]
        })
    
    return retrieved_chunks

# Delete all chunks for a specific document
def delete_document_chunks(doc_id: str) -> None:
    collection = get_or_create_collection()
    collection.delete(where={"doc_id": doc_id})
    print(f"Deleted all chunks for doc_id: {doc_id}")

# Delete all chunks from the database (USE CAUTIOUSLY)
def clear_all_chunks() -> None:
    chroma_client.delete_collection(name=COLLECTION_NAME)
    print("Cleared all chunks from database")