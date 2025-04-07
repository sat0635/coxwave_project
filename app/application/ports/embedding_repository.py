from abc import ABC, abstractmethod


class EmbeddingRepository(ABC):
    @abstractmethod
    def text_to_vector(self, texts: list[str]) -> list[list[float]]:
        pass