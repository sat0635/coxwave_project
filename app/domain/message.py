from pydantic import BaseModel


class Message(BaseModel):
    session_id: str
    writer_id: str
    message_type: int
    content: str
    created_at: str = None
    score: float = 0
    id: int = 0
