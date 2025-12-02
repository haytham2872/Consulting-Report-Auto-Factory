"""Simple wrapper around Claude messages API (Anthropic)."""
from __future__ import annotations

import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

DEFAULT_MODEL = os.getenv("CONSULTING_FACTORY_MODEL", "claude-3-haiku-20240307")

def _client() -> Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Create a .env file or export the variable.")
    return Anthropic(api_key=api_key)


def chat(
    system_prompt: str,
    user_content: str,
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 700,
) -> str:
    client = _client()
    response = client.messages.create(
        model=model or DEFAULT_MODEL,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return "".join([part.text for part in response.content if getattr(part, "type", "") == "text"])


def chat_json(
    system_prompt: str,
    user_content: str,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 700,
) -> Dict[str, Any]:
    raw = chat(system_prompt, user_content, model=model, temperature=temperature, max_tokens=max_tokens)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Failed to parse JSON from model response: {exc}\nRaw response: {raw}")

