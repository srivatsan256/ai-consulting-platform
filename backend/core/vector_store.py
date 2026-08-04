import chromadb

_client = None
_collection = None

CHROMA_PERSIST_DIR = "chroma_data"
COLLECTION_NAME = "knowledge_base"


def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
        )
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_document(
    doc_id: str,
    text: str,
    metadata: dict = None,
):
    collection = get_collection()
    collection.upsert(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata or {}],
    )


def search_documents(query: str, n_results: int = 5) -> list:
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )
    output = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            item = {"document": doc, "id": results["ids"][0][i]}
            if results["metadatas"] and results["metadatas"][0]:
                item["metadata"] = results["metadatas"][0][i]
            if results["distances"] and results["distances"][0]:
                item["score"] = 1 - results["distances"][0][i]
            output.append(item)
    return output


def delete_document(doc_id: str):
    collection = get_collection()
    collection.delete(ids=[doc_id])


def get_all_documents() -> list:
    collection = get_collection()
    return collection.get()
