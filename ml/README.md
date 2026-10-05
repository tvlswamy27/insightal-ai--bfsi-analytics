# ML Pipeline Scripts

This directory contains the reproducible machine learning pipeline for the Insightal AI Escalation Prediction model.

## Scripts Overview

1. `01_prepare_ml_dataset.py`: Extracts data from the `insightal_analytics` database, strictly enforces the Turn-3 prediction point, generates point-in-time features, audits for target leakage, and generates `ml/data/ml_dataset_t3.csv`.
2. `04_train_baseline.py`: Loads the frozen dataset, builds a preprocessing pipeline (imputation + scaling + encoding), and trains a transparent Logistic Regression baseline model using a strict chronological train/validation/test split.
3. `05_train_random_forest.py`: Trains a Random Forest candidate model using the exact same chronological split. XGBoost was skipped because it is not available in the current environment. (Phase 11)
4. `07_compare_models.py`: Compares the candidate models against the Logistic Regression baseline benchmark, applying chronological validation and strictly untouched test-set protection. (Phase 11)
5. `08_final_validation.py`: Performs final explainability, robustness, error analysis, and calibration checks on the champion model. Generates the final model card and validation reports. (Phase 12)

## Execution

To reproduce the baseline model:
```bash
python ml/04_train_baseline.py
```
To reproduce the candidate models and evaluation:
```bash
python ml/05_train_random_forest.py
python ml/07_compare_models.py
```
To reproduce the final validation of the champion model:
```bash
python ml/08_final_validation.py
```

## Methodology

### Chronological Validation & Test-Set Protection
The evaluation framework uses strict temporal boundaries to prevent future information leakage:
- **Train:** Jan 1 - May 1
- **Validation:** May 1 - May 31
- **Test:** May 31 - Jun 30

Models are tuned and compared on the **Validation Set**. The **Test Set** remains completely untouched during model selection.

### Model Comparison
Candidate models are evaluated based on their ability to meaningfully beat the Logistic Regression baseline benchmark across ranking (ROC-AUC, PR-AUC), threshold metrics (F1, Precision, Recall), calibration (Brier Score), and interpretability.

## Candidate Results

The Logistic Regression baseline **outperformed** Random Forest on both the Validation and Test sets across all major metrics:
- **LR Val ROC-AUC:** 0.949 | **RF Val ROC-AUC:** 0.944
- **LR Test ROC-AUC:** 0.959 | **RF Test ROC-AUC:** 0.952
- **LR Test Brier Score:** 0.074 | **RF Test Brier Score:** 0.083

The Random Forest model exhibited typical tree-based overfitting on the training set without translating to better generalization. **Logistic Regression remains the overall champion.**

### Final Validation & Robustness (Phase 12)
The Logistic Regression champion underwent a complete validation suite:
- **Explainability:** Global coefficients and Permutation Importance successfully extracted. (SHAP was skipped as it is not available).
- **Error Analysis:** Demonstrated that false negatives generally lacked the high fallback signals present in true positives.
- **Calibration:** Excellent probability calibration (Test Brier Score: 0.074).
- **Robustness:** A secondary Customer-Disjoint cross-validation achieved a 0.956 ROC-AUC, confirming the temporal holdout score (0.959 ROC-AUC) is highly robust and not dependent on customer memorization.

Detailed findings are documented in the [Final Validation Report](../reports/ml_final_validation.md) and the formal [Model Card](../docs/ml_model_card.md).

## Outputs
- **Models:** `artifacts/ml/models/*.joblib`
- **Figures:** `artifacts/ml/figures/*.png` (ROC curve, PR curve, Calibration, Coefficients, etc.)
- **Reports:** `reports/ml_baseline_report.json`, `reports/ml_baseline_report.md`, `reports/ml_baseline_validation.json`, `reports/ml_final_validation.md`, `reports/ml_model_comparison.md`

## Final ML Status

Champion:
Logistic Regression

Test ROC-AUC:
0.959

Test PR-AUC:
0.954

Test F1:
0.875

Test Brier:
0.074

Random Forest did not meaningfully outperform Logistic Regression.

XGBoost was not evaluated because it was unavailable in the controlled environment.

Primary evaluation:
Chronological train/validation/test split.

Secondary robustness:
Customer-disjoint GroupKFold.

The model is intended as a synthetic portfolio demonstration and requires real-world validation before production deployment.
