from fastapi import APIRouter, Response
from application.services.chat_service import ChatService

router = APIRouter()

def get_chat_router(service: ChatService) -> APIRouter:
    router = APIRouter()

    @router.post("/message")
    def send_message(response: Response):
        return {}

    @router.get("/message/history")
    def fetch_history(response: Response):
        return {}

    return router