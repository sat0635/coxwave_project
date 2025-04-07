from fastapi import APIRouter, Header

from app.application.services.session_service import SessionService

router = APIRouter()

def get_session_router(session_service: SessionService) -> APIRouter:
    router = APIRouter()

    @router.post("/session")
    def start_session(oauth_token: str = Header(..., alias="X-OAuth-Token")):
        return session_service.start_session(oauth_token)

    return router