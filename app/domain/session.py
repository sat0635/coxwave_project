from dataclasses import dataclass


@dataclass
class Session:
    session_id: str
    user_id: str