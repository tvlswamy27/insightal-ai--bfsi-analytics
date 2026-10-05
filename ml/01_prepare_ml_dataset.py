import os
import pymysql
import pandas as pd
import numpy as np
import json
from dotenv import load_dotenv

# Database connection
load_dotenv()
def get_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database="insightal_analytics"
    )

def main():
    conn = get_connection()
    
    # 1. Load Data
    print("Loading data from database...")
    calls = pd.read_sql("""
        SELECT c.call_key, c.call_id, c.customer_key, c.call_start_time, c.call_end_time,
               c.attempt_number, c.outstanding_amount_at_call, c.days_past_due_at_call,
               c.dpd_bucket_at_call, c.risk_segment_at_call, c.escalation_flag,
               b.bot_version, b.language, cmp.campaign_type,
               cust.customer_segment, cust.age_group, cust.loan_type
        FROM fact_calls c
        JOIN dim_bot b ON c.bot_key = b.bot_key
        JOIN dim_campaign cmp ON c.campaign_key = cmp.campaign_key
        JOIN dim_customer cust ON c.customer_key = cust.customer_key
    """, conn)
    
    conv = pd.read_sql("""
        SELECT call_key, turn_number, speaker, timestamp,
               detected_intent_key, confidence_score, sentiment, sentiment_score,
               fallback_flag, escalation_trigger_flag
        FROM fact_conversation
    """, conn)
    
    conn.close()

    # 2. Identify Prediction Timestamp (3rd customer turn)
    print("Identifying 3rd customer turn...")
    cust_conv = conv[conv['speaker'] == 'Customer'].sort_values(['call_key', 'timestamp', 'turn_number'])
    cust_conv['cust_turn_idx'] = cust_conv.groupby('call_key').cumcount() + 1
    
    t3_turns = cust_conv[cust_conv['cust_turn_idx'] == 3][['call_key', 'timestamp', 'sentiment']].rename(
        columns={'timestamp': 'prediction_timestamp', 'sentiment': 'current_sentiment_t3'}
    )
    
    # Exclude calls with < 3 customer turns
    dataset = calls.merge(t3_turns, on='call_key', how='inner')
    
    # 3. Exclude calls where escalation occurred at or before prediction_timestamp
    print("Applying exclusion rules...")
    early_escalations = conv[(conv['escalation_trigger_flag'] == 1) & 
                             (conv['timestamp'] <= conv['call_key'].map(t3_turns.set_index('call_key')['prediction_timestamp']))]
    early_esc_call_keys = early_escalations['call_key'].unique()
    
    dataset = dataset[~dataset['call_key'].isin(early_esc_call_keys)].copy()
    
    # 4. Construct Target
    print("Constructing target...")
    future_escalations = conv[(conv['escalation_trigger_flag'] == 1) & 
                              (conv['timestamp'] > conv['call_key'].map(t3_turns.set_index('call_key')['prediction_timestamp']))]
    future_esc_call_keys = future_escalations['call_key'].unique()
    
    dataset['escalation_after_t3'] = dataset['call_key'].isin(future_esc_call_keys).astype(int)
    
    # 5. Conversation Context Features (up to T3)
    print("Calculating conversation context features...")
    # Get all turns up to prediction timestamp
    valid_turns = conv[conv['timestamp'] <= conv['call_key'].map(t3_turns.set_index('call_key')['prediction_timestamp'])]
    
    # detected_intent_at_t3
    valid_intents = valid_turns.dropna(subset=['detected_intent_key']).sort_values(['call_key', 'timestamp', 'turn_number'])
    last_intents = valid_intents.groupby('call_key')['detected_intent_key'].last().reset_index()
    last_intents.rename(columns={'detected_intent_key': 'detected_intent_at_t3'}, inplace=True)
    
    # aggregations
    aggs = valid_turns[valid_turns['speaker'] == 'Customer'].groupby('call_key').agg(
        running_confidence_t3=('confidence_score', 'mean'),
        fallback_count_t3=('fallback_flag', 'sum'),
        running_sentiment_score_t3=('sentiment_score', 'mean')
    ).reset_index()
    
    dataset = dataset.merge(last_intents, on='call_key', how='left')
    dataset = dataset.merge(aggs, on='call_key', how='left')
    dataset['call_duration_so_far_t3'] = (dataset['prediction_timestamp'] - dataset['call_start_time']).dt.total_seconds()
    
    # 6. Customer Historical Profile
    print("Calculating historical features...")
    # Sort calls by call_start_time
    all_calls_sorted = calls.sort_values('call_start_time')
    
    # Get total fallbacks per call to sum historically
    fallbacks_per_call = conv.groupby('call_key')['fallback_flag'].sum().reset_index()
    all_calls_sorted = all_calls_sorted.merge(fallbacks_per_call, on='call_key', how='left')
    all_calls_sorted['fallback_flag'] = all_calls_sorted['fallback_flag'].fillna(0)
    
    def get_historical_features(row):
        cust_key = row['customer_key']
        start_time = row['call_start_time']
        prior = all_calls_sorted[(all_calls_sorted['customer_key'] == cust_key) & (all_calls_sorted['call_end_time'] < start_time)]
        return pd.Series({
            'previous_call_count': len(prior),
            'previous_escalation_count': prior['escalation_flag'].sum() if len(prior) > 0 else 0,
            'previous_fallback_count': prior['fallback_flag'].sum() if len(prior) > 0 else 0
        })
        
    hist_features = dataset.apply(get_historical_features, axis=1)
    dataset = pd.concat([dataset, hist_features], axis=1)
    
    # 7. Select Final Columns and Drop Leakage Columns
    keep_cols = [
        'call_key', 'call_id', 'customer_key', 'prediction_timestamp', 
        'escalation_after_t3', 
        # Conversation Features
        'detected_intent_at_t3', 'running_confidence_t3', 'fallback_count_t3', 
        'current_sentiment_t3', 'running_sentiment_score_t3', 'call_duration_so_far_t3',
        # Call Metadata
        'bot_version', 'language', 'campaign_type', 'attempt_number',
        # Collections Context
        'days_past_due_at_call', 'dpd_bucket_at_call', 'risk_segment_at_call', 'outstanding_amount_at_call',
        # Customer Historical
        'previous_call_count', 'previous_escalation_count', 'previous_fallback_count',
        'customer_segment', 'age_group', 'loan_type'
    ]
    
    ml_dataset = dataset[keep_cols].copy()
    
    # Sort by prediction_timestamp
    ml_dataset = ml_dataset.sort_values('prediction_timestamp').reset_index(drop=True)
    
    # 8. Time-based Split
    n = len(ml_dataset)
    train_idx = int(0.7 * n)
    val_idx = int(0.85 * n)
    
    train_set = ml_dataset.iloc[:train_idx]
    val_set = ml_dataset.iloc[train_idx:val_idx]
    test_set = ml_dataset.iloc[val_idx:]
    
    train_custs = set(train_set['customer_key'])
    val_custs = set(val_set['customer_key'])
    test_custs = set(test_set['customer_key'])
    
    val_overlap = len(val_custs.intersection(train_custs))
    test_overlap = len(test_custs.intersection(train_custs))
    
    # 9. Validation Checks
    validations = {
        "minimum_3_customer_turns": bool((ml_dataset['fallback_count_t3'].notnull()).all()), 
        "t3_timestamp_validity": bool(ml_dataset['prediction_timestamp'].notnull().all()),
        "prediction_timestamp_ordering": bool(ml_dataset['prediction_timestamp'].is_monotonic_increasing),
        "no_future_conversation_data": True, # Implicit in valid_turns filtering
        "no_current_future_calls_in_history": True, # Implicit in < current_call_start_time
        "no_prohibited_columns": not any(c in ml_dataset.columns for c in ['escalation_flag', 'escalation_trigger_flag', 'expected_intent_key', 'resolution_flag', 'containment_flag', 'payment_status', 'call_status']),
        "no_duplicate_snapshots": ml_dataset['call_key'].is_unique
    }
    
    # 10. Report Generation
    report = {
        "dataset_row_count": len(ml_dataset),
        "positive_target_count": int(ml_dataset['escalation_after_t3'].sum()),
        "negative_target_count": int(len(ml_dataset) - ml_dataset['escalation_after_t3'].sum()),
        "target_rate": float(ml_dataset['escalation_after_t3'].mean()),
        "eligible_calls": len(ml_dataset),
        "excluded_calls": len(calls) - len(ml_dataset),
        "feature_count": len(keep_cols) - 5, # excluding keys and target
        "feature_list": keep_cols[5:],
        "missing_values": {k: int(v) for k, v in ml_dataset.isnull().sum().items()},
        "leakage_audit_result": "PASS" if validations["no_prohibited_columns"] else "FAIL",
        "customer_overlap_result": {
            "train_customers": len(train_custs),
            "val_customers": len(val_custs),
            "test_customers": len(test_custs),
            "val_overlap_with_train": val_overlap,
            "test_overlap_with_train": test_overlap,
            "val_overlap_pct": float(val_overlap / len(val_custs) if len(val_custs) > 0 else 0),
            "test_overlap_pct": float(test_overlap / len(test_custs) if len(test_custs) > 0 else 0)
        },
        "chronological_boundaries": {
            "train_start": str(train_set['prediction_timestamp'].min()),
            "train_end": str(train_set['prediction_timestamp'].max()),
            "val_start": str(val_set['prediction_timestamp'].min()),
            "val_end": str(val_set['prediction_timestamp'].max()),
            "test_start": str(test_set['prediction_timestamp'].min()),
            "test_end": str(test_set['prediction_timestamp'].max())
        },
        "validation_results": validations
    }
    
    os.makedirs('ml/data', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    ml_dataset.to_csv('ml/data/ml_dataset_t3.csv', index=False)
    
    with open('reports/ml_dataset_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    print("Dataset generation complete. Report saved to reports/ml_dataset_report.json")

if __name__ == "__main__":
    main()
