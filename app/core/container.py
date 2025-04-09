from dependency_injector import containers, providers

from app.adapters.outbound.chroma.retriever_repository import ChromaRetrieverRepository
from app.adapters.outbound.inmemory.cache_repository import InMemoryCacheRepository
from app.adapters.outbound.inmemory.message_repository import InMemoryMessageRepository
from app.adapters.outbound.inmemory.session_repository import InMemorySessionRepository
from app.adapters.outbound.openai.embedding_repository import OpenaiEmbeddingRepository
from app.adapters.outbound.openai.llm_repository import OpenaiLLMRepository
from app.application.services.chat_service import ChatService
from app.application.services.session_service import SessionService
from app.core.config import settings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.adapters.inbound.api.chat_router",
            "app.adapters.inbound.api.session_router",
        ]
    )

    # Repository
    session_repo = providers.Singleton(
        InMemorySessionRepository, session_secret_key=settings.session_secret_key
    )
    cache_repo = providers.Singleton(InMemoryCacheRepository)
    message_repo = providers.Singleton(InMemoryMessageRepository)
    embedding_repo = providers.Singleton(
        OpenaiEmbeddingRepository,
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
    )
    retriever_repo = providers.Singleton(
        ChromaRetrieverRepository, embedding_repo=embedding_repo, cache_repo=cache_repo
    )
    llm_repo = providers.Singleton(
        OpenaiLLMRepository,
        api_key=settings.openai_api_key,
        model=settings.llm_model,
    )

    # Services
    session_service = providers.Singleton(SessionService, session_repo=session_repo)
    chat_service = providers.Singleton(
        ChatService,
        session_repo=session_repo,
        llm_repo=llm_repo,
        retriever_repo=retriever_repo,
        embedding_repo=embedding_repo,
        message_repo=message_repo,
        cache_repo=cache_repo,
    )
