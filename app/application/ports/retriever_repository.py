from abc import ABC, abstractmethod
from typing import Any


class RetrieverRepository(ABC):
    @abstractmethod
    def init_db(self, file_name: str) -> None:
        pass

    @abstractmethod
    def search(self, query_vector: list[float], top_k: int) -> list[dict[str, Any]]:
        pass
