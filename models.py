"""Pydantic schemas for Project Resonance - Zero-Knowledge Architecture."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ArousalStateToken(BaseModel):
    """Zero-knowledge biometric token - no raw biometric data exposed."""

    state: Literal["calm", "elevated", "critical"]
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        return v


class ContextToken(BaseModel):
    """Environmental context token from vision analysis."""

    scene: Literal["sedentary", "active", "outdoor", "unknown"]
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        return v


class ActuationCommand(BaseModel):
    """Fire TV actuation command."""

    action: str
    protocol: str
    status: str = "pending"