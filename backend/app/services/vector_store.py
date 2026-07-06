import chromadb
from chromadb.config import Settings
import uuid

class VectorStore:
    def __init__(self, host="localhost", port=8000):
        self.client = chromadb.HttpClient(
            host=host, 
            port=port,
            settings=Settings(allow_reset=True, anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(name="documents")

    def add_chunks(self, document_id: str, chunks: list[dict]):
        """
        Add text chunks to the vector store.
        `chunks` should be a list of dicts like: {"id": str, "text": str, "metadata": dict}
        """
        if not chunks:
            return []
            
        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            chunk_id = chunk.get("id", str(uuid.uuid4()))
            ids.append(chunk_id)
            documents.append(chunk["text"])
            
            meta = chunk.get("metadata", {})
            meta["document_id"] = document_id
            metadatas.append(meta)
            
        # Batch insert to handle large PDFs and avoid payload limits
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size]
            )
        return ids

    def search_similar(self, query: str, document_id: str = None, n_results: int = 5):
        """
        Search for similar chunks in the vector store.
        """
        where = {"document_id": document_id} if document_id else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        if not results or not results["documents"] or not results["documents"][0]:
            return []
            
        # Format results
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
            })
            
        return formatted_results
