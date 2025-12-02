from __future__ import annotations

from .. import llm_client
from ..models import Slide, SlideDeckOutline


SLIDE_PROMPT = """You are a management consultant turning a Markdown report into slide bullets.
Return JSON with 'slides': list of {title, bullets, visual, notes} and optional overview field.
Keep each slide to 3-5 bullets.
"""


class SlideOutlineAgent:
    def __init__(self, model: str | None = None, temperature: float = 0.4) -> None:
        self.model = model
        self.temperature = temperature

    def generate_outline(self, report_markdown: str, data_facts: str | None = None) -> SlideDeckOutline:
        prompt_content = report_markdown
        if data_facts:
            prompt_content += "\n\nData facts (use exactly):\n" + data_facts
        payload = llm_client.chat_json(
            SLIDE_PROMPT,
            prompt_content,
            model=self.model,
            temperature=self.temperature,
            max_tokens=500,
        )
        return SlideDeckOutline(**payload)

