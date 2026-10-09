import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    base_url: str = "http://127.0.0.1:11434/v1/"
    api_key: str = "ollama"
    model: str = "qwen2.5-coder:7b"
    timeout: float = Field(default=30, gt=0, le=60, allow_inf_nan=False)
    max_retries: int = Field(default=3, ge=0, le=3)
    input_price: float = Field(default=0, ge=0, allow_inf_nan=False)
    output_price: float = Field(default=0, ge=0, allow_inf_nan=False)

    @classmethod
    def from_env(cls):
        return cls(
            base_url=os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1/"),
            api_key=os.getenv("LLM_API_KEY", "ollama"),
            model=os.getenv("LLM_MODEL", "qwen2.5-coder:7b"),
            timeout=os.getenv("LLM_TIMEOUT_SECONDS", "30"),
            max_retries=os.getenv("LLM_MAX_RETRIES", "3"),
            input_price=os.getenv("LLM_INPUT_USD_PER_MILLION", "0"),
            output_price=os.getenv("LLM_OUTPUT_USD_PER_MILLION", "0"),
        )
