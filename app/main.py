from fastapi import FastAPI

from app.adapters.inbound.api.chat_router import router as chat_router
from app.adapters.inbound.api.session_router import router as session_router
from app.core.container import Container

app = FastAPI()

container = Container()
container.init_resources()

container.retriever_repo().init_db("faq_answer_question_pair_with_categories_v4.jsonl")

app = FastAPI()
app.container = container

app.include_router(chat_router)
app.include_router(session_router)
