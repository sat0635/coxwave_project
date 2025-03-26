from abc import ABC, abstractmethod
from typing import List, Dict
from domain.session import Session


class SessionRepository(ABC):
    @abstractmethod
    def create_session_id(self, user_id: str) -> str:
        pass

    @abstractmethod
    def get_session(self, encryped_session_id: str) -> Session:
        pass
