from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from semantix.models.base import Base, TimestampMixin, uuid_pk


class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = uuid_pk()
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="New chat")


class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"

    id: Mapped[str] = uuid_pk()
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    sql_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_summary_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
