# Consulting Report Auto-Factory

Consulting Report Auto-Factory is a Python-based **agentic multi-agent pipeline** that reads business CSV data and a short brief, autonomously plans analyses using LLM tool-calling, generates KPIs and tables, and writes a professional consulting-style report. It demonstrates advanced agentic AI capabilities for automated business intelligence and consulting deliverables.

## Architecture

```
+-----------------+       +-----------------+       +--------------------+       +-------------------+
|   Data Loader   | --->  |  PlannerAgent   | --->  | DataAnalystAgent   | --->  |  InsightsAgent    |
| (CSV + schema)  |       | (LLM plan JSON) |       | (Tool-using Agent) |       | (Report Markdown) |
+-----------------+       +-----------------+       +--------------------+       +-------------------+
                                                             |
                                                             v
                                                    +------------------+
                                                    |  Analysis Tools  |
                                                    | - Revenue stats  |
                                                    | - Top categories |
                                                    | - Churn metrics  |
                                                    | - Time series    |
                                                    | - LTV analysis   |
                                                    +------------------+
```

### Agentic Capabilities

The **DataAnalystAgent** operates in **agentic tool-using mode** where:
- The LLM autonomously decides which analyses to perform based on the business brief
- Uses Claude's native tool-calling API to execute analysis functions
- Dynamically explores dataframe structures using `get_dataframe_summary`
- Strategically selects and chains analysis tools (revenue, categories, churn, time series, LTV)
- Adapts to different data structures without hardcoded logic
- Performs multi-turn reasoning to gather comprehensive insights

This is a significant advancement over traditional hardcoded analysis pipelines.

## Quickstart

