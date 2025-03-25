from abc import ABC, abstractmethod
from typing import List, Dict
from domain.session import Session


class CacheRepository(ABC):
    @abstractmethod
    def get_embedding(self, key: str) -> any:
        pass

    @abstractmethod
    def set_embedding(self, key: str, value: any):
        pass