"""Simple wrapper around OpenAI Chat Completions."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_MODEL = os.getenv("CONSULTING_FACTORY_MODEL", "gpt-4.1-mini")

def _client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Create a .env file or export the variable.")
    return OpenAI(api_key=api_key)


def chat(system_prompt: str, user_content: str, model: str | None = None, temperature: float = 0.3) -> str:
    client = _client()
    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def chat_json(system_prompt: str, user_content: str, model: str | None = None, temperature: float = 0.2) -> Dict[str, Any]:
    raw = chat(system_prompt, user_content, model=model, temperature=temperature)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Failed to parse JSON from model response: {exc}\nRaw response: {raw}")

