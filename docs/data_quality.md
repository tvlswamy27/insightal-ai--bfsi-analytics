# Phase 6: Data Quality Pipeline

## Purpose
The Phase 6 Data Quality Pipeline assesses the readiness and trustworthiness of the synthetic data generated in Phase 4 and loaded into MySQL in Phase 5. It acts as a safety gate for downstream analytics, ML, and reporting.

## Architecture
- **Configuration**: Defined in `config/data_quality_config.yaml`. Sets baseline metrics, severity mappings, threshold targets, and dimension weights for the overall score.
- **SQL Rules**: Defined in `sql/13_data_quality_checks.sql`. Highly optimized rule-based assertions.
- **Audit Table**: Results persist in `insightal_staging.data_quality_results`. The creation (`sql/12_create_data_quality_audit.sql`) is idempotent.
- **Orchestration**: `scripts/run_data_quality.py`. It blends SQL evaluations and Pandas-based statistical evaluations.

## Data Quality Dimensions
1. **Completeness**: Checks for unexpectedly NULL fields while respecting intentional NULLs (like fallback lacking `detected_intent_key`).
2. **Uniqueness**: Asserts that primary keys and certain composites are truly unique.
3. **Validity**: Asserts standard bounds (e.g. valid age ranges, boolean fields).
4. **Consistency**: Asserts temporal logic (durations matching start/end boundaries, positive durations).
5. **Referential Integrity**: Double-checks physical FKs and logical orphans.
6. **Business Rules**: Ensures complex conditions like PTP vs payments are maintained.
7. **Statistical Checks**: Non-destructive anomaly detection for rates like Escalation, Resolution, and PTP (compared against approved baselines).
8. **Reconciliation**: Proves raw source counts match final analytics counts including quarantines.

## Severity Model
- **CRITICAL**: Failing reconciliation, broken referential integrity, impossible business rules. Yields a final pipeline FAIL.
- **HIGH**: Significant completeness misses or domain violations. Yields a final pipeline FAIL.
- **MEDIUM**: Suspicious distributions or relationship anomalies.
- **LOW**: Minor anomalies.
- **INFO**: Standard metrics passing within limits.

## Execution
Run `python scripts/run_data_quality.py`

Exit Code `0`: Pipeline PASS or WARN.
Exit Code `1`: Pipeline FAIL due to CRITICAL/HIGH errors.

## Limitations
- Synthetic anomaly correlation checks are observational (WARN level) rather than strict rules because some synthetic variations are intentionally messy.
- Relies on MySQL running securely with `InnoDB`.
