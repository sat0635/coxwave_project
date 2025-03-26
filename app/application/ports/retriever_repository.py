from abc import ABC, abstractmethod
from typing import List, Any, Dict

class RetrieverRepository(ABC):
    @abstractmethod
    def init_db(self, file_name: str) -> None:
        pass

    @abstractmethod
    def search(self, query_vector: List[float], top_k: int) -> List[Dict[str, Any]]:
        pass