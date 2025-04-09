from fastapi.testclient import TestClient

from app.application.ports.llm_repository import StructuredReplyResponse
from app.core.container import Container
from app.main import app


class MockSessionService:
    def get_user_id_by_token(self, token: str) -> str:
        return "user123"


class MockChatService:
    def generate_reply(
        self, message: str, user_id: str, session_id: str
    ) -> StructuredReplyResponse:
        return StructuredReplyResponse(
            answer="answer", lead_questions=["lead_question1", "lead_question2"]
        )


def test_send_message_happy():
    container = Container()
    container.chat_service.override(MockChatService())
    container.session_service.override(MockSessionService())

    with TestClient(app) as client:
        response = client.post(
            "/message",
            headers={"X-OAuth-Token": "token", "X-Session-Id": "session"},
            json={"content": "question"},
        )

    assert response.status_code == 200
    assert "answer" in response.text
    assert "lead_question1" in response.text
    assert "lead_question2" in response.text


def test_send_message_empty_header():
    container = Container()
    container.chat_service.override(MockChatService())
    container.session_service.override(MockSessionService())

    with TestClient(app) as client:
        response = client.post(
            "/message",
            # headers={"X-OAuth-Token": "token", "X-Session-Id": "session"},
            json={"content": "question"},
        )

    assert response.status_code == 401
    assert response.text == '{"message":"UNAUTHORIZED"}'
