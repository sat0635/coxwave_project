from core.config import settings
from fastapi import FastAPI
from adapters.inbound.api.session_router import get_session_router
from adapters.inbound.api.chat_router import get_chat_router
from application.services.session_service import SessionService
from application.services.chat_service import ChatService
from adapters.outbound.inmemory.session_repository import InMemorySessionRepository
from adapters.outbound.openai.embedding_repository import OpenaiEmbeddingRepository
from adapters.outbound.chroma.retriever_repository import ChromaRetrieverRepository
app = FastAPI()

session_repo = InMemorySessionRepository()
embedding_repo = OpenaiEmbeddingRepository(api_key=settings.openai_api_key, model=settings.embedding_model)
retriever_repo = ChromaRetrieverRepository()

session_service = SessionService(session_repo)
chat_service = ChatService(session_repo)

app.include_router(get_session_router(session_service))
app.include_router(get_chat_router(chat_service))
