import os

from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError

from src.llm.schema import STUB, TriageInput, TriageOutput
from src.llm.service import classify

router = APIRouter()


@router.post("/triage", response_model=TriageOutput, tags=["LLM"])
async def triage(request: Request):
    try:
        payload = TriageInput.model_validate(await request.json())
    except ValidationError as exc:
        errors = [
            {"field": ".".join(map(str, e["loc"])), "message": e["msg"]}
            for e in exc.errors()
        ]
        raise HTTPException(400, detail={"message": "Invalid input", "errors": errors})
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(400, detail={"message": "Body must be valid JSON", "field": "body"})
    if os.getenv("LLM_STUB") == "1":
        return STUB
    return await classify(payload.text)
