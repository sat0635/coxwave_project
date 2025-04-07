from abc import ABC, abstractmethod


class CacheRepository(ABC):
    @abstractmethod
    def get_embedding(self, key: str) -> any:
        pass

    @abstractmethod
    def set_embedding(self, key: str, value: any):
        pass

    @abstractmethod
    def lock_session_message(self, session_id: str):
        pass

    @abstractmethod
    def unlock_session_message(self, session_id: str):
        pass

    @abstractmethod
    def is_session_message_locked(self, session_id: str) -> bool:
        pass