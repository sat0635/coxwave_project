from typing import List, Dict, Any
import chromadb
import os
import json
from kiwipiepy import Kiwi
from chromadb.config import Settings
from chromadb.api.types import Documents, Embeddings, Metadatas, IDs

from application.ports.retriever_repository import RetrieverRepository
from application.ports.embedding_repository import EmbeddingRepository
from application.ports.cache_repository import CacheRepository

class ChromaRetrieverRepository(RetrieverRepository):
    def __init__(self, embedding_repo: EmbeddingRepository, cache_repo: CacheRepository):
        self.client = chromadb.PersistentClient(path=os.path.join(os.path.dirname(__file__), "chroma_db_chunck"))
        self.embedding_repo = embedding_repo
        self.cache_repo = cache_repo

    def _split_sentences(self, text):
        kiwi = Kiwi()
        sentences = kiwi.split_into_sents(text)

        return [s.text for s in sentences]

    def _create_sentence_chunks(self, sentences, window_size=3, overlap=1):
        chunks = []
        start = 0
        step = window_size - overlap

        while start < len(sentences):
            end = min(start + window_size, len(sentences))
            chunk = " ".join(sentences[start:end])
            chunks.append(chunk)
            if end == len(sentences):
                break
            start += step

        return chunks

    def init_db(self, file_name: str) -> None:
        # if collection exist, do skip
        existing_collections = self.client.list_collections()
        if existing_collections:
            print("chromadb already initialized. Skipping.")
            return

        collection_name = f"naver_smart_store_qna"
        collection = self.client.get_or_create_collection(name=collection_name)

        print("chromadb init start")

        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):

                data = json.loads(line)
                question = data.get("question")
                answer = data.get("answer")
                categories = data.get("categories", [])

                # split sentent and make overlapped chunk
                sentences = self._split_sentences(question)
                chunks = []
                if len(sentences) >= 3:
                    chunks = self._create_sentence_chunks(sentences, window_size=2, overlap=1)
                elif len(sentences) == 2:
                    chunks = [' '.join(sentences)]
                else:
                    chunks = sentences

                new_chunks = [chunk for chunk in chunks if self.cache_repo.get_embedding(chunk) is None]
                print(new_chunks)
                if new_chunks:
                    new_embeddings = self.embedding_repo.text_to_vector(new_chunks)
                    for chunk, embedding in zip(new_chunks, new_embeddings):
                        self.cache_repo.set_embedding(chunk, embedding)

                for i, chunk in enumerate(chunks):
                    collection.add(
                        documents=[chunk],
                        embeddings=self.cache_repo.get_embedding(chunk),
                        metadatas=[{
                            "answer": answer,
                            "original_question": question,
                            "topics": ", ".join(categories)
                        }],
                        ids=[f"{idx}_{i}"]
                    )

        print("✅ chromadb init done")

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        collection = self.client.get_collection(name="naver_smart_store_qna")
        result = collection.query(
            query_embeddings=query_vector,
            n_results=top_k
        )
        
        results = []
        for i in range(len(result["documents"][0])):
            results.append({
                "document": result["documents"][0][i],
                "metadata": result["metadatas"][0][i],
                "score": result["distances"][0][i],
            })

        return results