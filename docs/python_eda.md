# Phase 8 Python EDA

## 1. Phase Objective
Build a professional, reproducible Python EDA layer against MySQL database.

## 2. Business Questions
Understand task completion, conversational AI accuracy, collections performance, and escalation patterns.

## 3. Data Source
MySQL database `insightal_analytics`.

## 4. Dataset Population
fact_calls: 9885, fact_conversation: 38978, customers: 1976.

## 5. Data Model
Star schema from Phase 5.

## 6. Methodology
Extract to Pandas, analyze via Scipy, visualize via Matplotlib. Descriptive and diagnostic EDA. No predictive model is trained in Phase 8.

## 7. Data Quality
See validation rules in `run_eda.py`. 0 failed checks.

## 8. Univariate Analysis
Analyzed distributions of call_duration_seconds, attempt_number, confidence_score, outstanding_amount_at_call, days_past_due_at_call, ptp_amount, payment_amount.

## 9. Bivariate Analysis
Analyzed relationships between attempts, duration, escalation, ptp. Call duration correlates with attempts.

## 10. Conversational AI Analysis
Intent accuracy denominator correctly filtered to customer turns. Overall accuracy: 0.83.

## 11. Customer Journey
Identified task dropoffs. Tasks started: 6183, completed: 3520.

## 12. Escalation Association Analysis
Escalation analyzed at call level using `escalation_flag`. Average confidence and sentiment both show patterns in escalation rates.

## 13. Collections Analysis
Analyzed Loan Collections campaign specifically. PTP rate: 0.08.

## 14. Customer Behavior
Generated metrics on repeat callers. Total calls across customers: 9885.0.

## 15. Temporal Analysis
Daily, rolling 7-day, weekly, and monthly trends analyzed. Weekly volume shows specific seasonal variance.

## 16. Correlation Analysis
Used Spearman and Point-Biserial on numeric variables. Found valid descriptive correlations without implying causality.

## 17. Outlier Analysis
IQR used to bound outliers without deleting them.

## 18. Statistical Tests
Mann-Whitney U and Chi-Square evaluated. 3 tests performed.
- **Mann-Whitney U** (Confidence (Low/High) -> Fallback): n=19457, statistic=61530857.0000, p < 0.0001, Statistically significant association at alpha=0.05. Assumption: Independent two-group comparison; sufficient observations in both groups.
- **Chi-Square** (Risk Segment -> PTP): n=2843, statistic=177.2768, p < 0.0001, Statistically significant association at alpha=0.05. Assumption: Expected cell frequencies checked; test applicable.
- **Chi-Square** (Call-Level Sentiment -> Escalation): n=6178, statistic=2117.7485, p < 0.0001, Statistically significant association at alpha=0.05. Assumption: Expected cell frequencies checked; test applicable.

## 19. ML Readiness
All point-in-time features documented. Full-call aggregates may contain future information relative to an early-call prediction timestamp and therefore must not automatically be used as Phase 10 point-in-time features.

## 20. Leakage Controls
Prohibited fields properly identified as leakage_risk=True.

## 21. Key Findings
- **Customer Journey**: Task completion is lower than task initiation. (Evidence: 6183 calls started tasks and 3520 completed them.)
- **Collections**: PTP rates vary by Risk Segment. (Evidence: Tested on 2843 collections rows with valid risk segments.)
- **Conversational AI**: Fallback rate differs by confidence. (Evidence: Mann-Whitney U test shows significant separation in fallback incidence between low and high confidence subsets.)
- **Operations**: Escalation events represent a subset of connected interactions. (Evidence: Overall escalation rate is 22.7%.)
- **Customer Behavior**: Repeat callers are present in the customer base. (Evidence: 9885.0 calls made by 1976 customers.)
- **Temporal Trends**: Volume fluctuates week-to-week. (Evidence: Weekly volume metrics show distinct variances across the dataset timeline.)
- **Escalation Association**: Call duration positively associates with escalation. (Evidence: Spearman correlation and quantile breakdowns demonstrate higher escalation rates in longer calls.)
- **ML Readiness**: Leakage fields appropriately isolated. (Evidence: Prohibited POST-CALL features are restricted in the ml_readiness inventory.)

## 22. Limitations
Observational data. Findings do not establish causality.

## 23. Synthetic Data Disclosure
This project uses synthetic/anonymized data for portfolio and analytical demonstration purposes.

## 24. Reproducibility
Run `python python/eda/run_eda.py`.
