"""
Core journey generation logic - refactored for use by both CLI and web app.
"""
import os
import re
from typing import List, Dict, Tuple
import requests

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


def extract_prompt_body(prompt_content: str) -> str:
    """Extract prompt body from markdown content. If fenced code block exists, extract it."""
    match = re.search(r"```(.*?)```", prompt_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return prompt_content.strip()


def slugify_model(model_id: str) -> str:
    """Convert model ID to filesystem-safe slug."""
    return re.sub(r"[^a-zA-Z0-9]+", "_", model_id).strip("_")


def slugify_scenario(scenario: str) -> str:
    """Convert scenario text to filesystem-safe slug."""
    return re.sub(r"[^a-zA-Z0-9]+", "_", scenario.lower()).strip("_") or "scenario"


def call_model(model: str, prompt_body: str, scenario: str, api_key: str) -> str:
    """Call a single OpenRouter model and return the raw content string."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://whatsapp-journey-generator.railway.app",
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


def parse_files_from_content(content: str) -> List[Tuple[str, str]]:
    """
    Parse ```file:NAME\n...\n``` blocks from the model content.

    Returns list of (filename, text) tuples.
    """
    pattern = re.compile(r"```file:([^\n]+)\n(.*?)```", re.DOTALL)
    files = pattern.findall(content)
    if not files:
        raise ValueError(
            "No ```file:...``` blocks found in model output. "
            "Check that the model followed the formatting instructions."
        )
    return [(name.strip(), body.rstrip()) for name, body in files]


def generate_journeys(
    prompt_content: str,
    scenario: str,
    models: List[str],
    api_key: str,
) -> Dict[str, Dict[str, str]]:
    """
    Generate journeys for given models.

    Args:
        prompt_content: Full markdown prompt file content
        scenario: Scenario description
        models: List of model IDs to use
        api_key: OpenRouter API key

    Returns:
        Dictionary structure:
        {
            "scenario_slug": {
                "model_slug": {
                    "journey.md": "...",
                    "full_detailed.html": "...",
                    "workflow_overview.html": "..."
                }
            }
        }
    """
    prompt_body = extract_prompt_body(prompt_content)
    scenario_slug = slugify_scenario(scenario)

    results = {scenario_slug: {}}

    for model in models:
        model_slug = slugify_model(model)
        content = call_model(model, prompt_body, scenario, api_key)
        parsed_files = parse_files_from_content(content)

        # Convert list of (filename, content) to dict
        files_dict = {}
        for filename, file_content in parsed_files:
            # Sanitize filename
            safe_name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", filename).strip("_")
            files_dict[safe_name] = file_content

        results[scenario_slug][model_slug] = files_dict

    return results

