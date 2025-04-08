import json
import os

from app.application.ports.cache_repository import CacheRepository


class InMemoryCacheRepository(CacheRepository):
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        self.embedding_cache_path = os.path.join(base_dir, "embedding_cache_v3.jsonl")
        self.embedding_cache = {}
        self.message_lock_cache = {}
        if not os.path.exists(self.embedding_cache_path):
            return

        with open(self.embedding_cache_path, encoding="utf-8", errors="ignore") as f:
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

        return

    def save_embedding_cache_to_file(self):
        with open(self.embedding_cache_path, "w", encoding="utf-8") as f:
            for key, value in self.embedding_cache.items():
                json.dump({key: value}, f, ensure_ascii=False)
                f.write("\n")

        return

    def lock_session_message(self, session_id: str):
        self.message_lock_cache[session_id] = True

    def unlock_session_message(self, session_id: str):
        self.message_lock_cache[session_id] = False

    def is_session_message_locked(self, session_id: str) -> bool:
        if session_id in self.message_lock_cache:
            return self.message_lock_cache[session_id]

        return False
