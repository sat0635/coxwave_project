import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from kiwipiepy import Kiwi

from app.application.ports.cache_repository import CacheRepository
from app.application.ports.embedding_repository import EmbeddingRepository
from app.application.ports.retriever_repository import RetrieverRepository


class ChromaRetrieverRepository(RetrieverRepository):
    def __init__(
        self, embedding_repo: EmbeddingRepository, cache_repo: CacheRepository
    ):
        self.client = chromadb.PersistentClient(
            path=os.path.join(os.path.dirname(__file__), "chroma_db_chunk_v3")
        )
        self.embedding_repo = embedding_repo
        self.cache_repo = cache_repo

    def __split_sentences(self, text):
        kiwi = Kiwi()
        sentences = kiwi.split_into_sents(text)

        return [s.text for s in sentences]

    def __create_sentence_chunks(self, sentences, window_size=3, overlap=1):
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

    def __clean_text(self, text: str) -> str:
        """
        Remove special characters and invisible unicode symbols from the text.
        Keeps Korean, English, digits, and whitespace only.
        """

        # Replace non-breaking space (\xa0) with normal space
        text = text.replace("\xa0", " ")

        # Remove common special characters (except letters, digits, and whitespace)
        text = re.sub(r"[^\w\s가-힣]", "", text)

        # Remove invisible unicode characters like \ufeff, \u200b, etc.
        text = re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]", "", text)

        return text.strip()

    def __generate_and_insert_vectors(
        self,
        collection: Collection,
        target_text: str,
        answer: str,
        question: str,
        categories: list,
        id: str,
    ):
        # split sentent and make overlapped chunk
        sentences = self.__split_sentences(self.__clean_text(target_text))
        chunks = []
        if len(sentences) >= 3:
            chunks = self.__create_sentence_chunks(sentences, window_size=2, overlap=1)
        elif len(sentences) == 2:
            chunks = [" ".join(sentences)]
        else:
            chunks = sentences

        new_chunks = [
            chunk for chunk in chunks if self.cache_repo.get_embedding(chunk) is None
        ]

        if new_chunks:
            new_embeddings = self.embedding_repo.text_to_vector(new_chunks)
            for chunk, embedding in zip(new_chunks, new_embeddings, strict=False):
                self.cache_repo.set_embedding(chunk, embedding)

        metadata = [
            {
                "answer": answer,
                "original_question": question,
                "topics": ", ".join(categories),
            }
        ] * len(chunks)

        ids = [f"{id}_{i}" for i in range(len(chunks))]

        embeddings = [self.cache_repo.get_embedding(chunk) for chunk in chunks]

        collection.add(
            documents=chunks, embeddings=embeddings, metadatas=metadata, ids=ids
        )

        return

    def __process_line(self, collection: Collection, line: str, idx: int):
        data = json.loads(line)
        question = data.get("question")
        answer = data.get("answer")
        categories = data.get("categories", [])

        self.__generate_and_insert_vectors(
            collection, question, answer, question, categories, f"question_{idx}"
        )
        self.__generate_and_insert_vectors(
            collection, answer, answer, question, categories, f"answer_{idx}"
        )

    def __process_file(self, file_path: str, collection: Collection):
        futures = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            with open(file_path, encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    future = executor.submit(self.__process_line, collection, line, idx)
                    futures.append(future)

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error occurred: {e}")

    def init_db(self, file_name: str) -> None:
        # if collection exist, do skip
        existing_collections = self.client.list_collections()
        if existing_collections:
            print("chromadb already initialized. Skipping.")
            return

        collection_name = "naver_smart_store_qna"
        collection = self.client.get_or_create_collection(name=collection_name)

        print("chromadb init start")

        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, file_name)

        self.__process_file(file_path, collection)

        # save cache data to file
        self.cache_repo.save_embedding_cache_to_file()

        print("✅ chromadb init done")

    def search(self, query_vector: list[float], top_k: int = 20) -> list[dict[str, Any]]:
        collection = self.client.get_collection(name="naver_smart_store_qna")
        result = collection.query(query_embeddings=query_vector, n_results=top_k)

        results = []
        for i in range(len(result["documents"][0])):
            results.append(
                {
                    "document": result["documents"][0][i],
                    "metadata": result["metadatas"][0][i],
                    "score": result["distances"][0][i],
                }
            )

        return results
