from application.ports.llm_repository import LLMRepository
from typing import List
from openai import OpenAI

class OpenaiLLMRepository(LLMRepository):
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_reply(self, messages: List) -> str:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        return response["choices"][0]["message"]["content"]