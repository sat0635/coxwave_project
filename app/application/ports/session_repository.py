from abc import ABC, abstractmethod
from typing import List, Dict
from domain.session import Session


class SessionRepository(ABC):
    @abstractmethod
    def create_session(self) -> str:
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Session:
        pass

    @abstractmethod
    def save_session(self, session: Session) -> None:
        pass

    @abstractmethod
    def delete_session(self, session: Session) -> None:
        pass