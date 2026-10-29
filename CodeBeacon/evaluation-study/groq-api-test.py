"""Send a Groq request and save one minimal JSON log per API attempt.

Run: python groq-api-test.py --prompt-file prompts/detection.txt
Use --model to select one model without automatic fallbacks.
Credentials: GROQ_API_KEY in the environment or this folder's .env.
"""

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv
from evaluation_logging import save_log


BASE_DIR = Path(__file__).resolve().parent
MODELS = ("openai/gpt-oss-120b", "openai/gpt-oss-20b")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
PROMPT = "Reply with one short sentence confirming that you received this API test request."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=MODELS, help="Use only this model, without fallbacks.")
    prompts = parser.add_mutually_exclusive_group()
    prompts.add_argument("--prompt", help="Exact message to send; defaults to a short connection test.")
    prompts.add_argument("--prompt-file", type=Path, help="UTF-8 file containing the exact message.")
    args = parser.parse_args()
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_groq_api_key_here":
        parser.exit(1, "Set GROQ_API_KEY in CodeBeacon/evaluation-study/.env before running.\n")

    prompt = args.prompt if args.prompt is not None else PROMPT
    if args.prompt_file:
        # Preserve line endings and whitespace in the supplied prompt.
        try:
            prompt = args.prompt_file.read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as exc:
            parser.exit(1, f"Cannot read prompt file: {exc}\n")
    if not prompt.strip():
        parser.exit(1, "The request message cannot be empty.\n")

    models = (args.model,) if args.model else MODELS
    output_dir = BASE_DIR / "evaluation-runs" / "groq"
    output_dir.mkdir(parents=True, exist_ok=True)
    eastern = ZoneInfo("America/New_York")

    with httpx.Client(headers={"Authorization": f"Bearer {api_key}"}, timeout=60) as client:
        for index, model in enumerate(models):
            if index:
                time.sleep(3)
            date = datetime.now(eastern).strftime("%Y-%m-%d")
            messages = [{"role": "user", "content": prompt}]
            log = {
                "model_used": model,
                "request": messages,
                "http_status": None,
                "error": None,
                "response": None,
            }
            print(f"Request to {model}:\n{prompt.replace(api_key, '[REDACTED]')}", flush=True)
            try:
                response = client.post(
                    API_URL,
                    json={
                        "model": model, "messages": messages,
                        "temperature": 0, "top_p": 1,
                        "max_completion_tokens": 4096, "stream": False,
                        "include_reasoning": True,
                    },
                )
                log["http_status"] = response.status_code
                response.raise_for_status()
                data = response.json()
                log["model_used"] = data.get("model") or model
                choices = data.get("choices", [])
                if not choices:
                    log["error"] = "The API returned no response choices."
                else:
                    choice = choices[0]
                    message = choice.get("message", {})
                    log["response"] = {
                        "content": message.get("content"),
                        "reasoning": message.get("reasoning"),
                    }
                    if not message.get("content"):
                        log["error"] = "The API returned empty response content."
                    elif choice.get("finish_reason") != "stop":
                        log["error"] = f"Response did not finish normally: {choice.get('finish_reason')}"
            except httpx.HTTPStatusError as exc:
                log["error"] = exc.response.text
            except httpx.RequestError as exc:
                log["error"] = f"Connection or timeout error: {exc}"
            except (ValueError, KeyError, TypeError, AttributeError) as exc:
                log["error"] = f"Invalid API response: {exc}"
            finally:
                payload = json.dumps(log, indent=2, ensure_ascii=False)
                output_file = save_log(output_dir, date, model, payload.replace(api_key, "[REDACTED]"))
                print(f"Model: {log['model_used']} | HTTP status: {log['http_status']}")
                if log["response"] is not None:
                    content = log["response"]["content"]
                    print(f"Response: {str(content).replace(api_key, '[REDACTED]')}")
                if log["error"]:
                    print(f"Error: {log['error'].replace(api_key, '[REDACTED]')}")
                print(f"Log saved to: {output_file}")

            if log["error"] is None:
                return 0
            if log["http_status"] not in (403, 404, 503) or model == models[-1]:
                return 1
            print("Model access/availability problem; trying the next backup.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
