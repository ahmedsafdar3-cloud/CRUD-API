import json

from src.llm.schema import TriageOutput


def parse_output(raw: str) -> TriageOutput:
    """Accept a JSON object with an optional fence or introductory sentence."""
    start = raw.find("{")
    if start < 0:
        raise ValueError("Expected a JSON object")
    value, _ = json.JSONDecoder().raw_decode(raw[start:])
    return TriageOutput.model_validate(value)
