import asyncio
import math
import random
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from fastapi import HTTPException
from openai import APIConnectionError, APIStatusError, APITimeoutError

from src.llm.logs import write_log
from src.llm.settings import Settings

PROMPT_VERSION = "triage-v1"


def retry_after(headers) -> float | None:
    value = headers.get("retry-after")
    if value is None:
        return None
    try:
        seconds = float(value)
        return max(0.0, seconds) if math.isfinite(seconds) else None
    except ValueError:
        try:
            date = parsedate_to_datetime(value)
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            return max(0.0, (date - datetime.now(timezone.utc)).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None


async def complete(client, settings: Settings, messages: list, repair: int):
    """SDK retries are off; at most four transport attempts per completion."""
    for attempt in range(settings.max_retries + 1):
        started = time.perf_counter()
        record = {
            "prompt_version": PROMPT_VERSION, "model": settings.model,
            "repair_count": repair, "needed_repair": bool(repair),
            "attempt": attempt + 1, "input_tokens": None,
            "output_tokens": None, "estimated_cost_usd": None,
        }
        failure = None
        delay = None
        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=settings.model, messages=messages,
                    temperature=0, max_tokens=256,
                ),
                timeout=settings.timeout,
            )
            usage = response.usage
            if usage is not None:
                record.update(input_tokens=usage.prompt_tokens, output_tokens=usage.completion_tokens)
                record["estimated_cost_usd"] = (
                    usage.prompt_tokens * settings.input_price
                    + usage.completion_tokens * settings.output_price
                ) / 1_000_000
            record["status"] = "success"
            return response
        except (APITimeoutError, asyncio.TimeoutError):
            record["status"] = "timeout"
            failure = HTTPException(504, detail="LLM provider timed out")
        except APIStatusError as exc:
            record.update(status="provider_error", http_status=exc.status_code)
            if exc.status_code != 429 and exc.status_code < 500:
                raise HTTPException(502, detail=f"LLM provider rejected the request (HTTP {exc.status_code}); not retried")
            if exc.status_code == 429:
                delay = retry_after(exc.response.headers)
            failure = HTTPException(503 if exc.status_code == 429 else 502, detail=f"LLM provider unavailable (HTTP {exc.status_code})")
        except APIConnectionError:
            record["status"] = "connection_error"
            raise HTTPException(503, detail="Cannot connect to LLM provider; check Ollama is running")
        except asyncio.CancelledError:
            record["status"] = "cancelled"
            raise
        except Exception:
            record["status"] = "unexpected_error"
            raise
        finally:
            record["duration_ms"] = round((time.perf_counter() - started) * 1000, 2)
            write_log("calls.jsonl", record)
        if attempt == settings.max_retries:
            raise failure
        await asyncio.sleep(delay if delay is not None else 2 ** attempt + random.uniform(0, 0.25))
