"""Send a Gemini request and save one minimal JSON log per API attempt.

Run: python gemini-api-test.py --prompt-file prompts/detection.txt
Use --model to select one model without automatic fallbacks.
Readable thought summaries are requested by default; use --no-thought-summaries to disable.
Credentials: GEMINI_API_KEY in the environment or this folder's .env.
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
MODELS = ("gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite")
AVAILABLE_MODELS = MODELS + (
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
)
API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
PROMPT = "Reply with one short sentence confirming that you received this API test request."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=AVAILABLE_MODELS, help="Use only this model, without fallbacks.")
    parser.add_argument("--no-thought-summaries", action="store_true", help="Do not request readable thought summaries (does not disable thinking).")
    prompts = parser.add_mutually_exclusive_group()
    prompts.add_argument("--prompt", help="Exact message to send; defaults to a short connection test.")
    prompts.add_argument("--prompt-file", type=Path, help="UTF-8 file containing the exact message.")
    args = parser.parse_args()
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        parser.exit(1, "Set GEMINI_API_KEY in CodeBeacon/evaluation-study/.env before running.\n")

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
    output_dir = BASE_DIR / "evaluation-runs" / "gemini"
    output_dir.mkdir(parents=True, exist_ok=True)
    eastern = ZoneInfo("America/New_York")

    # Keep credentials in a header, out of URLs and saved request logs.
    with httpx.Client(headers={"x-goog-api-key": api_key}, timeout=60) as client:
        for index, model in enumerate(models):
            if index:
                time.sleep(3)
            date = datetime.now(eastern).strftime("%Y-%m-%d")
            messages = [{"role": "user", "parts": [{"text": prompt}]}]
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
                    f"{API_URL}/{model}:generateContent",
                    json={
                        "contents": messages,
                        "generationConfig": {
                            "temperature": 0,
                            "topP": 1,
                            # The existing cap includes both thinking and answer tokens.
                            "maxOutputTokens": 4096,
                            "thinkingConfig": {"includeThoughts": not args.no_thought_summaries},
                        },
                    },
                )
                log["http_status"] = response.status_code
                response.raise_for_status()
                data = response.json()
                log["model_used"] = data.get("modelVersion") or model
                candidates = data.get("candidates", [])
                if not candidates:
                    log["error"] = f"The API returned no response candidates. Feedback: {data.get('promptFeedback')}"
                else:
                    candidate = candidates[0]
                    # Signatures are encrypted state, not readable reasoning.
                    # Keep readable thoughts and content; omit signature-only parts.
                    parts = [
                        clean_part
                        for part in candidate.get("content", {}).get("parts", [])
                        if (clean_part := {
                            key: value for key, value in part.items()
                            if key not in ("thoughtSignature", "thought_signature")
                        })
                    ]
                    log["response"] = parts
                    if not any(part.get("text") and not part.get("thought") for part in parts):
                        log["error"] = "The API returned empty response text."
                    elif candidate.get("finishReason") != "STOP":
                        log["error"] = f"Response did not finish normally: {candidate.get('finishReason')}"
            except httpx.HTTPStatusError as exc:
                log["error"] = exc.response.text
            except httpx.RequestError as exc:
                # No HTTP status exists when no server response was received.
                log["error"] = f"Connection or timeout error: {exc}"
            except (ValueError, KeyError, TypeError, AttributeError) as exc:
                log["error"] = f"Invalid API response: {exc}"
            finally:
                payload = json.dumps(log, indent=2, ensure_ascii=False)
                output_file = save_log(output_dir, date, model, payload.replace(api_key, "[REDACTED]"))
                print(f"Model: {log['model_used']} | HTTP status: {log['http_status']}")
                if log["response"] is not None:
                    content = "".join(part.get("text", "") for part in log["response"] if not part.get("thought"))
                    print(f"Response: {content.replace(api_key, '[REDACTED]')}")
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
