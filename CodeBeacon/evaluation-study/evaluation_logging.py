"""Shared log naming for evaluation API scripts."""


def save_log(output_dir, date, model, payload):
    """Save a dated model log, numbering repeat runs without overwriting files."""
    filename_model = model
    for prefix in ("gemini-", "mistral-", "ministral-"):
        if filename_model.startswith(prefix):
            filename_model = filename_model[len(prefix):]
            break
    stem = f"{date}_{filename_model}"
    index = 0
    while True:
        suffix = f" ({index})" if index else ""
        output_file = output_dir / f"{stem}{suffix}.json"
        try:
            with output_file.open("x", encoding="utf-8") as handle:
                handle.write(payload)
            return output_file
        except FileExistsError:
            index += 1
