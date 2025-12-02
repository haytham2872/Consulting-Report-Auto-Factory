# Consulting Report Auto-Factory

Consulting Report Auto-Factory is a Python-based multi-agent pipeline that reads business CSV data and a short brief, plans analyses, generates KPIs and charts, and writes a consulting-style report. It is designed to be realistic enough for a Deloitte AI Agents internship demo yet simple to run locally.

```
+-----------------+       +-----------------+       +----------------+       +-------------------+
|   Data Loader   | --->  |  PlannerAgent   | --->  | DataAnalystAgent| ---> |  InsightsAgent    |
| (CSV + schema)  |       | (LLM plan JSON) |       | (pandas + MPL) |       | (Report Markdown) |
+-----------------+       +-----------------+       +----------------+       +-------------------+
```

## Quickstart

Requirements: Python 3.11

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -r requirements.txt
pip install -e .
cp .env.example .env  # and set ANTHROPIC_API_KEY
```

The editable install registers the `consulting-auto-factory` CLI used in the commands below. By default the agents call Anthropic Claude (cost-effective `claude-3-haiku-20240307` unless you override `CONSULTING_FACTORY_MODEL`). Set `ANTHROPIC_API_KEY` before running commands.

Generate the sample dataset (already committed, but you can refresh it):

```bash
python scripts/generate_sample_data.py
```

Run the full pipeline:

```bash
consulting-auto-factory run --input-dir data/input --brief config/business_brief.txt --reports-dir reports

```

Outputs appear under `reports/`:
- `analysis_summary.json`: structured KPIs, plan, tables, charts, and run metadata (timestamp, model, input file digests)
- `charts/*.png`: matplotlib visuals
- `consulting_report.md`: client-ready narrative that reuses the same KPIs/tables/charts and metadata for consistency

Preview only the plan without running analysis:

```bash
consulting-auto-factory show-plan
```

## Project Structure

- `src/consulting_auto_factory/`
  - `cli.py`: Typer CLI entrypoint
  - `orchestrator.py`: connects agents end-to-end
  - `llm_client.py`: Claude (Anthropic) chat helper
  - `data_loader.py`: CSV loading and schema inference
  - `analysis_tools.py`: pandas utilities for KPIs
  - `charting.py`: matplotlib chart creators
  - `models.py`: Pydantic data classes
  - `agents/`: Planner, DataAnalyst, Insights agents
- `data/input/`: sample CSVs (`orders.csv`, `customers.csv`)
- `config/business_brief.txt`: sample brief
- `reports/`: generated outputs (git-ignored)
- `scripts/generate_sample_data.py`: refresh synthetic data
- `tests/`: unit tests for loader, tools, and CLI

## Agents Overview

- **PlannerAgent**: Reads schema + brief, proposes `AnalysisPlan` (objectives, steps).
- **DataAnalystAgent**: Executes generic business analyses using pandas, calculates KPIs, and produces charts.
- **InsightsAgent**: Produces a consulting-style Markdown report referencing generated visuals.

## Example Brief

```
We are an e-commerce retailer operating in Europe and North America.
This dataset contains orders over the past 18 months and a customer table.
We want to understand revenue trends, top segments, churn patterns, and identify opportunities to increase customer lifetime value.
```

## Extending in Real Engagements

- Swap in domain-specific prompts or additional agents (e.g., RiskAgent).
- Add more robust schema detection and data quality checks.
- Plug into BI tools (Snowflake, dbt) for enterprise data pipelines.
- Host the CLI in a scheduler (Airflow, Prefect) to automate recurring reports.

## Why this matters for AI agents & consulting

- Demonstrates a lightweight multi-agent architecture with clear tool usage.
- Separates planning, analysis, and insight generation steps.
- Uses structured Pydantic models for reliable data exchange between agents.

## License

MIT License.
