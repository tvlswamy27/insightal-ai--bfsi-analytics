USE insightal_analytics;

DROP TABLE IF EXISTS fact_conversation;
DROP TABLE IF EXISTS fact_calls;

CREATE TABLE fact_calls (
    call_key INT UNSIGNED PRIMARY KEY,
    call_id VARCHAR(100) UNIQUE,
    customer_key INT UNSIGNED,
    campaign_key INT UNSIGNED,
    bot_key INT UNSIGNED,
    date_key INT UNSIGNED,
    intent_key INT UNSIGNED,
    call_start_time DATETIME,
    call_end_time DATETIME,
    call_duration_seconds INT,
    call_status VARCHAR(50),
    connection_status VARCHAR(50),
    hangup_reason VARCHAR(100),
    attempt_number INT UNSIGNED,
    confidence_score DECIMAL(5,4),
    outstanding_amount_at_call DECIMAL(12,2),
    days_past_due_at_call INT,
    dpd_bucket_at_call VARCHAR(50),
    risk_segment_at_call VARCHAR(50),
    identity_verified_flag TINYINT(1),
    task_started_flag TINYINT(1),
    task_completed_flag TINYINT(1),
    resolution_flag TINYINT(1),
    fallback_flag TINYINT(1),
    escalation_flag TINYINT(1),
    containment_flag TINYINT(1),
    sentiment VARCHAR(50),
    sentiment_score DECIMAL(5,4),
    ptp_flag TINYINT(1),
    ptp_amount DECIMAL(12,2),
    payment_status VARCHAR(50),
    payment_amount DECIMAL(12,2),
    
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (campaign_key) REFERENCES dim_campaign(campaign_key),
    FOREIGN KEY (bot_key) REFERENCES dim_bot(bot_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (intent_key) REFERENCES dim_intent(intent_key)
) ENGINE=InnoDB;

CREATE TABLE fact_conversation (
    turn_key BIGINT UNSIGNED PRIMARY KEY,
    turn_id VARCHAR(100) UNIQUE,
    conversation_id VARCHAR(255),
    call_key INT UNSIGNED,
    turn_number INT UNSIGNED,
    speaker VARCHAR(50),
    timestamp DATETIME,
    utterance TEXT,
    expected_intent_key INT UNSIGNED,
    detected_intent_key INT UNSIGNED,
    confidence_score DECIMAL(5,4),
    sentiment VARCHAR(50),
    sentiment_score DECIMAL(5,4),
    fallback_flag TINYINT(1),
    escalation_trigger_flag TINYINT(1),
    
    FOREIGN KEY (call_key) REFERENCES fact_calls(call_key),
    FOREIGN KEY (expected_intent_key) REFERENCES dim_intent(intent_key),
    FOREIGN KEY (detected_intent_key) REFERENCES dim_intent(intent_key)
) ENGINE=InnoDB;
