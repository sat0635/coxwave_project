from typing import List, Optional
from dataclasses import dataclass, field

@dataclass
class Message:
    writer: str
    message_type: int
    content: str
    content_vector: List[float]
    created_at: int
    score: int

