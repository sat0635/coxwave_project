from application.ports.cache_repository import CacheRepository
from domain.session import Session
import uuid
import os
import json

class InMemoryCacheRepository(CacheRepository):
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        embedding_cache_path = os.path.join(base_dir, "embedding_cache.jsonl")
        self.embedding_cache_path = embedding_cache_path
        self.embedding_cache = {}
        if not os.path.exists(embedding_cache_path):
            return

        with open(embedding_cache_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    chunk_embedding = json.loads(line)
                    self.embedding_cache.update(chunk_embedding)
                except json.JSONDecodeError:
                    continue

        return

    def get_embedding(self, key: str) -> any:
        if key in self.embedding_cache:
            return self.embedding_cache[key]
        
        return None

    def set_embedding(self, key: str, value: any):
        self.embedding_cache[key] = value
        with open(self.embedding_cache_path, "a", encoding="utf-8") as f:
            json.dump({chunk: embedding}, f)
            f.write("\n")
        return