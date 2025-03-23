from abc import ABC, abstractmethod
from typing import List, Any, Dict

class RetrieverRepository(ABC):
    @abstractmethod
    def add(self, ids: List[str], vectors: List[List[float]], metadatas: List[Dict[str, Any]]) -> None:
        pass