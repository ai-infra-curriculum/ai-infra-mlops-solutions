"""Pydantic schemas for ingestion-time validation."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserEvent(BaseModel):
    user_id: int = Field(..., ge=1)
    event_ts: datetime
    event_type: Literal["click", "view", "purchase", "add_to_cart"]
    item_id: str = Field(..., min_length=1, max_length=64)
    price: float = Field(..., ge=0, le=100_000)
    session_id: str = Field(..., pattern=r"^[a-f0-9]{32}$")

    @field_validator("event_ts")
    @classmethod
    def not_in_future(cls, v: datetime) -> datetime:
        if v.timestamp() > datetime.now().timestamp() + 60:
            raise ValueError("event_ts cannot be > 60s in the future")
        return v


class User(BaseModel):
    id: int = Field(..., ge=1)
    email: EmailStr
    country: str = Field(..., min_length=2, max_length=2)
    created_at: datetime


def validate_batch(rows: list[dict], model_cls) -> tuple[list, list]:
    """Return (valid, errors). Errors are (row_index, validation_error_str)."""
    valid, errors = [], []
    for i, row in enumerate(rows):
        try:
            valid.append(model_cls(**row))
        except Exception as e:
            errors.append((i, str(e)))
    return valid, errors
