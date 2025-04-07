from abc import ABC, abstractmethod
from collections.abc import Generator


class LLMRepository(ABC):
    @abstractmethod
    def generate_reply(self, question: str, retrieved_docs: list, prev_messages: list, system_prompt: str) -> Generator[str, None, str]:
        pass