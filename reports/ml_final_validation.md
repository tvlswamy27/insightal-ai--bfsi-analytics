# Final ML Validation Report

## 1. Overview
This report contains the final analytical validation of the champion model (Logistic Regression) developed for the Insightal AI Escalation Prediction task. 

## 2. Dataset Summary
- **Total Rows:** 3,426
- **Train Split:** 2,398
- **Validation Split:** 514
- **Test Split:** 514
- **Target Rate:** 40.11% positive (`escalation_after_t3`)

## 3. Champion Model
**Logistic Regression** remains the champion model.
- **Baseline Metrics (Test):**
  - ROC-AUC: 0.959
  - PR-AUC: 0.954
  - Precision: 0.883
  - Recall: 0.867
  - F1: 0.875
  - Accuracy: 0.899
  - Brier Score: 0.074

## 4. Candidate Comparison summary
Random Forest was evaluated as a candidate model but failed to meaningfully outperform Logistic Regression on both validation and test sets. Furthermore, Random Forest showed signs of overfitting and poor calibration compared to the linear baseline. XGBoost was skipped because the package was not available in the controlled environment.

## 5. Explainability
SHAP was not available in the controlled environment; coefficient and permutation-based explanations were used.

*Note on Odds Ratios (Exponentiated Coefficients):* Numeric features were standardized before Logistic Regression fitting. Therefore, exponentiated coefficients for numeric variables represent the modeled odds multiplier associated approximately with a one-standard-deviation increase, holding other model inputs constant. For categorical features, they represent the modeled difference relative to the omitted/reference category, holding other model inputs constant.

### Top Global Positive Features (Increases Risk)
1. `fallback_count_t3`
2. `detected_intent_at_t3_6.0`
3. `detected_intent_at_t3_nan`
4. `detected_intent_at_t3_4.0`
5. `customer_segment_Wealth`

### Top Global Negative Features (Decreases Risk)
1. `detected_intent_at_t3_5.0`
2. `running_sentiment_score_t3`
3. `running_confidence_t3`
4. `detected_intent_at_t3_16.0`
5. `detected_intent_at_t3_3.0`

### Permutation Importance (Top 5 on Validation)
1. `fallback_count_t3`
2. `running_confidence_t3`
3. `running_sentiment_score_t3`
4. `attempt_number`
5. `days_past_due_at_call`

## 6. Error Analysis (Test Set, Threshold=0.50)
- **True Positives (TP):** 182 (Median fallback: 2.0)
- **True Negatives (TN):** 280 (Median fallback: 0.0)
- **False Positives (FP):** 24 (Median fallback: 1.0)
- **False Negatives (FN):** 28 (Median fallback: 1.0)
False negatives tend to have lower fallback counts than true positives, leading the model to underestimate escalation risk when fallbacks are absent.

## 7. Threshold Analysis (Validation Set)
- **0.30 Threshold:** Precision=0.783, Recall=0.887, Flagged Rate=44.7%
- **0.50 Threshold:** Precision=0.887, Recall=0.813, Flagged Rate=36.2%
- **0.70 Threshold:** Precision=0.930, Recall=0.724, Flagged Rate=30.7%

## 8. Risk Bands (Test Set)
- **Low (<0.30):** 52.5% of calls (Actual rate: 6.3%)
- **Moderate (0.30-0.50):** 7.4% of calls (Actual rate: 28.9%)
- **High (0.50-0.70):** 6.6% of calls (Actual rate: 58.8%)
- **Very High (>=0.70):** 33.5% of calls (Actual rate: 94.2%)

## 9. Calibration
The model demonstrates good calibration on the temporal test set, with a Brier score of 0.074 and predicted probabilities that track observed escalation rates reasonably well across the evaluated probability bins.

## 10. Robustness
- **Primary Evaluation (Temporal Test ROC-AUC):** 0.959
- **Secondary Evaluation (Customer-Disjoint CV ROC-AUC):** 0.956
The small difference between temporal test ROC-AUC (0.959) and customer-disjoint cross-validation ROC-AUC (0.956) provides supporting evidence that performance is not primarily dependent on repeated customer identities.

## 11. Leakage Audit
- Target absent from X: **True**
- Identifiers absent from X: **True**
- Prohibited fields absent: **True**
- Test predictions generated after fitting: **True**

## 12. Limitations
- Model only applies to calls reaching the 3rd customer turn.
- Does not predict escalation prior to T3.

## 13. Synthetic-Data Disclosure
Trained on synthetic data. Importances reflect synthetic data generation logic, not biological or sociological causal facts.

## 14. Artifact Inventory
- **Model Card:** `docs/ml_model_card.md`
- **Validation Script:** `ml/08_final_validation.py`
- **Figures:** `artifacts/ml/figures/*.png` (Coefficients, Permutation, Errors, Calibration, Trade-offs)

## FINAL RECOMMENDATION
**FINAL MODEL:** Logistic Regression

**WHY:**
- highest evaluated test ROC-AUC (0.959)
- highest evaluated test PR-AUC (0.954)
- highest evaluated test F1 (0.875)
- best Brier score among evaluated models (0.074)
- simpler than Random Forest
- interpretable coefficients
- strong chronological generalization

The Logistic Regression model is the preferred candidate for this synthetic portfolio project based on the evaluated temporal holdout performance, calibration, interpretability, and simplicity. Further real-world validation would be required before production deployment.
