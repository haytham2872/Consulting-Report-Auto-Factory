# Consulting Report Auto Factory

Utilities to generate synchronized consulting reports, slide outlines, and machine-readable summaries from the same data source.

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Prepare `analysis_summary.json` in `reports/` (or another path).
3. Generate artifacts with provenance metadata:
   ```bash
   python scripts/generate_reports.py reports/analysis_summary.json reports/ --write-json --model-name claude-3-haiku --token-in 1645 --token-out 2822
   ```
4. Validate that markdown outputs stay aligned with the JSON and referenced charts:
   ```bash
   python scripts/validate_artifacts.py reports/analysis_summary.json reports/consulting_report.md reports/slides_outline.md
   ```

## Conventions
- Markdown and slide outputs are **generated artifacts**; do not hand-edit them. Regenerate from the JSON source when inputs change.
- Provenance fields (timestamp, dataset hash, git commit, model, token counts) are embedded in all artifacts to ensure reproducibility.
- Rounding/formatting is centralized in `src/reporting/rounding.py` and used across templates for numerical parity.

## Files & Directories
- `scripts/generate_reports.py`: Renders consulting report and slide outline from JSON via Jinja templates, injecting provenance metadata.
- `scripts/validate_artifacts.py`: CI-friendly validator that checks KPI parity, category totals, chart references, and provenance fields across markdown artifacts.
- `templates/`: Jinja templates shared by both report and slides.
- `src/reporting/`: Shared utilities for formatting, template rendering, and provenance handling.
- `docs/results_analysis.md`: Problem statement and remediation plan.
