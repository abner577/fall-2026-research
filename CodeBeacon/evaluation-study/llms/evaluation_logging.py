"""Shared run output handling for the three LLM API scripts."""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from support.run_outputs import create_run_folder, now


def resolve_case(parser, args):
    """Recognize the saved study prompts; custom study inputs need --case."""
    inferred = None
    if args.prompt_file:
        for version in ("version-A", "version-B"):
            if args.prompt_file.name == f"llm-detection-prompt-{version}.txt":
                inferred = version
    if inferred and args.case and args.case != inferred:
        parser.error(f"--case {args.case} conflicts with {args.prompt_file.name}.")
    return args.case or inferred or "practice"


def response_text(response):
    """Extract returned answer text without normalizing or grading it."""
    if response is None:
        return ""
    if isinstance(response, str):
        return response
    if isinstance(response, dict):
        return response_text(response.get("content"))
    if isinstance(response, list):
        return "".join(
            part.get("text", "") for part in response
            if isinstance(part, dict) and not part.get("thought")
            and isinstance(part.get("text", ""), str)
        )
    raise TypeError(f"Unexpected response content: {type(response).__name__}")


def save_log(folder, payload):
    """Keep the existing JSON log and a separate copy of its original answer."""
    output_file = folder / "run-log.json"
    output_file.write_text(payload, encoding="utf-8")
    content = response_text(json.loads(payload)["response"])
    with (folder / "raw-output.txt").open("w", encoding="utf-8", newline="") as stream:
        stream.write(content)
    return output_file
