
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header

from app.application.services.session_service import SessionService
from app.core.container import Container

router = APIRouter()

@router.post("/session")
@inject
def start_session(oauth_token: str = Header(..., alias="X-OAuth-Token"),
    session_service: SessionService = Depends(Provide[Container.session_service])
):
    return session_service.start_session(oauth_token)
