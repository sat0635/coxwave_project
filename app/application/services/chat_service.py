from application.ports.session_repository import SessionRepository
from typing import Dict


class ChatService:
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    def send(self) -> str:
        return ""