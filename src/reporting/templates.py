"""Template rendering utilities for markdown and slide outlines."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

from .rounding import register_jinja_filters


def build_environment(template_dir: Path) -> Environment:
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False, trim_blocks=True, lstrip_blocks=True)
    register_jinja_filters(env)
    return env


def render_template(env: Environment, template_name: str, context: Dict[str, Any], output_path: Path) -> None:
    template = env.get_template(template_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template.render(**context), encoding="utf-8")
