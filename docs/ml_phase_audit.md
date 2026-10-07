# ML Phase Audit: Escalation Prediction

## 1. Current Repository Structure
The repository is well-structured and contains artifacts from all 9 previous completed phases. Key directories include:
- `docs/`: Contains specifications, architecture, and data dictionary.
- `python/`: Contains EDA modules (`python/eda/`).
- `sql/`: Contains raw, staging, and analytics layer SQL scripts.
- `reports/`: Contains validation and EDA outputs (`data_quality_results.json`, `eda_results.json`).
- `Insightal_AI_BFSI_Analytics.Report/` & `Insightal_AI_BFSI_Analytics.SemanticModel/`: Power BI assets.
- `pbix_unzipped/`, `notebooks/`, `scripts/`, `data/`, etc.

## 2. Existing ML-Related Assets
- `python/eda/12_ml_readiness.py`: Identifies allowed vs. prohibited fields for ML and explicitly outlines leakage risks.
- `docs/data_dictionary.md`: Contains a robust specification of field timing ("ML Elig" and "Leakage" columns) ensuring point-in-time validity.
- `reports/eda_results.json`: Contains insights on data distribution that can be used to inform ML expectations.

## 3. Available Source Fields
According to `12_ml_readiness.py` and `docs/data_dictionary.md`, the following fields are available prior to the prediction point:
**Current-Call Point-in-Time:**
- `detected_intent_key`, `confidence_score`, `sentiment`, `sentiment_score`
- `fallback_count_so_far`, `turn_count_so_far`, `call_duration_so_far`, `turn_number`, `speaker`

**Historical Pre-Call:**
- `bot_version`, `language` (from `dim_bot`)
- `campaign_key`, `campaign_type` (from `dim_campaign`)
- `dpd_bucket_at_call`, `days_past_due_at_call`, `risk_segment_at_call`, `outstanding_amount_at_call`
- `previous_call_count`, `previous_escalation_count`, `previous_fallback_count`
- Customer demographics: `age_group`, `gender`, `region`, `customer_segment`, `loan_type`

## 4. Potential Prediction Units
Since we are predicting escalation risk *during* an active call, the prediction unit should be a snapshot of the interaction. 
**Options:**
1. **Per-Turn (Continuous Evaluation):** Evaluate the risk at every customer turn.
2. **Fixed-Point Snapshot (e.g., After Turn 3):** Evaluate risk after exactly 3 customer turns.
3. **Elapsed-Time Snapshot:** Evaluate after a fixed duration (e.g., 30 seconds).
**Recommendation:** A fixed-point snapshot (e.g., after the 3rd customer turn) is highly defensible, easier to model with tabular data, and aligns well with the "early human intervention" objective. 

## 5. Candidate Features
- **Conversation State:** `running_confidence_score`, `current_turn_sentiment`, `fallback_count_so_far`, `call_duration_so_far`
- **Customer Profile:** `age_group`, `customer_segment`, `loan_type`
- **Historical Risk:** `previous_escalation_count`, `previous_fallback_count`
- **Context:** `days_past_due_at_call`, `risk_segment_at_call`

## 6. Leakage Risks
The most critical risk is **Target Leakage**. Prohibited fields include:
- `escalation_flag` (The target)
- `escalation_trigger_flag`
- `expected_intent_key` (Ground truth, not known by bot)
- `resolution_flag`, `task_completed_flag`, `containment_flag`
- `ptp_flag`, `payment_status`, `payment_amount`
- `call_status`, `hangup_reason`
- Aggregate end-of-call stats (e.g., final `confidence_score` or total `call_duration_seconds` instead of the running count).

## 7. Missing Information
- An explicit point-in-time extraction script is missing. The current `fact_conversation` and `fact_calls` describe the final state of the call. We must dynamically calculate point-in-time rolling features (e.g., `fallback_count_so_far`) during the ML dataset generation step.
- The chronological ordering of calls for historical customer features (e.g., `previous_escalation_count`) needs a precise SQL/Python window function implementation.

## 8. Recommended ML Architecture
A dedicated `ml/` folder cleanly separating ML lifecycle components:
- `data/`: Extracted datasets
- `features/`: Engineered features
- `models/`: Saved artifacts
- `evaluation/`: Output metrics
- `explainability/`: SHAP/importance reports
- Pipelines structured as modular Python scripts.

## 9. Files That Should Be Created
- `docs/ml_escalation_prediction_specification.md`
- `docs/ml_feature_dictionary.md`
- `ml/01_prepare_ml_dataset.py`
- `ml/02_feature_engineering.py`
- `ml/03_leakage_audit.py`
- `ml/04_train_baseline.py`
- `ml/05_train_candidate_models.py`
- `ml/06_evaluate_models.py`
- `ml/07_threshold_analysis.py`
- `ml/08_explain_model.py`
- `ml/run_ml_pipeline.py`
- Reports in `reports/` (e.g., `ml_dataset_report.json`, `ml_leakage_report.json`, etc.)

## 10. Files That Must Remain Untouched
- All files in `Insightal_AI_BFSI_Analytics.Report/` and `Insightal_AI_BFSI_Analytics.SemanticModel/`
- Existing SQL scripts in `sql/`
- Existing EDA scripts in `python/eda/`
- Synthetic data generation scripts and raw data
- Project data models and architectural guidelines
