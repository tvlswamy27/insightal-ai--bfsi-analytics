USE insightal_staging;

TRUNCATE TABLE stg_customers;
TRUNCATE TABLE stg_calls;
TRUNCATE TABLE stg_conversations;

INSERT INTO stg_customers (
    customer_key, customer_id, age, gender, state, city, customer_type, 
    customer_segment, loan_type, customer_since_date, age_group, region, error_flag, error_reason
)
SELECT DISTINCT
    CAST(customer_key AS UNSIGNED), customer_id, 
    CAST(age AS DECIMAL), 
    gender, state, city, customer_type, customer_segment, loan_type, 
    STR_TO_DATE(NULLIF(customer_since_date, 'NaT'), '%Y-%m-%d'),
    age_group, region,
    CASE WHEN age IS NULL OR age = 'nan' THEN 1 ELSE 0 END,
    CASE WHEN age IS NULL OR age = 'nan' THEN 'Invalid Age' ELSE NULL END
FROM insightal_raw.raw_customers;

INSERT INTO stg_calls (
    call_key, call_id, customer_key, campaign_key, bot_key, call_start_time, date_key, 
    attempt_number, connection_status, days_past_due_at_call, dpd_bucket_at_call, 
    outstanding_amount_at_call, risk_segment_at_call, fallback_flag, confidence_score, 
    sentiment, sentiment_score, escalation_flag, call_duration_seconds, call_end_time, 
    task_started_flag, task_completed_flag, resolution_flag, containment_flag, ptp_flag, 
    ptp_amount, payment_status, payment_amount, hangup_reason, call_status, intent_key, 
    identity_verified_flag, error_flag, error_reason
)
SELECT DISTINCT
    CAST(call_key AS UNSIGNED), call_id, CAST(customer_key AS UNSIGNED), 
    CAST(campaign_key AS UNSIGNED), CAST(bot_key AS UNSIGNED), 
    STR_TO_DATE(NULLIF(call_start_time, 'NaT'), '%Y-%m-%d %H:%i:%s'), 
    CAST(date_key AS UNSIGNED), CAST(attempt_number AS UNSIGNED), connection_status, 
    CAST(days_past_due_at_call AS SIGNED), dpd_bucket_at_call, 
    CAST(outstanding_amount_at_call AS DECIMAL(12,2)), risk_segment_at_call, 
    CAST(fallback_flag AS UNSIGNED), CAST(NULLIF(confidence_score, 'nan') AS DECIMAL(5,4)), sentiment, 
    CAST(NULLIF(sentiment_score, 'nan') AS DECIMAL(5,4)), CAST(escalation_flag AS UNSIGNED), 
    CAST(call_duration_seconds AS SIGNED), 
    STR_TO_DATE(NULLIF(call_end_time, 'NaT'), '%Y-%m-%d %H:%i:%s'), 
    CAST(task_started_flag AS UNSIGNED), CAST(task_completed_flag AS UNSIGNED), 
    CAST(resolution_flag AS UNSIGNED), CAST(containment_flag AS UNSIGNED), 
    CAST(ptp_flag AS UNSIGNED), CAST(NULLIF(ptp_amount, 'nan') AS DECIMAL(12,2)), payment_status, 
    CAST(NULLIF(payment_amount, 'nan') AS DECIMAL(12,2)), hangup_reason, call_status, 
    CAST(NULLIF(NULLIF(intent_key, 'nan'), '') AS UNSIGNED), CAST(identity_verified_flag AS UNSIGNED),
    CASE WHEN CAST(call_duration_seconds AS SIGNED) < 0 OR call_start_time = 'NaT' THEN 1 ELSE 0 END,
    CASE WHEN CAST(call_duration_seconds AS SIGNED) < 0 THEN 'Negative Duration' 
         WHEN call_start_time = 'NaT' THEN 'Invalid Date' ELSE NULL END
FROM insightal_raw.raw_calls;

INSERT INTO stg_conversations (
    turn_key, turn_id, conversation_id, call_key, turn_number, speaker, timestamp, 
    utterance, expected_intent_key, detected_intent_key, confidence_score, sentiment, 
    sentiment_score, fallback_flag, escalation_trigger_flag, error_flag, error_reason
)
SELECT DISTINCT
    CAST(turn_key AS UNSIGNED), turn_id, conversation_id, CAST(call_key AS UNSIGNED), 
    CAST(turn_number AS UNSIGNED), speaker, 
    STR_TO_DATE(NULLIF(timestamp, 'NaT'), '%Y-%m-%d %H:%i:%s'), 
    utterance, 
    CAST(NULLIF(NULLIF(expected_intent_key, 'nan'), '') AS UNSIGNED), 
    CAST(NULLIF(NULLIF(detected_intent_key, 'nan'), '') AS UNSIGNED), 
    CAST(NULLIF(confidence_score, 'nan') AS DECIMAL(5,4)), sentiment, 
    CAST(NULLIF(sentiment_score, 'nan') AS DECIMAL(5,4)), CAST(fallback_flag AS UNSIGNED), 
    CAST(escalation_trigger_flag AS UNSIGNED),
    CASE WHEN timestamp = 'NaT' THEN 1 ELSE 0 END,
    CASE WHEN timestamp = 'NaT' THEN 'Invalid Timestamp' ELSE NULL END
FROM insightal_raw.raw_conversations;
