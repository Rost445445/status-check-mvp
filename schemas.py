from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, field_validator

class Token(BaseModel):
    access_token: str
    token_type: str

AllowedStatus = Literal["to check", "expired", "done", "not actual", "ideas backlog"]


class CommitmentBase(BaseModel):
    author: str
    title: str
    description: Optional[str] = None
    project: Optional[str] = None
    assignee: Optional[str] = None
    reviewer: Optional[str] = None
    deadline: Optional[datetime] = None
    status: AllowedStatus = "to check"

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = {"to check", "expired", "done", "not actual", "ideas backlog"}
        if value not in allowed:
            raise ValueError(
                f"Invalid status '{value}'. Allowed values: {allowed}"
            )
        return value


class CommitmentCreate(CommitmentBase):
    """Schema used when creating a new commitment (POST)."""
    pass


class CommitmentUpdate(BaseModel):
    """Schema used when updating a commitment (PUT). All fields are optional."""
    author: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    project: Optional[str] = None
    assignee: Optional[str] = None
    reviewer: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[AllowedStatus] = None

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed = {"to check", "expired", "done", "not actual", "ideas backlog"}
        if value not in allowed:
            raise ValueError(
                f"Invalid status '{value}'. Allowed values: {allowed}"
            )
        return value


class CommitmentRead(CommitmentBase):
    """Schema returned in responses (includes DB-generated fields)."""
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
