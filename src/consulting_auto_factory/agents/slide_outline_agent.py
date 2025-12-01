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

    def generate_outline(self, report_markdown: str) -> SlideDeckOutline:
        try:
            payload = llm_client.chat_json(SLIDE_PROMPT, report_markdown, model=self.model, temperature=self.temperature)
            return SlideDeckOutline(**payload)
        except Exception:
            slides = [
                Slide(
                    title="Executive summary",
                    bullets=["Overall performance overview", "Highlights of revenue and churn"],
                    visual="Line chart of revenue by month",
                ),
                Slide(
                    title="Opportunities",
                    bullets=["Invest in top categories", "Focus retention on at-risk segments"],
                    visual="Bar chart of top categories",
                ),
            ]
            return SlideDeckOutline(slides=slides, overview="Auto-generated offline outline")

