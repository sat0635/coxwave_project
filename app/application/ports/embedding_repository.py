from abc import ABC, abstractmethod
from typing import List

class EmbeddingRepository(ABC):
    @abstractmethod
    def text_to_vector(self, texts: List[str]) -> List[List[float]]:
        pass