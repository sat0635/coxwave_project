import sqlite3

from app.application.ports.message_repository import MessageRepository
from app.domain.message import Message


class InMemoryMessageRepository(MessageRepository):
    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            writer_id TEXT,
            message_type INTEGER,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            score FLOAT DEFAULT 0
        )
        """)
        self.conn.commit()

    def insert(self, message: Message):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO message (session_id, writer_id, message_type, content)
            VALUES (?, ?, ?, ?)
        """, (
            message.session_id,
            message.writer_id,
            message.message_type,
            message.content
        ))
        self.conn.commit()

    def select_by_session(self, session_id: str) -> list[Message]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, session_id, writer_id, message_type, content, created_at, score
            FROM (
                SELECT id, session_id, writer_id, message_type, content, created_at, score
                FROM message
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT 30
            ) AS recent_messages
            ORDER BY created_at;
        """, (session_id,))
        rows = cursor.fetchall()

        messages = []
        for row in rows:
            messages.append(Message(
                id=row["id"],
                session_id=row["session_id"],
                writer_id=row["writer_id"],
                message_type=row["message_type"],
                content=row["content"],
                created_at=row["created_at"],
                score=row["score"]
            ))

        return messages

