import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_score,
    recall_score, f1_score, accuracy_score, brier_score_loss,
    confusion_matrix, roc_curve, precision_recall_curve
)
from sklearn.calibration import calibration_curve
import joblib

def generate_evaluation_metrics(y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    
    return {
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "pr_auc": float(average_precision_score(y_true, y_prob)),
        "brier_score": float(brier_score_loss(y_true, y_prob)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
        "positive_predictions": int(tp + fp),
        "negative_predictions": int(tn + fn),
        "actual_positives": int(tp + fn),
        "actual_negatives": int(tn + fp)
    }

def main():
    # Directories
    os.makedirs('artifacts/ml/models', exist_ok=True)
    os.makedirs('artifacts/ml/figures', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # 1. Load and Audit
    dataset_path = 'ml/data/ml_dataset_t3.csv'
    df = pd.read_csv(dataset_path)
    
    # Safety Checks
    assert len(df) == 3426, f"Expected 3426 rows, got {len(df)}"
    assert 'escalation_after_t3' in df.columns, "Target missing"
    assert set(df['escalation_after_t3'].unique()).issubset({0, 1}), "Target not 0/1"
    assert df['call_key'].is_unique, "Duplicate call_key found"
    
    prohibited = ['escalation_flag', 'escalation_trigger_flag', 'expected_intent_key', 
                  'resolution_flag', 'containment_flag', 'ptp_flag', 'payment_status', 
                  'payment_amount', 'call_status', 'hangup_reason', 'call_duration_seconds']
    for p in prohibited:
        assert p not in df.columns, f"Prohibited field {p} found!"
        
    df['prediction_timestamp'] = pd.to_datetime(df['prediction_timestamp'])
    assert df['prediction_timestamp'].is_monotonic_increasing, "Not chronologically sorted"
    assert not df['escalation_after_t3'].isnull().any(), "NaN found in target"
    assert not np.isinf(df['escalation_after_t3']).any(), "Inf found in target"
    
    # 2. Split Data (Chronological)
    train_end = pd.to_datetime('2026-05-01 08:55:09')
    val_end = pd.to_datetime('2026-05-31 17:15:00')
    
    train_df = df[df['prediction_timestamp'] <= train_end].copy()
    val_df = df[(df['prediction_timestamp'] > train_end) & (df['prediction_timestamp'] <= val_end)].copy()
    test_df = df[df['prediction_timestamp'] > val_end].copy()
    
    assert len(train_df) == 2398
    assert len(val_df) == 514
    assert len(test_df) == 514
    
    # Features Definition
    numeric_features = [
        'running_confidence_t3', 'fallback_count_t3', 'running_sentiment_score_t3',
        'call_duration_so_far_t3', 'attempt_number', 'days_past_due_at_call',
        'outstanding_amount_at_call', 'previous_call_count', 'previous_escalation_count',
        'previous_fallback_count'
    ]
    
    categorical_features = [
        'detected_intent_at_t3', 'current_sentiment_t3', 'bot_version', 'language',
        'campaign_type', 'dpd_bucket_at_call', 'risk_segment_at_call',
        'customer_segment', 'age_group', 'loan_type'
    ]
    
    for col in categorical_features:
        train_df[col] = train_df[col].astype(str)
        val_df[col] = val_df[col].astype(str)
        test_df[col] = test_df[col].astype(str)
        
    target = 'escalation_after_t3'
    identifiers = ['call_key', 'call_id', 'customer_key', 'prediction_timestamp']
    
    # 3. Preprocessing (No StandardScaler for RF)
    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median'))
    ])
    
    cat_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='Missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(transformers=[
        ('num', num_pipeline, numeric_features),
        ('cat', cat_pipeline, categorical_features)
    ])
    
    X_train = train_df[numeric_features + categorical_features]
    y_train = train_df[target]
    
    X_val = val_df[numeric_features + categorical_features]
    y_val = val_df[target]
    
    X_test = test_df[numeric_features + categorical_features]
    y_test = test_df[target]
    
    # 4. Train Random Forest
    print("Training Random Forest...")
    clf = Pipeline([
        ('preprocessor', preprocessor),
        ('model', RandomForestClassifier(
            n_estimators=500,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ])
    
    clf.fit(X_train, y_train)
    
    # 5. Evaluate
    y_train_prob = clf.predict_proba(X_train)[:, 1]
    y_val_prob = clf.predict_proba(X_val)[:, 1]
    y_test_prob = clf.predict_proba(X_test)[:, 1]
    
    train_metrics = generate_evaluation_metrics(y_train, y_train_prob)
    val_metrics = generate_evaluation_metrics(y_val, y_val_prob)
    test_metrics = generate_evaluation_metrics(y_test, y_test_prob)
    
    # 6. Threshold Analysis (Validation)
    thresholds = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]
    thresh_analysis = []
    for t in thresholds:
        m = generate_evaluation_metrics(y_val, y_val_prob, threshold=t)
        thresh_analysis.append({
            "threshold": t, "precision": m['precision'], "recall": m['recall'],
            "f1": m['f1'], "accuracy": m['accuracy'], 
            "tp": m['tp'], "fp": m['fp'], "tn": m['tn'], "fn": m['fn']
        })
        
    # 7. Feature Importance
    feature_names = numeric_features + list(clf.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(categorical_features))
    importances = clf.named_steps['model'].feature_importances_
    
    imp_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
    imp_df = imp_df.sort_values('importance', ascending=False)
    
    top_features_list = imp_df.head(20)[['feature', 'importance']].to_dict(orient='records')
    
    # 8. Visualizations
    plt.figure(figsize=(10,8))
    sns.barplot(x='importance', y='feature', data=imp_df.head(15))
    plt.title('Top 15 Random Forest Feature Importances')
    plt.tight_layout()
    plt.savefig('artifacts/ml/figures/rf_feature_importance.png')
    plt.close()
    
    # 9. Save Models
    joblib.dump(clf, 'artifacts/ml/models/random_forest_classifier.joblib')
    
    # 10. Reports
    report = {
        "dataset_version": dataset_path,
        "row_counts": {
            "total": len(df),
            "train": len(train_df),
            "val": len(val_df),
            "test": len(test_df)
        },
        "feature_count": len(numeric_features + categorical_features),
        "target_distribution": {
            "positive_rate": float(df[target].mean()),
            "total_positives": int(df[target].sum())
        },
        "preprocessing_summary": {
            "numeric_imputation": "median",
            "categorical_imputation": "Missing",
            "scaling": "None",
            "encoding": "OneHotEncoder(handle_unknown=ignore)"
        },
        "model_configuration": {
            "algorithm": "RandomForestClassifier",
            "n_estimators": 500,
            "max_depth": "None",
            "min_samples_leaf": 2,
            "class_weight": "balanced",
            "random_state": 42
        },
        "metrics": {
            "train": train_metrics,
            "validation": val_metrics,
            "test": test_metrics
        },
        "threshold_analysis_validation": thresh_analysis,
        "feature_importances": top_features_list,
        "execution_status": "SUCCESS"
    }
    
    with open('reports/ml_random_forest_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    print("Random Forest Training Complete.")

if __name__ == "__main__":
    main()
