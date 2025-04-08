from abc import ABC, abstractmethod

from pydantic import BaseModel


class StructuredReplyResponse(BaseModel):
    answer: str
    lead_questions: list[str]


class LLMRepository(ABC):
    @abstractmethod
    def generate_reply(
        self,
        question: str,
        retrieved_docs: list,
        prev_messages: list,
        system_prompt: str,
    ) -> StructuredReplyResponse:
        pass
