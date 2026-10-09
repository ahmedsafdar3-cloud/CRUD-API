import json
import os
from pathlib import Path

from openai import AsyncOpenAI
from fastapi import HTTPException
from pydantic import ValidationError

from src.llm.logs import write_log
from src.llm.parser import parse_output

ROOT = Path(__file__).resolve().parents[2]
PROMPT_VERSION = "triage-v1"


async def classify(text: str):
    prompt = (ROOT / "prompts" / f"{PROMPT_VERSION}.md").read_text(encoding="utf-8")
    async with AsyncOpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
        timeout=30.0,
        max_retries=0,
    ) as client:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps({"text": text})},
        ]
        failures = []
        for repair in range(2):
            response = await client.chat.completions.create(
                model=os.environ["LLM_MODEL"], messages=messages,
                temperature=0, max_tokens=256,
            )
            raw = response.choices[0].message.content or ""
            try:
                return parse_output(raw)
            except (ValueError, ValidationError) as exc:
                error = str(exc)
                failures.append({"output": raw, "error": error})
                if repair == 0:
                    messages.extend([
                        {"role": "assistant", "content": raw},
                        {"role": "user", "content": "Your previous answer was rejected: " + error + ". Return only corrected JSON matching the schema."},
                    ])
        write_log("quarantine.jsonl", {
            "input": {"text": text}, "prompt_version": PROMPT_VERSION,
            "model": os.environ["LLM_MODEL"], "failures": failures,
        })
        raise HTTPException(422, detail="Model output failed validation after one repair; sent for review")
