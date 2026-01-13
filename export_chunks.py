from utils.chunking.chunk_storage import get_or_create_collection

# Get the collection
collection = get_or_create_collection()

# Get collection stats
print(f"Total chunks in database: {collection.count()}")
print()

# Peek at all chunks (or first 10)
results = collection.get(limit=10)

for i, (doc_id, text, metadata) in enumerate(zip(
    results['ids'],
    results['documents'], 
    results['metadatas']
)):
    print(f"--- Chunk {i+1} ---")
    print(f"ID: {doc_id}")
    print(f"Source: {metadata.get('source_file', 'N/A')}")
    print(f"Page: {metadata.get('page', 'N/A')}")
    print(f"Type: {metadata.get('chunk_type', 'N/A')}")
    print(f"Text preview: {text[:200]}...")
    print()
