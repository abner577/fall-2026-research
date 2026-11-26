"""Send a Mistral request and save the original answer and log in a separate folder per API attempt.

Run: python mistral-api-test.py --prompt-file prepared-request.txt
Use --model to select one model without automatic fallbacks.
Credentials: MISTRAL_API_KEY in the environment or this folder's .env.
"""

import argparse
import json
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv
from evaluation_logging import create_run_folder, now, resolve_case, save_log
from mistralai.client import Mistral
from mistralai.client.errors import MistralError


BASE_DIR = Path(__file__).resolve().parent
MODELS = ("mistral-large-4", "ministral-14b-2512", "ministral-8b-2512")
PROMPT = "Reply with one short sentence confirming that you received this API test request."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=MODELS, help="Use only this model, without fallbacks.")
    prompts = parser.add_mutually_exclusive_group()
    prompts.add_argument("--prompt", help="Exact message to send; defaults to a short connection test.")
    prompts.add_argument("--prompt-file", type=Path, help="UTF-8 file containing the exact message.")
    parser.add_argument("--case", choices=("practice", "version-A", "version-B"),
                        help="Run version; inferred for the saved A/B prompts, otherwise practice.")
    args = parser.parse_args()
    case = resolve_case(parser, args)
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("MISTRAL_API_KEY", "").strip()
    if not api_key or api_key == "your_mistral_api_key_here":
        parser.exit(1, "Set MISTRAL_API_KEY in CodeBeacon/evaluation-study/llms/.env before running.\n")

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
    output_dir = BASE_DIR.parent / "evaluation-runs" / "mistral"
    output_dir.mkdir(parents=True, exist_ok=True)

    with Mistral(api_key=api_key, timeout_ms=60000, retry_config=None) as client:
        for index, model in enumerate(models):
            if index:
                time.sleep(3)
            started = now()
            folder = create_run_folder(output_dir, case, started)
            (folder / "raw-output.txt").touch()
            print(f"Saving this attempt to: {folder}", flush=True)
            messages = [{"role": "user", "content": prompt}]
            log = {
                "case": case,
                "started_at": started.isoformat(),
                "model_used": model,
                "request": messages,
                "http_status": None,
                "error": None,
                "response": None,
            }
            print(f"Request to {model}:\n{prompt.replace(api_key, '[REDACTED]')}", flush=True)
            try:
                response = client.chat.complete(
                    model=model, messages=messages, temperature=0, top_p=1,
                    max_tokens=4096, stream=False,
                )
                log["http_status"] = 200
                log["model_used"] = response.model
                if not response.choices:
                    log["error"] = "The API returned no response choices."
                else:
                    choice = response.choices[0]
                    # Preserve structured content, including reasoning, when returned.
                    log["response"] = choice.message.model_dump(mode="json")["content"]
                    if not choice.message.content:
                        log["error"] = "The API returned empty response content."
                    elif choice.finish_reason != "stop":
                        log["error"] = f"Response did not finish normally: {choice.finish_reason}"
            except MistralError as exc:
                log["http_status"] = exc.status_code
                log["error"] = str(exc)
            except httpx.RequestError as exc:
                # No HTTP status exists when no server response was received.
                log["error"] = f"Connection or timeout error: {exc}"
            finally:
                payload = json.dumps(log, indent=2, ensure_ascii=False)
                output_file = save_log(folder, payload.replace(api_key, "[REDACTED]"))
                print(f"Model: {log['model_used']} | HTTP status: {log['http_status']}")
                content = log["response"]
                if isinstance(content, list):
                    content = "".join(chunk.get("text", "") for chunk in content if chunk.get("type") == "text")
                if content is not None:
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
