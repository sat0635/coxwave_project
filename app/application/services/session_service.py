from app.application.ports.session_repository import SessionRepository


class SessionService:
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    def verify_oauth_token(self, oauth_token: str):
        return True

    def get_user_id_by_token(self, oauth_token: str):
        return "1000001"

    def start_session(self, user_id: str) -> str:
        encrypted_session_id = self.session_repo.create_session_id(user_id)

        return encrypted_session_id
