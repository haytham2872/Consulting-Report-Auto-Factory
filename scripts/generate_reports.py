"""Generate markdown artifacts from the JSON summary using Jinja templates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any

from reporting.provenance import load_summary_with_provenance
from reporting.templates import build_environment, render_template


def _default_templates(template_dir: Path) -> Dict[str, str]:
    return {
        "consulting_report": "consulting_report.md.j2",
        "slides_outline": "slides_outline.md.j2",
    }


def generate(summary_path: Path, template_dir: Path, output_dir: Path, model_name: str | None = None, token_usage: Dict[str, int] | None = None, write_json: bool = False) -> None:
    data = load_summary_with_provenance(summary_path, model_name=model_name, token_usage=token_usage)
    env = build_environment(template_dir)
    templates = _default_templates(template_dir)

    context: Dict[str, Any] = {
        "summary": data,
        "kpis": data.get("kpis", {}),
        "top_categories": data.get("top_categories", []),
        "charts": data.get("charts", []),
        "metadata": data.get("metadata", {}),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    render_template(env, templates["consulting_report"], context, output_dir / "consulting_report.md")
    render_template(env, templates["slides_outline"], context, output_dir / "slides_outline.md")

    if write_json:
        summary_out = output_dir / "analysis_summary.json"
        summary_out.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate consulting artifacts from analysis summary JSON")
    parser.add_argument("summary", type=Path, help="Path to analysis_summary.json")
    parser.add_argument("output_dir", type=Path, help="Where to write generated artifacts")
    parser.add_argument("--templates", type=Path, default=Path("templates"), help="Directory containing Jinja templates")
    parser.add_argument("--model-name", dest="model_name", type=str, default=None, help="LLM model name used for generation")
    parser.add_argument("--token-in", dest="token_in", type=int, default=None, help="Input token count for the run")
    parser.add_argument("--token-out", dest="token_out", type=int, default=None, help="Output token count for the run")
    parser.add_argument("--write-json", action="store_true", help="Write a provenance-enriched JSON copy to the output dir")

    args = parser.parse_args()
    token_usage = None
    if args.token_in is not None or args.token_out is not None:
        token_usage = {"input_tokens": args.token_in or 0, "output_tokens": args.token_out or 0}

    generate(
        summary_path=args.summary,
        template_dir=args.templates,
        output_dir=args.output_dir,
        model_name=args.model_name,
        token_usage=token_usage,
        write_json=args.write_json,
    )


if __name__ == "__main__":
    main()
