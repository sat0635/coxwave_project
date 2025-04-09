from unittest.mock import MagicMock

import pytest
from openai import OpenAIError

from app.adapters.outbound.openai.llm_repository import OpenaiLLMRepository
from app.application.ports.llm_repository import StructuredReplyResponse


def build_openai_repo_with_mocks(parse_response=None, raise_exception=False):
    mock_client = MagicMock()

    if raise_exception:
        mock_client.beta.chat.completions.parse.side_effect = OpenAIError(
            "API call failed"
        )
    else:
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=parse_response
                    or '{"answer": "answer", "lead_questions": ["Q1", "Q2"]}'
                )
            )
        ]
        mock_client.beta.chat.completions.parse.return_value = mock_response

    repo = OpenaiLLMRepository(api_key="dummy", model="gpt-4o-mini")
    repo.client = mock_client
    return repo, mock_client


def test_generate_reply_happy():
    repo, mock_client = build_openai_repo_with_mocks()

    question = "question"
    retrieved_docs = [
        {
            "score": 0.95,
            "metadata": {
                "original_question": "original_question",
                "answer": "answer",
                "topics": ["topic1", "topic2"],
            },
        }
    ]
    prev_messages = []
    system_prompt = "system_prompt"

    response = repo.generate_reply(
        question=question,
        retrieved_docs=retrieved_docs,
        prev_messages=prev_messages,
        system_prompt=system_prompt,
    )

    # then
    assert isinstance(response, StructuredReplyResponse)
    assert response.answer == "answer"
    assert response.lead_questions == ["Q1", "Q2"]
    mock_client.beta.chat.completions.parse.assert_called_once()


def test_generate_reply_raises_exception():
    repo, _ = build_openai_repo_with_mocks(raise_exception=True)

    with pytest.raises(OpenAIError) as exc_info:
        repo.generate_reply(
            question="question",
            retrieved_docs=[],
            prev_messages=[],
            system_prompt="system_prompt",
        )

    assert "API call failed" in str(exc_info.value)
