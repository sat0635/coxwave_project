from app.domain.message import Message

from abc import ABC, abstractmethod
from typing import List

class MessageRepository(ABC):
    @abstractmethod
    def insert(self, message: Message):
        pass

    @abstractmethod
    def select_by_session(self, session_id: str) -> List[Message]:
        pass
