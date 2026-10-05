# Model Card — Insightal AI Escalation Prediction

## 1. Model Purpose
The objective of this model is to proactively predict whether a BFSI customer service interaction will result in an escalation event. By identifying high-risk calls early, the system can enable timely human intervention, routing adjustments, or dynamic dialogue policy changes.

## 2. Business Problem
Unresolved queries, frustration, and eventual escalations drive operational costs up and reduce customer satisfaction (CSAT), especially in sensitive BFSI areas (collections, loan support). Anticipating escalation allows pre-emptive resolution.

## 3. Prediction Point
Immediately after the **3rd customer turn**. This provides a fixed-point evaluation.

## 4. Target Definition
`escalation_after_t3` = 1 if an escalation event occurs strictly after the 3rd customer turn. Calls escalating at or before T3 are excluded.

## 5. Dataset
- **Name:** `ml_dataset_t3.csv`
- **Rows:** 3,426 eligible snapshots
- **Target Rate:** 40.11% positive
- **Features:** 20 (10 Numeric, 10 Categorical)

## 6. Data Split
Strict chronological ordering:
- **Train:** Jan 1, 2026 – May 1, 2026 (2,398 rows)
- **Validation:** May 1, 2026 – May 31, 2026 (514 rows)
- **Test:** May 31, 2026 – Jun 30, 2026 (514 rows)

## 7. Feature Groups
- Conversation Dynamics (e.g., fallback count, running sentiment, running confidence, duration).
- Customer Profile (e.g., age group, risk segment, customer segment).
- Loan & Financials (e.g., outstanding amount, DPD bucket, loan type).
- Historical context (e.g., previous calls, previous escalations).

## 8. Leakage Controls
- Excluded future fields (`call_duration_seconds`, `containment_flag`, `resolution_flag`, etc.).
- Point-in-time calculation enforced.
- Training set strict cutoff ensures no future lookahead.
- Preprocessor fit strictly on Train.

## 9. Champion Model
**Logistic Regression.** Chosen after a rigorous comparison with a non-linear candidate (Random Forest). XGBoost was unavailable in the controlled environment.

## 10. Baseline Performance (Logistic Regression)
*(Metrics on Training set are omitted to focus on out-of-sample generalization)*

## 11. Validation Performance
- **ROC-AUC:** 0.949
- **PR-AUC:** 0.941
- **F1:** 0.848
- **Brier Score:** 0.083

## 12. Test Performance
- **ROC-AUC:** 0.959
- **PR-AUC:** 0.954
- **Precision:** 0.883
- **Recall:** 0.867
- **F1:** 0.875
- **Accuracy:** 0.899
- **Brier Score:** 0.074

## 13. Calibration
The model demonstrates good calibration on the temporal test set, with a Brier score of 0.074 and predicted probabilities that track observed escalation rates reasonably well across the evaluated probability bins.

## 14. Explainability
- **Numeric Features:** Numeric features were standardized before Logistic Regression fitting. Therefore, exponentiated coefficients for numeric variables represent the modeled odds multiplier associated approximately with a one-standard-deviation increase, holding other model inputs constant.
- **Categorical Features:** Modeled difference relative to the omitted/reference category, holding other model inputs constant.
- **Top Positive Drivers (Increases Risk):** High `fallback_count_t3`, specific intent mappings (e.g., `detected_intent_at_t3_6.0`), and late DPD buckets (`90+`).
- **Top Negative Drivers (Decreases Risk):** High `running_confidence_t3`, positive `running_sentiment_score_t3`, and specific campaign types (e.g., `Insurance Renewal`).
- *SHAP was not available; coefficients and permutation importance were used.*

## 15. Error Analysis
False negatives generally exhibited much lower fallback counts (median=1.0) compared to true positives (median=2.0). The model successfully learned that lower fallbacks correspond to lower risk, but occasionally missed non-fallback-driven escalations.

## 16. Threshold Analysis
- **Low Threshold (0.30):** High recall (88.7%), more flagged conversations (44.7%), higher false positive rate.
- **High Threshold (0.60):** Lower recall (76.8%), fewer flagged conversations (33.3%), higher precision (91.2%).
- *A final operational threshold requires a business cost matrix.*

## 17. Risk Bands
Test Set Distribution:
- **Low (<0.30):** 52.5% of calls (6.3% actual escalation rate)
- **Moderate (0.30-0.50):** 7.4% of calls (28.9% actual escalation rate)
- **High (0.50-0.70):** 6.6% of calls (58.8% actual escalation rate)
- **Very High (>=0.70):** 33.5% of calls (94.2% actual escalation rate)

## 18. Robustness
Primary evaluation uses chronological train/validation/test separation. A secondary customer-disjoint GroupKFold analysis produced ROC-AUC of 0.956 compared with the temporal test ROC-AUC of 0.959. This small difference provides supporting evidence that performance is not primarily dependent on repeated customer identities.

## 19. Limitations
- The model only applies to calls that reach the 3rd customer turn.
- It does NOT predict escalation for calls that end before T3.
- It does NOT apply to calls that escalate at or before T3.

## 20. Synthetic-Data Disclosure
This model was trained on synthetic data. Importance values reflect synthetic data generation logic and structural correlations, not biological or sociological causal facts.

## 21. Intended Use
To pilot proactive mitigation strategies in a controlled portfolio environment based on T3 behavioral snapshots.

## 22. Non-Intended Use
- Predicting outcomes at Call Start (T0).
- Fully autonomous interventions without a fallback business policy.
- Applying outside the synthetic constraints of the Insightal AI simulation.

## 23. Deployment Considerations
The model requires a real-time feature generation pipeline that computes `fallback_count_t3`, `running_confidence_t3`, and `running_sentiment_score_t3` seamlessly at the exact moment Turn 3 concludes.
