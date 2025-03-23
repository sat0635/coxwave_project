from abc import ABC, abstractmethod
from typing import List

class LLMRepository(ABC):
    @abstractmethod
    def generate_reply(self, prompt: str) -> str:
        pass