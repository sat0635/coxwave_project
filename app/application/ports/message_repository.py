from abc import ABC, abstractmethod

from app.domain.message import Message


class MessageRepository(ABC):
    @abstractmethod
    def insert(self, message: Message):
        pass

    @abstractmethod
    def select_by_session(self, session_id: str) -> list[Message]:
        pass
