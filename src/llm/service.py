import json
import os
from pathlib import Path
from openai import AsyncOpenAI
ROOT = Path(__file__).resolve().parents[2]
PROMPT_VERSION = "triage-v1"
async def classify(text: str):
    prompt = (ROOT / "prompts" / f"{PROMPT_VERSION}.md").read_text(encoding="utf-8")
    async with AsyncOpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"], timeout=30, max_retries=0) as client:
        response = await client.chat.completions.create(model=os.environ["LLM_MODEL"], messages=[{"role":"system","content":prompt},{"role":"user","content":json.dumps({"text":text})}], temperature=0, max_tokens=256)
        return json.loads(response.choices[0].message.content or "")
