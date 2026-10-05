# ML Baseline Evaluation Report: Escalation Prediction

## 1. Objective
Establish a clean, robust baseline for the Escalation Prediction model using Logistic Regression. This provides a transparent understanding of linear relationships within the data before testing more complex ensemble models.

## 2. Prediction Point
The model evaluates the call exactly after the **3rd customer turn**. Calls that do not reach a 3rd customer turn, or escalate before/at this boundary, are excluded from the dataset.

## 3. Dataset
- **Version:** `ml/data/ml_dataset_t3.csv`
- **Total Eligible Calls:** 3,426
- **Target (`escalation_after_t3`):** 1,374 Positives (40.11%) / 2,052 Negatives
- **Training Set:** 2,398 rows
- **Validation Set:** 514 rows
- **Test Set:** 514 rows

## 4. Feature Engineering
Features include Conversation Context (running sentiment, confidence, and fallback counts strictly through T3), Call Metadata (campaign, bot version), Collections Context (DPD, outstanding amount), and Customer Historical Profile (aggregates from prior calls only).

## 5. Leakage Controls
A strict audit ensures no post-outcome variables (e.g., `resolution_flag`, `escalation_flag`) or ground-truth variables (`expected_intent_key`) entered the feature matrix.

## 6. Temporal Split
The data was split purely chronologically to prevent future information leakage and test actual real-world generalization:
- **Train:** Jan 1, 2026 - May 1, 2026
- **Validation:** May 1, 2026 - May 31, 2026
- **Test:** May 31, 2026 - Jun 30, 2026

## 7. Baseline Model
**Algorithm:** Logistic Regression (Scikit-Learn).
**Preprocessing:** Median imputation and Standard Scaling for numeric features. Constant ('Missing') imputation and One-Hot Encoding for categorical features.

## 8. Evaluation Methodology
Models are evaluated on probability calibration (Brier Score, ROC-AUC, PR-AUC) and threshold-dependent metrics (Precision, Recall, F1). A primary threshold analysis is run exclusively on the Validation set.

## 9. Results (Test Set @ Threshold 0.5)
*(Refer to `ml_baseline_report.json` for precise decimal values)*
- **ROC-AUC:** High capability to rank risk.
- **PR-AUC:** Strong performance on the positive class.
- **Precision / Recall / F1:** Calculated on the untouched test holdout.

## 10. Threshold Analysis
Tested thresholds from 0.30 to 0.70 on the Validation set to map the Precision-Recall trade-off. **Threshold selection deferred pending business cost trade-off.** (A default of 0.5 is used for point metrics).

## 11. Calibration
The predicted probabilities were evaluated for calibration. Logistic Regression natively produces well-calibrated probabilities, though slight deviations may exist.

## 12. Interpretability
Key risk drivers were extracted from the Logistic Regression coefficients. 
- **High Positive Risk:** Associated with specific campaign types, high running fallback counts, and negative running sentiment by T3.
- **High Negative Risk (Containment):** Associated with high running confidence by T3.

## 13. Limitations
The model only evaluates calls that survive to a 3rd customer turn. Early drops are outside the scope of this model.

## 14. Synthetic-Data Disclosure
This model is trained on a rigorously generated synthetic dataset. The learned feature importances reflect intentional synthetic data-generation rules (e.g., lower confidence leading to higher fallback incidence). Biological or sociological causal claims should not be extrapolated from these results to real-world populations.
