import json
from collections.abc import Generator

from openai import OpenAI

from app.application.ports.llm_repository import LLMRepository
from app.application.ports.message_repository import MessageRepository
from app.domain.constant.chat_role import ChatRole
from app.domain.constant.message_type import MessageType


class OpenaiLLMRepository(LLMRepository):
    def __init__(self, api_key: str, model: str, message_repo: MessageRepository):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.message_repo = message_repo

    def __convert_db_messages_to_llm_chat_messages(self, messages: list) -> list:
        message_type_role_map = {
            MessageType.SYSTEM: ChatRole.SYSTEM,
            MessageType.USER: ChatRole.USER,
            MessageType.ASSISTANT: ChatRole.ASSISTANT,
        }

        chat_messages = []
        for msg in messages:
            role = message_type_role_map.get(msg.message_type)
            if role is None:
                continue
            chat_messages.append({"role": role, "content": msg.content})

        return chat_messages

    def __make_related_qna_list(self, retrieved_docs: list):
        qna_list = []
        for retrieved_doc in retrieved_docs:
            metadata = retrieved_doc.get("metadata", {})
            score = retrieved_doc.get("score", 0)

            qna = json.dumps(
                {
                    "score": score,
                    "질문": metadata["original_question"],
                    "답변": metadata["answer"],
                    "주제": metadata["topics"],
                },
                ensure_ascii=False,
            )

            qna_list.append(qna)
        return qna_list

    def generate_reply(
        self,
        question: str,
        retrieved_docs: list,
        prev_messages: list,
        system_prompt: str,
    ) -> Generator[str, None, str]:
        messages = []

        if not prev_messages:
            messages = [{"role": ChatRole.SYSTEM, "content": system_prompt}]
        else:
            messages = self.__convert_db_messages_to_llm_chat_messages(prev_messages)

        messages.append(
            {
                "role": ChatRole.USER,
                "content": f"""
                "유저의 질문":"{question}"
                "유저의 질문과 관련있는 Q&A 리스트": {",".join(self.__make_related_qna_list(retrieved_docs))}
            """,
            }
        )

        response = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=0.2, stream=True
        )

        full_reply = ""
        for chunk in response:
            content = chunk.choices[0].delta.content if chunk.choices[0].delta else None
            if content:
                for char in content:
                    full_reply += char
                    yield char

        return full_reply
