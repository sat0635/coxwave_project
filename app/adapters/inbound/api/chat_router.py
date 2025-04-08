from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.application.services.chat_service import ChatService
from app.application.services.session_service import SessionService
from app.core.container import Container

router = APIRouter()


class SendMessageBody(BaseModel):
    content: str


@router.post("/message")
@inject
def send_message(
    send_message_body: SendMessageBody,
    oauth_token: str = Header(..., alias="X-OAuth-Token"),
    encrypted_session_id: str = Header(..., alias="X-Session-Id"),
    chat_service: ChatService = Depends(Provide[Container.chat_service]),
    session_service: SessionService = Depends(Provide[Container.session_service]),
):
    if not session_service.verify_oauth_token(oauth_token):
        return StreamingResponse(
            (chunk for chunk in ["401 Unauthorized"]), media_type="text/plain"
        )

    user_id = session_service.get_user_id_by_token(oauth_token)

    stream = chat_service.generate_reply(
        send_message_body.content, user_id, encrypted_session_id
    )

    return StreamingResponse(stream, media_type="text/plain")


@router.get("/message/history")
def fetch_history(
    oauth_token: str = Header(..., alias="X-OAuth-Token"),
    encrypted_session_id: str = Header(..., alias="X-Session-Id"),
):
    return {}
