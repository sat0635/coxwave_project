from pydantic import BaseModel


class Session(BaseModel):
    session_id: str
    user_id: str