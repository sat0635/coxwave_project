from application.ports.session_repository import SessionRepository
from domain.session import Session
from typing import Dict


class SessionService:
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    def start_new_session(self) -> str:
        return self.session_repo.create_session()

    def delete_session(self, session_id: str) -> None:
        self.session_repo.delete_session(session_id)