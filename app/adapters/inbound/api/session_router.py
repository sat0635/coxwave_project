from fastapi import APIRouter, Response
from application.services.session_service import SessionService

router = APIRouter()

def get_session_router(service: SessionService) -> APIRouter:
    router = APIRouter()

    @router.post("/session")
    def create_session(response: Response):
        return {"session_id": "new_session_id"}

    @router.get("/session/{id}")
    def get_session(id: str, response: Response):
        return {"session_id": id}

    @router.delete("/session/{id}")
    def close_session(id: str, response: Response):
        return {"session_id": id}

    return router