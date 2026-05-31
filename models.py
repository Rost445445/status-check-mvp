from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

ALLOWED_STATUSES = {"to check", "expired", "done", "not actual", "ideas backlog"}

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)


class Commitment(Base):
    __tablename__ = "commitments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.now,
        nullable=False,
    )
    project: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assignee: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50),
        default="to check",
        nullable=False,
    )
