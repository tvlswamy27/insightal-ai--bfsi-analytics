USE insightal_staging;

DROP TABLE IF EXISTS stg_customers;
CREATE TABLE stg_customers (
    customer_key INT UNSIGNED, customer_id VARCHAR(255), age INT, gender VARCHAR(50),
    state VARCHAR(100), city VARCHAR(100), customer_type VARCHAR(100), customer_segment VARCHAR(100),
    loan_type VARCHAR(100), customer_since_date DATE, age_group VARCHAR(50), region VARCHAR(100),
    error_flag TINYINT(1) DEFAULT 0, error_reason TEXT
);

DROP TABLE IF EXISTS stg_calls;
CREATE TABLE stg_calls (
    call_key INT UNSIGNED, call_id VARCHAR(255), customer_key INT UNSIGNED, campaign_key INT UNSIGNED,
    bot_key INT UNSIGNED, call_start_time DATETIME, date_key INT UNSIGNED, attempt_number INT UNSIGNED,
    connection_status VARCHAR(50), days_past_due_at_call INT, dpd_bucket_at_call VARCHAR(50),
    outstanding_amount_at_call DECIMAL(12,2), risk_segment_at_call VARCHAR(50), fallback_flag TINYINT(1),
    confidence_score DECIMAL(5,4), sentiment VARCHAR(50), sentiment_score DECIMAL(5,4),
    escalation_flag TINYINT(1), call_duration_seconds INT, call_end_time DATETIME,
    task_started_flag TINYINT(1), task_completed_flag TINYINT(1), resolution_flag TINYINT(1),
    containment_flag TINYINT(1), ptp_flag TINYINT(1), ptp_amount DECIMAL(12,2), payment_status VARCHAR(50),
    payment_amount DECIMAL(12,2), hangup_reason VARCHAR(100), call_status VARCHAR(50),
    intent_key INT UNSIGNED, identity_verified_flag TINYINT(1), error_flag TINYINT(1) DEFAULT 0, error_reason TEXT
);

DROP TABLE IF EXISTS stg_conversations;
CREATE TABLE stg_conversations (
    turn_key BIGINT UNSIGNED, turn_id VARCHAR(255), conversation_id VARCHAR(255), call_key INT UNSIGNED,
    turn_number INT UNSIGNED, speaker VARCHAR(50), timestamp DATETIME, utterance TEXT,
    expected_intent_key INT UNSIGNED, detected_intent_key INT UNSIGNED, confidence_score DECIMAL(5,4),
    sentiment VARCHAR(50), sentiment_score DECIMAL(5,4), fallback_flag TINYINT(1),
    escalation_trigger_flag TINYINT(1), error_flag TINYINT(1) DEFAULT 0, error_reason TEXT
);
