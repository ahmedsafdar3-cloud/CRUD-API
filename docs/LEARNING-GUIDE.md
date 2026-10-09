# Understanding the Week 7 assignment

This guide explains the support-triage endpoint, its reliability checks, and how to run and test it.

## 1. What we added

Your existing FastAPI application already manages tasks and authenticates users. We added `POST /triage`, a separate operation that classifies a support message. It does not create tasks, authenticate users, or change the database.

An endpoint is an address plus an HTTP method. `POST` means the caller supplies data in the request body. For example, a message about a duplicate subscription charge is sent as `{"text":"I was charged twice."}`.

An LLM is a language model. It can interpret messy wording, but it can also make mistakes. We run your downloaded `qwen2.5-coder:7b` through Ollama on your own computer. The `openai` Python package is only the client library: its base URL points at Ollama, not an OpenAI paid service.

## 2. Follow one request through the code

1. `main.py` registers the router from `src/routes/triage.py`.
2. The route reads JSON and validates it using `TriageInput` in `src/llm/schema.py`. Missing text, numbers instead of text, blank text, extra fields, or more than 2,000 characters produce HTTP 400 before any model call.
3. The route checks `LLM_ENABLED` and `LLM_STUB`. Disabled mode sends the message to manual review. Stub mode returns a known fixed response for development.
4. `src/llm/service.py` loads `prompts/triage-v1.md`. That file describes the job, output fields, rules, uncertainty behavior, and examples.
5. The prompt is a system message. The caller's text is JSON-encoded in a separate user message. This reduces prompt-injection risk; it does not guarantee semantic correctness.
6. `src/llm/provider.py` sends the request with `AsyncOpenAI`. Async means another request can be handled while this one waits for the provider.
7. `src/llm/parser.py` finds the JSON object, including when wrapped in a Markdown fence. Pydantic checks its fields and values.
8. If validation fails, the service sends the model its broken answer and exact error, then asks for corrected JSON once.
9. After another invalid answer, the route returns HTTP 422 and stores both failures in the ignored local quarantine log. Raw model text never becomes the API response.

## 3. Why the schema matters

JSON is a data format; a schema is its contract. Our output must contain exactly category, urgency, confidence, and reason. Category is one of billing, bug, feature, other. Urgency is low, normal, or high. Confidence is numeric from 0 to 1. Reason is nonblank and no longer than 240 characters.

Pydantic rejects invented labels, numeric strings masquerading as confidence, and unexpected fields. It cannot tell whether an outage really belongs in bug. The evaluation catches that kind of error.

## 4. Repairs and transport retries are different

A repair fixes the *content* of an answer. There is at most one repair.

A transport retry repeats a failed provider call. Timeouts, HTTP 429 (rate limit), and HTTP 5xx (provider failures) may retry three times after the first attempt. The waits are 1, 2, and 4 seconds plus random jitter, unless a 429 supplies Retry-After. HTTP 400, 401, and 403 are never retried. The SDK's own retries are explicitly disabled so two retry systems do not multiply the calls.

Each provider attempt has a default 30-second deadline; settings may not exceed 60 seconds. The whole operation, including waits and repair, has a 120-second deadline. In the worst case there are eight provider attempts: four for the first answer and four for a repair, subject to that overall deadline.

## 5. What the status codes mean

| Code | Meaning here |
| --- | --- |
| 200 | Valid structured answer, stub, or disabled fallback |
| 400 | The caller's input is invalid |
| 422 | The model's output was still invalid after one repair |
| 502 | The provider rejected the request or kept returning server errors |
| 503 | Provider unavailable, rate-limited, or configuration invalid |
| 504 | A provider timeout or the overall deadline expired |

## 6. Environment variables and secrets

`.env` contains your local configuration and is ignored by Git. `.env.example` documents the variable names without real credentials. The literal Ollama key `ollama` is a dummy value the client requires and the local server ignores.

`LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` select the provider. `LLM_STUB=1` helps debug without inference. `LLM_ENABLED=false` is the kill switch. Change settings, then restart the API to load them.

Database and Supabase connections are created only when their routes need them. That lets the new endpoint run without those services; existing task and authentication routes still need their original setup.

## 7. Logs and costs

`logs/calls.jsonl` stores one JSON object per attempted model call: model, prompt version, token counts, duration, repair count, status, and estimated price. Tokens are the pieces of text the model consumes and generates. Failed calls may have unknown usage, represented by null.

Ollama has zero provider charges. Electricity and hardware still cost something. To estimate a hosted provider, set its input and output prices per million tokens: `(input_tokens * input_price + output_tokens * output_price) / 1,000,000` per call. Count repair calls and retries too.

`logs/quarantine.jsonl` contains rejected text, input, and errors for review. It can contain sensitive support content, so it stays local and is not committed. This is a learning project; production would need a retention policy and access controls.

## 8. Evaluation versus automated tests

`evals/cases.json` has eight made-up messages and expected labels. `evals/run.py` calls the actual endpoint and records the actual model answers in `evals/results.json`. The score is 7/8 on category and 7/8 on all checks, from October 9, 2026 using triage-v1. The model misclassified the outage as billing. This small dataset is useful evidence, not a general accuracy guarantee.

`tests/test_triage.py` uses a fake HTTP transport through the real SDK to exercise errors without calling Ollama or spending quota. It checks malformed output, exactly one repair, quarantine, refusal, empty choices, timeouts, retry bounds, Retry-After, pricing, input validation, stub, and kill switch.

## 9. Git and GitHub

Git tracks local snapshots; GitHub hosts them for other people. Each assignment stage has its own commit with a meaningful message. Run `git log --oneline -6` to see them, `git show <commit>` to inspect a stage, and `git status` to check pending changes. A push uploads commits to the repository's remote.

## 10. Practice in VS Code

Open `http://127.0.0.1:8000/docs`, expand POST /triage, click Try it out, and send `{"text":"The app crashes when I save a task."}`. Read the response, then find the matching line in the call log.

Try an empty body and notice that no call-log line is added. Set LLM_STUB=1 in .env, restart, and observe the fixed answer. Then set LLM_ENABLED=false, restart, and observe the manual-review fallback. Restore LLM_STUB=0 and LLM_ENABLED=true when finished.

Run `python -m unittest discover -s tests -v` to check the failure paths. Run `python evals/run.py` with the real server up to measure the model again. Read the failed outage case and explain why schema validation accepted it: billing is a valid label even when it is the wrong judgment.
