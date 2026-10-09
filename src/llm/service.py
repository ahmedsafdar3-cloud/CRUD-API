import asyncio
import json
from pathlib import Path

from fastapi import HTTPException
from openai import AsyncOpenAI
from pydantic import ValidationError

from src.llm.logs import write_log
from src.llm.parser import parse_output
from src.llm.provider import PROMPT_VERSION, complete
from src.llm.settings import Settings

ROOT = Path(__file__).resolve().parents[2]


async def classify(text: str):
    """Bound provider attempts, backoff, and repair to 120 seconds total."""
    try:
        async with asyncio.timeout(120):
            return await _classify(text)
    except TimeoutError:
        raise HTTPException(504, detail="LLM request exceeded its 120-second total deadline")


async def _classify(text: str):
    try:
        settings = Settings.from_env()
        prompt = (ROOT / "prompts" / f"{PROMPT_VERSION}.md").read_text(encoding="utf-8")
    except (ValidationError, OSError):
        raise HTTPException(503, detail="LLM configuration is invalid; check settings and prompt file")
    async with AsyncOpenAI(
        base_url=settings.base_url, api_key=settings.api_key,
        timeout=settings.timeout, max_retries=0,
    ) as client:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps({"text": text})},
        ]
        failures = []
        for repair in range(2):
            response = await complete(client, settings, messages, repair)
            choice = response.choices[0] if response.choices else None
            raw = (choice.message.content or "") if choice else ""
            refusal = getattr(choice.message, "refusal", None) if choice else None
            try:
                if refusal:
                    raise ValueError("Model refused the classification")
                return parse_output(raw)
            except (ValueError, ValidationError) as exc:
                error = str(exc)
                failures.append({"output": raw, "error": error})
                if repair == 0:
                    messages.extend([
                        {"role": "assistant", "content": raw},
                        {"role": "user", "content": (
                            "Your previous answer was rejected: " + error
                            + ". Return only corrected JSON matching the schema."
                        )},
                    ])
        write_log("quarantine.jsonl", {
            "input": {"text": text}, "prompt_version": PROMPT_VERSION,
            "model": settings.model, "failures": failures,
        })
        raise HTTPException(422, detail="Model output failed validation after one repair; sent for review")
