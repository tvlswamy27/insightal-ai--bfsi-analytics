def run_ml_readiness():
    allowed = [
        {"feature_name": "detected_intent_key", "source_table": "fact_conversation", "data_type": "int", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": 20, "ml_allowed": True, "leakage_risk": False, "reason": "Available during call"},
        {"feature_name": "confidence_score", "source_table": "fact_conversation", "data_type": "float", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Available during inference"},
        {"feature_name": "sentiment", "source_table": "fact_conversation", "data_type": "str", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": 3, "ml_allowed": True, "leakage_risk": False, "reason": "Sequential calculation"},
        {"feature_name": "sentiment_score", "source_table": "fact_conversation", "data_type": "float", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Sequential calculation"},
        {"feature_name": "fallback_count_so_far", "source_table": "derived", "data_type": "int", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Accumulates incrementally"},
        {"feature_name": "turn_count_so_far", "source_table": "derived", "data_type": "int", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Accumulates incrementally"},
        {"feature_name": "call_duration_so_far", "source_table": "derived", "data_type": "int", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Accumulates incrementally"},
        {"feature_name": "bot_version", "source_table": "dim_bot", "data_type": "str", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": 5, "ml_allowed": True, "leakage_risk": False, "reason": "Pre-call config"},
        {"feature_name": "campaign_key", "source_table": "fact_calls", "data_type": "int", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": 10, "ml_allowed": True, "leakage_risk": False, "reason": "Pre-call config"},
        {"feature_name": "campaign_type", "source_table": "dim_campaign", "data_type": "str", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": 5, "ml_allowed": True, "leakage_risk": False, "reason": "Pre-call config"},
        {"feature_name": "language", "source_table": "dim_bot", "data_type": "str", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": 3, "ml_allowed": True, "leakage_risk": False, "reason": "Pre-call config"},
        {"feature_name": "dpd_bucket_at_call", "source_table": "fact_calls", "data_type": "str", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": 5, "ml_allowed": True, "leakage_risk": False, "reason": "Snapshot before call"},
        {"feature_name": "days_past_due_at_call", "source_table": "fact_calls", "data_type": "int", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Snapshot before call"},
        {"feature_name": "risk_segment_at_call", "source_table": "fact_calls", "data_type": "str", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": 3, "ml_allowed": True, "leakage_risk": False, "reason": "Snapshot before call"},
        {"feature_name": "outstanding_amount_at_call", "source_table": "fact_calls", "data_type": "float", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Snapshot before call"},
        {"feature_name": "previous_call_count", "source_table": "derived", "data_type": "int", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "History"},
        {"feature_name": "previous_escalation_count", "source_table": "derived", "data_type": "int", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "History"},
        {"feature_name": "previous_fallback_count", "source_table": "derived", "data_type": "int", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "History"}
    ]
    prohibited = [
        {"feature_name": "expected_intent_key", "source_table": "fact_conversation", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "escalation_trigger_flag", "source_table": "fact_conversation", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "escalation_flag", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "escalation_target", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "resolution_flag", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "task_completed_flag", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "containment_flag", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "ptp_flag", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "payment_status", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "payment_amount", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "hangup_reason", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"}
    ]
    return {"allowed": allowed, "prohibited": prohibited}
