# Results Quality Analysis and Remediation Plan

## Context
The supplied artifacts (analysis summary JSON, consulting report, slides outline, and token usage snapshot) show a functioning reporting pipeline that produces machine-readable and human-facing outputs. However, there are notable inconsistencies and missing provenance that reduce trust in the deliverables.

## Key Issues
1. **Numeric drift between artifacts**: KPI and category figures in the markdown reports do not match the JSON summary values, indicating the sources are not synchronized.
2. **Inconsistent LTV and revenue statistics**: Lifetime value and revenue aggregates conflict across files, creating factual mismatches for stakeholders.
3. **Rounding and presentation gaps**: Markdown content sometimes uses rounded or illustrative numbers that differ from the authoritative dataset.
4. **Missing run provenance**: Outputs lack embedded metadata (timestamp, dataset version/hash, git commit, model name, token counts), making it hard to verify when and how artifacts were produced.
5. **No automated consistency validation**: There is no evidence of checks that confirm markdown content matches the JSON summary or that referenced chart files exist.
6. **Staleness/overwrites risk**: Differences suggest manual edits or regeneration from different data snapshots, undermining reproducibility.

## Recommended Fixes
- **Single source of truth for numbers**: Generate markdown reports directly from the JSON summary (or a shared data model) using templates to eliminate manual edits and drift.
- **Add consistency checks**: Implement automated tests/CI steps that compare key metrics between JSON and generated markdown, and fail if discrepancies exceed tolerance.
- **Standardize rounding rules**: Define and apply consistent rounding/formatting for KPIs across all artifacts so stakeholder-facing numbers match programmatic outputs.
- **Embed provenance metadata**: Record run timestamp, dataset checksum or version, git commit hash, model name, and token usage inside both JSON and markdown artifacts.
- **Verify chart assets**: During generation and in CI, assert that each chart referenced in JSON/markdown exists and is updated in the output directory.
- **Guard against stale content**: Store generated artifacts in a dedicated output directory, clear it before each run, and avoid manual edits by regenerating from source data as part of the pipeline.

## Next Steps (Implemented)
1. Add a report-generation step that consumes the JSON summary and renders markdown/slides via templates, ensuring numerical parity.
   - Implemented via `scripts/generate_reports.py` and shared Jinja templates in `templates/`.
2. Create validation scripts (and CI jobs) to diff JSON metrics versus markdown and to check chart file presence.
   - Implemented via `scripts/validate_artifacts.py`, checking KPI parity, category totals, chart references, and provenance fields.
3. Extend the JSON schema to include provenance fields and surface the same metadata in markdown headers/footers.
   - Implemented via `reporting.provenance.load_summary_with_provenance`, which enriches JSON and makes metadata available to templates.
4. Define rounding/formatting utilities used by both data export and markdown rendering.
   - Implemented via `reporting.rounding`, with filters registered for template use.
5. Update developer docs to require regeneration of reports from source data and to prohibit manual edits to generated artifacts.
   - Implemented in the updated `README.md` under "Conventions" and "Getting Started".
