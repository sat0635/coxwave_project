
from typing import List, Dict
from dataclasses import dataclass, field
from domain.message import Message

@dataclass
class Session:
    session_id: str
    user_id: str