from application.ports.session_repository import SessionRepository
from domain.session import Session
import uuid

class InMemorySessionRepository(SessionRepository):
    def __init__(self):
        self.sessions = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = Session(session_id=session_id)
        return session_id

    def get_session(self, session_id: str) -> Session:
        return self.sessions.get(session_id)

    def save_session(self, session: Session) -> None:
        self.sessions[session.session_id] = session

    def delete_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            del self.sessions[session_id]