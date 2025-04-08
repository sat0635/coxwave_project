from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header

from app.application.services.session_service import SessionService
from app.core.container import Container
from app.core.middleware import CommonRouter

router = APIRouter(route_class=CommonRouter)


@router.post("/session")
@inject
def start_session(
    oauth_token: str = Header(..., alias="X-OAuth-Token"),
    session_service: SessionService = Depends(Provide[Container.session_service]),
):
    user_id = session_service.get_user_id_by_token(oauth_token)
    return session_service.start_session(user_id)