Requirements: Python 3.11+

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -r requirements.txt
pip install -e .
cp .env.example .env  # and set ANTHROPIC_API_KEY
```

The editable install registers the `consulting-auto-factory` CLI. By default the agents call Anthropic Claude (`claude-3-haiku-20240307` unless you override `CONSULTING_FACTORY_MODEL`). Set `ANTHROPIC_API_KEY` before running commands.

### Web UI (Recommended)

Launch the interactive web interface with professional design:

```bash
streamlit run app.py
```

The web UI provides:
- **Drag-and-drop file upload** for CSV files with visual feedback
- **Interactive business brief editor** with real-time preview
- **Animated progress tracking** showing which agent is currently active
- **Beautiful report rendering** with professional color scheme
- **Tabbed results view** with Executive Report, Analytics Dashboard, and Export options
- **Download capabilities** for both Markdown and JSON outputs

See [WEBUI_GUIDE.md](WEBUI_GUIDE.md) for detailed usage instructions and demo tips.

### CLI Usage

Generate the sample dataset (already committed, but you can refresh it):

```bash
python scripts/generate_sample_data.py
```

Run the full pipeline:

```bash
consulting-auto-factory run --input-dir data/input --brief config/business_brief.txt --reports-dir reports
```

Outputs appear under `reports/`:
- `analysis_summary.json`: structured KPIs, plan, tables, and run metadata (timestamp, model, input file digests)
- `consulting_report.md`: client-ready narrative with executive summary, key findings, data tables, and actionable recommendations

Preview only the plan without running analysis:

```bash
consulting-auto-factory show-plan
```

## Project Structure

- `app.py`: Streamlit web UI (recommended interface)
- `src/consulting_auto_factory/`
  - `cli.py`: Typer CLI entrypoint
  - `orchestrator.py`: connects agents end-to-end
  - `llm_client.py`: Claude (Anthropic) chat helper with tool-calling support
  - `data_loader.py`: CSV loading and schema inference
  - `analysis_tools.py`: legacy pandas utilities (kept for backward compatibility)
  - `analysis_tools_v2.py`: **NEW** - tool definitions and functions for agentic mode
  - `models.py`: Pydantic data classes for type-safe agent communication
  - `agents/`: Planner, DataAnalyst, Insights agents
    - `planner_agent.py`: Creates analysis plan from brief and schemas
    - `data_analyst_agent.py`: **Agentic tool-using agent** that autonomously analyzes data
    - `insights_agent.py`: Generates consulting-style narrative report
- `data/input/`: sample CSVs (`orders.csv`, `customers.csv`)
- `config/business_brief.txt`: sample business brief
- `reports/`: generated outputs (git-ignored)
- `scripts/generate_sample_data.py`: refresh synthetic data
- `tests/`: unit tests for loader, tools, and CLI
- `.streamlit/`: UI theme configuration

## Agents Overview

### PlannerAgent
Reads data schemas and business brief, proposes structured `AnalysisPlan` with objectives and analysis steps.

### DataAnalystAgent (Agentic Tool-Using)
**The core innovation of this system.**

Operates in two modes:
- **Tool mode (default)**: Agentic LLM decides which analyses to perform using tool calling
- **Legacy mode**: Hardcoded pandas analysis (kept for backward compatibility)

In tool mode, the agent:
1. Receives the analysis plan and available dataframes
2. Uses `get_dataframe_summary` to understand data structure
3. Autonomously selects relevant tools: `compute_revenue_summary`, `analyze_top_categories`, `calculate_churn_metrics`, `compute_time_series`, `calculate_customer_ltv`
4. Executes multi-turn tool calls to gather comprehensive insights
5. Returns structured KPIs and tables

### InsightsAgent
Synthesizes analysis results into a professional consulting-style Markdown report with executive summary, key findings, data visualizations (tables), and actionable recommendations.

## Example Brief

```
We are an e-commerce retailer operating in Europe and North America.
This dataset contains orders over the past 18 months and a customer table.
We want to understand revenue trends, top segments, churn patterns, and identify opportunities to increase customer lifetime value.
```

The agentic system will autonomously decide to:
- Compute revenue statistics from orders
- Identify top product categories and regions
- Calculate customer churn rate
- Analyze monthly revenue trends
- Compute LTV distribution

## Current Limitations

While the system demonstrates strong agentic capabilities, there are known limitations:

1. **Data Format Constraints**
   - Currently only supports CSV input files
   - Expects tabular data (no support for JSON, XML, databases, or semi-structured data)
   - Limited automatic type inference

2. **Analysis Scope**
   - Tool set is focused on common business metrics (revenue, categories, churn, LTV, time series)
   - No statistical testing, forecasting, or ML model building
   - No automated data quality assessment or cleaning

3. **Visualization**
   - Generates tables but not charts/graphs
   - No interactive visualizations or dashboards
   - Results are text-based (Markdown + JSON)

4. **Infrastructure**
   - Requires Anthropic API key (no local LLM support)
   - Single-session only (no persistent storage or caching)
   - No user authentication or multi-user support
   - No containerization (Docker) provided

5. **Agent Limitations**
   - Maximum 10 tool-calling rounds to prevent runaway costs
   - No self-correction or error recovery mechanisms
   - No agent debate or multi-agent collaboration on analysis decisions

6. **Scalability**
   - In-memory pandas processing (not suitable for very large datasets)
   - No distributed computing support
   - Single-threaded execution

## Short-Term Improvement Objectives

Realistic next steps to enhance the system:

### 1. Visualization Generation (High Priority)
- Implement chart generation using matplotlib/plotly
- Add automated visualization selection based on data type
- Embed visualizations in reports (PNG/SVG)
- **Effort**: 2-3 days | **Impact**: High

### 2. Expanded Data Format Support
- Add Excel (.xlsx) file support
- Support JSON data input
- Implement database connectors (PostgreSQL, SQLite)
- **Effort**: 3-5 days | **Impact**: High

### 3. Enhanced Analysis Tools
- Add statistical significance testing
- Implement correlation analysis
- Add simple forecasting (moving averages, trend detection)
- Include outlier detection and data quality scoring
- **Effort**: 5-7 days | **Impact**: Medium-High

### 4. Docker Deployment
- Create Dockerfile for easy deployment
- Add docker-compose for local development
- Document cloud deployment (AWS, GCP, Azure)
- **Effort**: 1-2 days | **Impact**: Medium

### 5. Caching and Persistence
- Implement analysis result caching
- Add session persistence for web UI
- Store historical reports for comparison
- **Effort**: 2-3 days | **Impact**: Medium

### 6. Agent Self-Healing
- Add retry logic with exponential backoff
- Implement error detection and alternative analysis paths
- Add validation checks for tool outputs
- **Effort**: 3-4 days | **Impact**: Medium

### 7. Multi-Agent Collaboration
- Implement agent debate pattern (multiple DataAnalystAgents propose analyses)
- Add consensus mechanism for selecting best insights
- Create QualityReviewAgent to critique reports
- **Effort**: 5-7 days | **Impact**: High (demonstrates advanced agentic behavior)

### 8. Testing and Quality
- Expand test coverage to >80%
- Add integration tests for full pipeline
- Implement property-based testing for analysis tools
- **Effort**: 2-3 days | **Impact**: Medium

## Extending for Real Engagements

- Swap in domain-specific prompts or additional agents (e.g., RiskAgent, ComplianceAgent)
- Add more robust schema detection and data quality checks
- Plug into enterprise BI tools (Snowflake, dbt, Tableau) for data pipelines
- Host in a scheduler (Airflow, Prefect) to automate recurring reports
- Implement human-in-the-loop feedback for report refinement
- Add industry-specific analysis templates (finance, healthcare, retail)

## Why This Matters for AI Agents & Consulting

- **Demonstrates advanced agentic capabilities** with autonomous tool selection and multi-turn reasoning
- **Production-ready architecture** with clear separation of concerns (planning, analysis, synthesis)
- **Type-safe agent communication** using Pydantic models for reliable data exchange
- **Dual-mode operation** shows both cutting-edge (tool-using) and stable (legacy) approaches
- **Business value focus** - generates actual consulting deliverables, not just technical demos
- **Extensible design** - easy to add new tools, agents, or data sources

## Development

Run tests:
```bash
pytest
```

Run with different model:
```bash
export CONSULTING_FACTORY_MODEL=claude-3-5-sonnet-20241022
consulting-auto-factory run
```

## License

MIT License.
