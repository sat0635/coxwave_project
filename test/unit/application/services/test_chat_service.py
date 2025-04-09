from unittest.mock import Mock

import pytest

from app.application.ports.llm_repository import StructuredReplyResponse
from app.core.container import Container
from app.domain.exception import ServerException
from app.domain.message import Message
from app.domain.session import Session


def build_mocked_container(
    session: Session = None,
    llm_response: StructuredReplyResponse = None,
    is_locked: bool = False,
    prev_messages=None,
):
    container = Container()

    session = session or Session(session_id="s1", user_id="u1")
    llm_response = llm_response or StructuredReplyResponse(
        answer="answer", lead_questions=["Q1", "Q2"]
    )
    prev_messages = prev_messages or []

    mocks = {
        "session_repo": Mock(),
        "llm_repo": Mock(),
        "retriever_repo": Mock(),
        "embedding_repo": Mock(),
        "message_repo": Mock(),
        "cache_repo": Mock(),
    }

    mocks["session_repo"].get_session.return_value = session
    mocks["cache_repo"].is_session_message_locked.return_value = is_locked
    mocks["embedding_repo"].text_to_vector.return_value = [0.1, 0.2, 0.3]
    mocks["retriever_repo"].search.return_value = [{"score": 0.1, "metadata": {}}]
    mocks["message_repo"].select_by_session.return_value = prev_messages
    mocks["llm_repo"].generate_reply.return_value = llm_response

    container.session_repo.override(mocks["session_repo"])
    container.llm_repo.override(mocks["llm_repo"])
    container.retriever_repo.override(mocks["retriever_repo"])
    container.embedding_repo.override(mocks["embedding_repo"])
    container.message_repo.override(mocks["message_repo"])
    container.cache_repo.override(mocks["cache_repo"])

    return container, mocks


def test_generate_reply_happy():
    container, mocks = build_mocked_container()
    service = container.chat_service()
    result = service.generate_reply(
        "question",
        user_id="u1",
        encrypted_session_id="encrypted_session_id",
    )
    assert result == StructuredReplyResponse(
        answer="answer", lead_questions=["Q1", "Q2"]
    )

    cache_repo = mocks["cache_repo"]
    cache_repo.is_session_message_locked.assert_called_once()
    cache_repo.lock_session_message.assert_called_once()
    cache_repo.unlock_session_message.assert_called_once()

    message_repo = mocks["message_repo"]
    assert message_repo.insert.call_count == 3


def test_generate_reply_prev_messages():
    container, mocks = build_mocked_container()
    service = container.chat_service()
    mocks["message_repo"].select_by_session.return_value = [
        Message(session_id="s1", writer_id="u1", message_type=1, content="prev message")
    ]

    result = service.generate_reply(
        "question",
        user_id="u1",
        encrypted_session_id="encrypted_session_id",
    )
    assert result == StructuredReplyResponse(
        answer="answer", lead_questions=["Q1", "Q2"]
    )

    cache_repo = mocks["cache_repo"]
    cache_repo.is_session_message_locked.assert_called_once()
    cache_repo.lock_session_message.assert_called_once()
    cache_repo.unlock_session_message.assert_called_once()

    message_repo = mocks["message_repo"]
    assert message_repo.insert.call_count == 2


def test_generate_reply_locked_session():
    container, mocks = build_mocked_container()
    service = container.chat_service()
    mocks["cache_repo"].is_session_message_locked.return_value = True

    with pytest.raises(ServerException) as exc_info:
        service.generate_reply(
            "question",
            user_id="u1",
            encrypted_session_id="encrypted_session_id",
        )

    assert exc_info.value.user_message == "IN_PROGRESS"
    assert exc_info.value.http_code == 409

    cache_repo = mocks["cache_repo"]
    cache_repo.is_session_message_locked.assert_called_once()
    cache_repo.lock_session_message.assert_not_called()

    message_repo = mocks["message_repo"]
    assert message_repo.insert.call_count == 0
