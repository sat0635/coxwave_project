from adapters.inbound.api.session_router import get_session_router
from adapters.inbound.api.chat_router import get_chat_router
from application.services.session_service import SessionService
from application.services.chat_service import ChatService
from adapters.outbound.inmemory.session_repository import InMemorySessionRepository
from adapters.outbound.inmemory.cache_repository import InMemoryCacheRepository
from adapters.outbound.inmemory.message_repository import InMemoryMessageRepository
from adapters.outbound.openai.embedding_repository import OpenaiEmbeddingRepository
from adapters.outbound.openai.llm_repository import OpenaiLLMRepository
from adapters.outbound.chroma.retriever_repository import ChromaRetrieverRepository

from core.config import settings
from fastapi import FastAPI

app = FastAPI()

# repo
session_repo = InMemorySessionRepository(settings.session_secret_key)
cache_repo = InMemoryCacheRepository()
message_repo = InMemoryMessageRepository()
embedding_repo = OpenaiEmbeddingRepository(api_key=settings.openai_api_key, model=settings.embedding_model)
retriever_repo = ChromaRetrieverRepository(embedding_repo, cache_repo)
llm_repo = OpenaiLLMRepository(api_key=settings.openai_api_key, model=settings.llm_model, message_repo=message_repo)

# service
session_service = SessionService(session_repo)
chat_service = ChatService(session_repo, llm_repo, retriever_repo, embedding_repo, message_repo, cache_repo)

retriever_repo.init_db("faq_answer_question_pair_with_categories_v4.jsonl")

app.include_router(get_session_router(session_service))
app.include_router(get_chat_router(chat_service, session_service))
