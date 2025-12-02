from __future__ import annotations

import json
from pathlib import Path

import typer

from .orchestrator import plan_only, run_pipeline

app = typer.Typer(help="Consulting Report Auto-Factory")


@app.command()
def run(
    input_dir: Path = typer.Option("data/input", help="Directory with input CSVs"),
    brief_path: Path = typer.Option(
        "config/business_brief.txt", "--brief", "--brief-path", help="Business brief text file"
    ),
    reports_dir: Path = typer.Option("reports", help="Output directory for reports"),
):
    """Run the full multi-agent pipeline and generate reports."""
    run_pipeline(str(input_dir), str(brief_path), str(reports_dir))
    typer.echo(f"Reports written to {reports_dir}")


@app.command("show-plan")
def show_plan(
    input_dir: Path = typer.Option("data/input", help="Directory with input CSVs"),
    brief_path: Path = typer.Option(
        "config/business_brief.txt", "--brief", "--brief-path", help="Business brief text file"
    ),
):
    """Preview the analysis plan without running the full pipeline."""
    plan = plan_only(str(input_dir), str(brief_path))
    typer.echo(json.dumps(plan.model_dump(), indent=2))


if __name__ == "__main__":
    app()
