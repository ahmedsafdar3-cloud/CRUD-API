from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TriageInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    text: str = Field(min_length=1, max_length=2000)

    @field_validator("text")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be blank")
        return value


class TriageOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    category: Literal["billing", "bug", "feature", "other"]
    urgency: Literal["low", "normal", "high"]
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)
    reason: str = Field(min_length=1, max_length=240)

    @field_validator("reason")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("reason must not be blank")
        return value


STUB = TriageOutput(
    category="other", urgency="normal", confidence=0.0,
    reason="Stub response; no model was called.",
)
