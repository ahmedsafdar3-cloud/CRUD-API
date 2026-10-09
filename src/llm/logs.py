import json
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"


def write_log(filename: str, record: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": datetime.now(timezone.utc).isoformat(), **record}
    with (LOG_DIR / filename).open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=True, allow_nan=False) + "\n")
