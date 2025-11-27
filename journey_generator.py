"""
Core journey generation logic - refactored for use by both CLI and web app.
"""
import os
import re
from typing import List, Dict, Tuple
import requests

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

FORMAT_INSTRUCTIONS = """
## FINAL REMINDER - CRITICAL

**USE ONLY THE DATA FROM SECTION 1 (BRIEF) ABOVE.**

Do NOT invent:
- Company names (use ONLY the company name from the BRIEF)
- Product names (use ONLY the product name from the BRIEF)
- Industries (use ONLY what's implied by the user's product/audience)
- URLs (use ONLY the URLs provided in the BRIEF)
- Assets (use ONLY the assets listed in the BRIEF)

You MAY be creative with:
- Message copy/wording (following brand voice)
- Journey flow structure
- Timing between messages

Now format your entire response as exactly three fenced code blocks, with no extra commentary before, after, or between them.

1) Markdown journey file:

```file:journey.md
(Journey documentation using ONLY the company, product, audience, URLs, and assets from the BRIEF section above)
```

2) Summary Workflow HTML:

```file:summary_workflow.html
(Summary HTML using ONLY the company, product, audience, URLs, and assets from the BRIEF section above)
```

3) Full Detail Workflow HTML:

```file:full_detail_workflow.html
(Full detail HTML using ONLY the company, product, audience, URLs, and assets from the BRIEF section above)
```
"""


def extract_prompt_body(prompt_content: str) -> str:
    """
    Extract prompt body from markdown content.
    
    Previously this extracted content from a single code block, but now our prompts
    contain multiple code blocks (HTML/CSS templates), so we return the full content.
    
    Only extract from a code block if the ENTIRE content is wrapped in one
    (starts with ``` on line 1).
    """
    lines = prompt_content.strip().split('\n')
    
    # Only extract if the prompt starts with a code fence (entire content wrapped)
    if lines and lines[0].strip().startswith('```'):
        # Find the closing fence and extract content between them
        content_lines = []
        in_block = False
        for line in lines:
            if line.strip().startswith('```') and not in_block:
                in_block = True
                continue
            elif line.strip() == '```' and in_block:
                break
            elif in_block:
                content_lines.append(line)
        if content_lines:
            return '\n'.join(content_lines).strip()
    
    # Otherwise return the full content as-is (prompt contains embedded code blocks)
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
                "You are an expert WhatsApp marketing automation journey designer. "
                "CRITICAL RULE: You must ONLY use the company name, product name, industry, "
                "URLs, and assets that the user provides in Section 1 (BRIEF). "
                "NEVER invent fictional companies, products, industries, or URLs. "
                "You may be creative with message wording and journey flow, but all "
                "factual data (names, URLs, assets) must come directly from the user's input."
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
                "REMEMBER: Use ONLY the company name, product name, URLs, and assets "
                "from Section 1 (BRIEF) above. Do not invent any new companies, products, "
                "industries, or URLs.\n\n"
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
                    "summary_workflow.html": "...",
                    "full_detail_workflow.html": "..."
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

