from fastapi import APIRouter, Header
from fastapi.responses import StreamingResponse
from application.services.chat_service import ChatService
from application.services.session_service import SessionService
from pydantic import BaseModel

class SendMessageBody(BaseModel):
    content: str

router = APIRouter()
def get_chat_router(chat_service: ChatService, session_service: SessionService) -> APIRouter:
    router = APIRouter()

    @router.post("/message")
    def send_message(
        sendMessageBody: SendMessageBody,
        oauth_token: str = Header(..., alias="X-OAuth-Token"),
        encrypted_session_id: str = Header(..., alias="X-Session-Id")
    ):
        if not session_service.verify_oauth_token(oauth_token):
            return StreamingResponse((chunk for chunk in ["401 Unauthorized"]), media_type="text/plain")

        user_id = session_service.get_user_id_by_token(oauth_token)

        stream = chat_service.generate_reply(
            sendMessageBody.content,
            user_id,
            encrypted_session_id
        )

        return StreamingResponse(stream, media_type="text/plain")

    @router.get("/message/history")
    def fetch_history(
        oauth_token: str = Header(..., alias="X-OAuth-Token"),
        encrypted_session_id: str = Header(..., alias="X-Session-Id")
    ):
        return {}

    return router