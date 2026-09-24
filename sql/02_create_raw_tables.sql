USE insightal_raw;

DROP TABLE IF EXISTS raw_customers;
CREATE TABLE raw_customers (
    customer_key TEXT, customer_id TEXT, age TEXT, gender TEXT, state TEXT, city TEXT,
    customer_type TEXT, customer_segment TEXT, loan_type TEXT, customer_since_date TEXT,
    age_group TEXT, region TEXT
);

DROP TABLE IF EXISTS raw_calls;
CREATE TABLE raw_calls (
    call_key TEXT, call_id TEXT, customer_key TEXT, campaign_key TEXT, bot_key TEXT,
    call_start_time TEXT, date_key TEXT, attempt_number TEXT, connection_status TEXT,
    days_past_due_at_call TEXT, dpd_bucket_at_call TEXT, outstanding_amount_at_call TEXT,
    risk_segment_at_call TEXT, fallback_flag TEXT, confidence_score TEXT, sentiment TEXT,
    sentiment_score TEXT, escalation_flag TEXT, call_duration_seconds TEXT, call_end_time TEXT,
    task_started_flag TEXT, task_completed_flag TEXT, resolution_flag TEXT, containment_flag TEXT,
    ptp_flag TEXT, ptp_amount TEXT, payment_status TEXT, payment_amount TEXT, hangup_reason TEXT,
    call_status TEXT, intent_key TEXT, identity_verified_flag TEXT
);

DROP TABLE IF EXISTS raw_conversations;
CREATE TABLE raw_conversations (
    turn_key TEXT, turn_id TEXT, conversation_id TEXT, call_key TEXT, turn_number TEXT,
    speaker TEXT, timestamp TEXT, utterance TEXT, expected_intent_key TEXT, detected_intent_key TEXT,
    confidence_score TEXT, sentiment TEXT, sentiment_score TEXT, fallback_flag TEXT, escalation_trigger_flag TEXT
);
