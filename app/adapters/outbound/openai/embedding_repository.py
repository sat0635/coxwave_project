from openai import OpenAI

from app.application.ports.embedding_repository import EmbeddingRepository


class OpenaiEmbeddingRepository(EmbeddingRepository):
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def text_to_vector(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]
