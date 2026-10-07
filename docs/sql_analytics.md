# Phase 7 — SQL Analytics Engine

## 1. Phase 7 Objective
Build a professional, interview-defensible SQL Analytics Layer against the hardened `insightal_analytics` schema. This phase demonstrates strong SQL, business analysis, BFSI domain understanding, and structured analytics engineering by querying dimensional models.

## 2. Database Grain
- `fact_calls`: **One row per complete voice call.** Aggregation requires counting/summing across `call_key`.
- `fact_conversation`: **One row per conversation turn.** Aggregation at the call level must group by `call_key` first before joining back to `fact_calls` to avoid fan-out duplication.

## 3. Analytical Architecture
The analytics layer relies on 13 modular SQL files located in `sql/analytics/`, executed securely via `scripts/run_sql_analytics.py` to produce standard reporting JSON and validate SQL structural constraints.

## 4. Query Catalog

| Query ID | Category | Business Question | SQL Technique | Output Grain |
|----------|----------|-------------------|---------------|--------------|
| EXE-001 | Executive KPIs | What are the top-level executive KPIs? | CROSS JOIN, Aggregation | Single Row |
| OPS-001 | Call Operations | How do connection statuses and hangups distribute? | GROUP BY, SUM() OVER | By Status/Reason |
| OPS-002 | Call Operations | What is the distribution of outreach attempts? | GROUP BY | By Attempt |
| BOT-001 | Bot Performance | Which bots perform best overall? | Multiple CTEs | By Bot |
| INT-001 | Intent Analytics | Which intents are recognized with the highest/lowest accuracy? | Conditional Aggregation | By Expected Intent |
| JRN-001 | Customer Journey | Where do customers drop off in the journey? | Conditional Aggregation | Funnel Stages |
| ESC-001 | Escalation | What factors are associated with escalation? | JOIN, GROUP BY | By Segment |
| COL-001 | Collections | How do collections campaigns perform by DPD bucket? | WHERE filter | By DPD Bucket |
| CMP-001 | Campaign | How do campaigns compare across volume/outcome metrics? | JOIN, GROUP BY | By Campaign |
| SEG-001 | Segmentation | Which age groups engage most with the AI? | JOIN, GROUP BY | By Age Group |
| TME-001 | Time Series | What is the trend of call volume over time? | AVG() OVER (ROWS) | By Day |
| ROI-001 | ROI | What is the cost avoidance of automated calls? | CTE | Single Row |
| ADV-001 | Advanced SQL | Escalation trajectory for repeat callers? | ROW_NUMBER, LEAD | By Call |
| VAL-001 | Validation | Any fan-out or missing intent definitions? | Subqueries | By Check |


## 5. Clean Analytics Population
- **Phase 4 generated baseline**: 10,000 calls
- **Current clean analytics population**: 9,885 calls

The difference is caused by Phase 5 quarantine of anomalous records. Therefore, Phase 7 KPI values describe the CLEAN ANALYTICS POPULATION and should not automatically be interpreted as identical to the Phase 4 raw baseline. Specifically, the current **Average Call Duration = 36.56 seconds** represents the clean analytics population metric and is not artificially adjusted toward the old baseline.

## 6. Important Assumptions and Definitions

- **Intent Recognition Accuracy**: Denominator only includes customer turns where `expected_intent_key` is non-null AND `detected_intent_key` is non-null AND `speaker = 'Customer'`. Bot turns and unknown intents are exclusively excluded.
- **Bot Quality Score (Project Defined)**: 30% Containment + 25% Task Completion + 20% Intent Recognition + 15% Satisfaction Proxy + 10% Reliability.
- **Satisfaction Proxy (Project Defined)**: 40% Resolution + 30% Containment + 20% Normalized Sentiment + 10% Task Completion.
- **Business Impact**:
  - Average Human Agent Call = 300 seconds.
  - Productive FTE Hours = 6 hours (21,600s) / day.
  - Cost per call = ₹50.
- **Collections Filtering**: All collections metrics strictly filter for `campaign_type = 'Loan Collections'`.

## 6. Validation Results
Automated validation successfully verifies that:
- Customer level aggregation matches total distinct facts.
- No fan-out occurs during fact-to-fact joins.
- Collections rules are securely filtered.
- Unexpected NULLs in dimensional keys (caught during Phase 6) do not appear in aggregations.

## 7. Interview Talking Points
- **NULL-Safe Joins**: Explicitly handling NULL dimensions during ETL guarantees accurate denominator calculations in SQL.
- **Window Functions**: Implementing `ROW_NUMBER()`, `LEAD()`, and `AVG() OVER()` handles time-series trends and sequence analysis effectively.
- **Conditional Aggregation**: Utilizing `SUM(CASE WHEN...)` allows clean pivoted funnel stages without excessive sub-queries.
- **Grain Awareness**: Careful CTE modeling prevents duplicating `fact_calls` when evaluating `fact_conversation` intent accuracies.
