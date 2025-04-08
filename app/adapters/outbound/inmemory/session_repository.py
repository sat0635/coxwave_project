import base64
import hashlib
import time
import uuid

from cryptography.fernet import Fernet

from app.application.ports.session_repository import SessionRepository
from app.domain.session import Session


class InMemorySessionRepository(SessionRepository):
    def __init__(self, session_secret_key: str):
        self.sessions = {}
        self.session_secret_key = session_secret_key
        self.fernet = Fernet(
            base64.urlsafe_b64encode(
                hashlib.sha256(self.session_secret_key.encode()).digest()
            )
        )

    def create_session_id(self, user_id: str) -> str:
        timestamp_ms = int(time.time() * 1000)
        unique_id = uuid.uuid4().hex

        session_id = f"{timestamp_ms}_{unique_id}"

        self.sessions[session_id] = Session(session_id=session_id, user_id=user_id)
        encrypted_session_id = self.fernet.encrypt(session_id.encode()).decode()
        return encrypted_session_id

    def get_session(self, encryped_session_id: str) -> Session:
        session_id = self.fernet.decrypt(encryped_session_id).decode()
        return self.sessions[session_id]
