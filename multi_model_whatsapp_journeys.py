#!/usr/bin/env python3
"""
Multi-model WhatsApp Journey Generator using OpenRouter.

- Reads a master prompt from a .md file (e.g. PROMPT_4_WhatsApp_Journey_Generator.md)
- Sends it to multiple models on OpenRouter
- Expects each model to return THREE fenced code blocks:
    ```file:journey.md
    ...
    ```
    ```file:full_detailed.html
    ...
    ```
    ```file:workflow_overview.html
    ...
    ```
- Writes each block to disk under outputs/<scenario>/<model_slug>/...
"""

import argparse
import os
import re
from pathlib import Path
from typing import List

import requests

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip .env loading

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


FORMAT_INSTRUCTIONS = """Now format your entire response as exactly three fenced code blocks, with no extra commentary before, after, or between them.

1) Markdown journey file:

```file:journey.md
...your markdown journey for the scenario...
```

2) Full detailed HTML visualization:

```file:full_detailed.html
...your full detailed HTML visualization for the scenario...
```

3) Workflow overview HTML:

```file:workflow_overview.html
...your workflow overview HTML visualization for the scenario...
```
"""


def load_prompt_body(prompt_path: Path) -> str:
    """Load the prompt .md and, if present, extract the first ``` fenced block."""
    text = prompt_path.read_text(encoding="utf-8")
    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def slugify_model(model_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", model_id).strip("_")


def call_model(model: str, prompt_body: str, scenario: str, api_key: str) -> str:
    """Call a single OpenRouter model and return the raw content string."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # Optional but recommended for attribution:
        "HTTP-Referer": "http://localhost",
        "X-Title": "WhatsApp Journey Generator",
    }

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert WhatsApp marketing automation journey designer "
                "and senior front-end engineer. You strictly follow formatting instructions."
            ),
        },
        {
            "role": "user",
            "content": prompt_body,
        },
        {
            "role": "user",
            "content": (
                "For this run, create journeys for the following scenario:\n\n"
                f"{scenario}\n\n"
                "Override any [NUMBER] placeholders to generate exactly ONE journey set.\n"
                "Name the journey clearly using the scenario, audience, and product details.\n\n"
                f"{FORMAT_INSTRUCTIONS}"
            ),
        },
    ]

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
    }

    resp = requests.post(BASE_URL, headers=headers, json=payload, timeout=600)
    if resp.status_code != 200:
        raise RuntimeError(f"OpenRouter error {resp.status_code}: {resp.text}")
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected OpenRouter response format: {data}") from exc


def parse_files_from_content(content: str):
    """
    Parse ```file:NAME\n...\n``` blocks from the model content.

    Returns list of (filename, text).
    """
    pattern = re.compile(r"```file:([^\n]+)\n(.*?)```", re.DOTALL)
    files = pattern.findall(content)
    if not files:
        raise ValueError(
            "No ```file:...``` blocks found in model output. "
            "Check that the model followed the formatting instructions."
        )
    return [(name.strip(), body.rstrip()) for name, body in files]


def write_files_for_model(
    model_id: str,
    parsed_files,
    output_dir: Path,
    scenario_slug: str,
):
    """Write parsed (filename, body) pairs to disk under outputs/<scenario>/<model_slug>/."""
    model_slug = slugify_model(model_id)
    base = output_dir / scenario_slug / model_slug
    base.mkdir(parents=True, exist_ok=True)

    written_paths = []
    for filename, body in parsed_files:
        # Make sure filename is safe-ish
        safe_name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", filename).strip("_")
        path = base / safe_name
        path.write_text(body, encoding="utf-8")
        written_paths.append(path)

    return written_paths


def main(
    prompt_path: str,
    scenario: str,
    models: List[str],
    output_dir: str,
):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Missing OPENROUTER_API_KEY environment variable. "
            "Set it before running this script."
        )

    prompt_file = Path(prompt_path)
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    output_base = Path(output_dir)
    output_base.mkdir(parents=True, exist_ok=True)

    prompt_body = load_prompt_body(prompt_file)
    scenario_slug = re.sub(r"[^a-zA-Z0-9]+", "_", scenario.lower()).strip("_") or "scenario"

    print(f"Using prompt file: {prompt_file}")
    print(f"Scenario: {scenario}")
    print(f"Models: {', '.join(models)}")
    print(f"Output directory: {output_base.resolve()}")
    print()

    for model in models:
        print(f"=== Calling model: {model} ===")
        content = call_model(model, prompt_body, scenario, api_key)
        parsed = parse_files_from_content(content)
        paths = write_files_for_model(model, parsed, output_base, scenario_slug)
        print(f"Wrote {len(paths)} files for {model}:")
        for p in paths:
            print(f"  - {p}")
        print()

    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate WhatsApp journeys with multiple OpenRouter models."
    )
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Path to PROMPT_4_WhatsApp_Journey_Generator.md (or similar).",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        required=True,
        help="Short description of the scenario (product, audience, offer, etc.).",
    )
    parser.add_argument(
        "--model",
        dest="models",
        action="append",
        required=False,
        help=(
            "OpenRouter model ID. Use multiple --model flags for multiple models. "
            "If omitted, a default trio will be used."
        ),
    )
    parser.add_argument(
        "--out",
        type=str,
        default="outputs",
        help="Base output directory (default: ./outputs).",
    )

    args = parser.parse_args()

    default_models = [
        "openai/gpt-4.1-mini",
        "anthropic/claude-3.5-sonnet",
        "meta-llama/llama-3.1-70b-instruct",
    ]

    models = args.models if args.models else default_models

    main(
        prompt_path=args.prompt,
        scenario=args.scenario,
        models=models,
        output_dir=args.out,
    )
