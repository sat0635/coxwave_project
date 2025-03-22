from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from chromadb.api.types import Documents, Embeddings, Metadatas, IDs

from application.ports.retriever_repository import RetrieverRepository

class ChromaRetrieverRepository(RetrieverRepository):
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("faq")

    def add(self, ids: List[str], vectors: List[List[float]], metadatas: List[Dict[str, Any]]) -> None:
        documents = [metadata.get("text", "") for metadata in metadatas]
        self.collection.add(
            ids=ids,
            embeddings=vectors,
            metadatas=metadatas,
            documents=documents
        )
