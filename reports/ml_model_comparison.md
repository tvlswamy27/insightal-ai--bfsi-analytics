# ML Model Comparison Report

## 1. Overview
Evaluated candidate models (Random Forest) against the Baseline Logistic Regression.
XGBoost was skipped as it is not available in the current environment.

## 2. Validation Set Comparison

| Model | ROC-AUC | PR-AUC | Precision | Recall | F1 | Accuracy | Brier Score |
|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.9493 | 0.9411 | 0.8871 | 0.8128 | 0.8483 | 0.8852 | 0.0829 |
| Random Forest | 0.9441 | 0.9360 | 0.8743 | 0.8227 | 0.8477 | 0.8833 | 0.0894 |

## 3. Test Set Comparison

| Model | ROC-AUC | PR-AUC | Precision | Recall | F1 | Accuracy | Brier Score |
|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.9591 | 0.9545 | 0.8835 | 0.8667 | 0.8750 | 0.8988 | 0.0741 |
| Random Forest | 0.9520 | 0.9503 | 0.8738 | 0.8571 | 0.8654 | 0.8911 | 0.0837 |

## 4. Overfitting Analysis (Random Forest)
- **Train ROC-AUC:** 0.9979
- **Validation ROC-AUC:** 0.9441 (Gap: 0.0537)
- **Train PR-AUC:** 0.9968
- **Validation PR-AUC:** 0.9360 (Gap: 0.0608)

*Note: High train metrics indicate tree models natively overfit training data compared to linear models, but the validation metrics hold stable indicating good generalization.*

## 5. Candidate Selection
- **Best Validation ROC-AUC:** Logistic Regression
- **Best Validation PR-AUC:** Logistic Regression
- **Best Validation F1:** Logistic Regression
- **Best Validation Brier:** Logistic Regression

**Overall Candidate Model:** Logistic Regression
**Meaningful Improvement:** False

**Reasoning:**
RF ROC difference is -0.0052. Simpler model preferred unless improvement is substantial.
