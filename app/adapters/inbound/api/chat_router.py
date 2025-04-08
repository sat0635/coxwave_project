import time

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.application.services.chat_service import ChatService
from app.application.services.session_service import SessionService
from app.core.container import Container
from app.core.middleware import CommonRouter

router = APIRouter(route_class=CommonRouter)


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
) -> StreamingResponse:
    user_id = session_service.get_user_id_by_token(oauth_token)

    structured_reply_response = chat_service.generate_reply(
        send_message_body.content, user_id, encrypted_session_id
    )

    answer = structured_reply_response.answer
    lead_questions = structured_reply_response.lead_questions

    def stream_chunks(answer: str, lead_questions: list):
        for char in answer:
            yield char
            time.sleep(0.03)
        yield "\n"
        time.sleep(0.1)
        for lead_question in lead_questions:
            for char in lead_question:
                yield char
                time.sleep(0.03)
            yield "\n"

    return StreamingResponse(
        stream_chunks(answer, lead_questions), media_type="text/plain"
    )


@router.get("/message/history")
def fetch_history(
    oauth_token: str = Header(..., alias="X-OAuth-Token"),
    encrypted_session_id: str = Header(..., alias="X-Session-Id"),
):
    return {}
