from abc import ABC, abstractmethod
from typing import List, Generator

class LLMRepository(ABC):
    @abstractmethod
    def generate_reply(self, question: str, retrieved_docs: List, prev_messages: List, system_prompt: str) -> Generator[str, None, str]:
        pass