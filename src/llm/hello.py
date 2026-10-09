"""Provider smoke check: python -m src.llm.hello"""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

if __name__ == "__main__":
    with OpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
        timeout=30.0,
        max_retries=0,
    ) as client:
        result = client.chat.completions.create(
            model=os.environ["LLM_MODEL"],
            messages=[{"role": "user", "content": "Reply with exactly the word: ready"}],
            temperature=0,
            max_tokens=10,
        )
        print(result.choices[0].message.content)
