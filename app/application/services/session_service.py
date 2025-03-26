from application.ports.session_repository import SessionRepository
from domain.session import Session

class SessionService:
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    def verify_oauth_token(self, oauth_token: str):
        return True

    def get_user_id_by_token(self, oauth_token: str):
        return "1000001"

    def start_session(self, oauth_token: str) -> str:
        if not self.verify_oauth_token(oauth_token):
            return "FAILED_VARIFICATION"

        user_id = self.get_user_id_by_token(oauth_token)

        encrypted_session_id = self.session_repo.create_session_id(user_id)

        return encrypted_session_id

    def get_session(self, encrypted_session_id: str) -> Session:
        return self.session_repo.get_session(encrypted_session_id)