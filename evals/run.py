"""python evals/run.py --url http://127.0.0.1:8000 --output evals/results.json"""
import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", default="evals/results.json")
    args = parser.parse_args()
    cases = json.loads((ROOT / "evals/cases.json").read_text())
    results = []
    for case in cases:
        request = Request(args.url.rstrip("/") + "/triage", data=json.dumps({"text":case["text"]}).encode(), headers={"Content-Type":"application/json"})
        try:
            with urlopen(request, timeout=130) as response:
                actual = json.load(response)
                status = response.status
        except HTTPError as exc:
            actual, status = json.load(exc), exc.code
        except (URLError, TimeoutError) as exc:
            actual, status = {"error": str(exc.reason) if isinstance(exc, URLError) else "Timed out"}, 0
        expected = case["expected"]
        category_ok = status == 200 and actual.get("category") == expected["category"]
        urgency_ok = status == 200 and actual.get("urgency") == expected["urgency"]
        unsure_ok = not expected.get("low_confidence") or (isinstance(actual.get("confidence"), (int,float)) and actual["confidence"] < 0.5)
        passed = category_ok and urgency_ok and unsure_ok
        results.append({"id":case["id"], "expected":expected, "actual":actual, "status":status, "category_matched":category_ok, "passed":passed})
        print(f'{case["id"]}: {"PASS" if passed else "FAIL"} - {actual}', flush=True)
    matched = sum(r["category_matched"] for r in results)
    full = sum(r["passed"] for r in results)
    report = {"date":datetime.now(ZoneInfo("Asia/Karachi")).isoformat(), "prompt_version":"triage-v1", "provider":"Ollama", "model":os.getenv("LLM_MODEL", "qwen2.5-coder:7b"), "total":len(results), "category_matched":matched, "category_accuracy_percent":matched / len(results) * 100, "all_checks_passed":full, "results":results}
    output = Path(args.output)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(f'Category: {matched}/{len(results)} ({report["category_accuracy_percent"]:.1f}%). All checks: {full}/{len(results)}. Saved {output}')

if __name__ == "__main__":
    main()
