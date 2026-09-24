USE insightal_staging;

-- Quarantine staging calls with invalid FKs
UPDATE stg_calls SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'NULL_CUSTOMER_KEY') WHERE customer_key IS NULL;
UPDATE stg_calls SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'INVALID_CUSTOMER_REFERENCE') WHERE customer_key IS NOT NULL AND NOT EXISTS (SELECT 1 FROM insightal_analytics.dim_customer d WHERE d.customer_key = stg_calls.customer_key);

UPDATE stg_calls SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'NULL_CAMPAIGN_KEY') WHERE campaign_key IS NULL;
UPDATE stg_calls SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'INVALID_CAMPAIGN_REFERENCE') WHERE campaign_key IS NOT NULL AND NOT EXISTS (SELECT 1 FROM insightal_analytics.dim_campaign d WHERE d.campaign_key = stg_calls.campaign_key);

UPDATE stg_calls SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'NULL_BOT_KEY') WHERE bot_key IS NULL;
UPDATE stg_calls SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'INVALID_BOT_REFERENCE') WHERE bot_key IS NOT NULL AND NOT EXISTS (SELECT 1 FROM insightal_analytics.dim_bot d WHERE d.bot_key = stg_calls.bot_key);

UPDATE stg_calls SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'NULL_DATE_KEY') WHERE date_key IS NULL;
UPDATE stg_calls SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'INVALID_DATE_REFERENCE') WHERE date_key IS NOT NULL AND NOT EXISTS (SELECT 1 FROM insightal_analytics.dim_date d WHERE d.date_key = stg_calls.date_key);

UPDATE stg_calls SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'INVALID_INTENT_REFERENCE') WHERE intent_key IS NOT NULL AND NOT EXISTS (SELECT 1 FROM insightal_analytics.dim_intent d WHERE d.intent_key = stg_calls.intent_key);

-- Quarantine staging calls with missing required temporal fields
UPDATE stg_calls SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'NULL_CALL_START_TIME') WHERE call_start_time IS NULL;
UPDATE stg_calls SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'NULL_CALL_DURATION') WHERE call_duration_seconds IS NULL;


USE insightal_analytics;

INSERT INTO fact_calls (
    call_key, call_id, customer_key, campaign_key, bot_key, date_key, intent_key,
    call_start_time, call_end_time, call_duration_seconds, call_status, connection_status,
    hangup_reason, attempt_number, confidence_score, outstanding_amount_at_call,
    days_past_due_at_call, dpd_bucket_at_call, risk_segment_at_call, identity_verified_flag,
    task_started_flag, task_completed_flag, resolution_flag, fallback_flag, escalation_flag,
    containment_flag, sentiment, sentiment_score, ptp_flag, ptp_amount, payment_status, payment_amount
)
SELECT 
    call_key, call_id, customer_key, campaign_key, bot_key, date_key, intent_key,
    call_start_time, call_end_time, call_duration_seconds, call_status, connection_status,
    hangup_reason, attempt_number, confidence_score, outstanding_amount_at_call,
    days_past_due_at_call, dpd_bucket_at_call, risk_segment_at_call, identity_verified_flag,
    task_started_flag, task_completed_flag, resolution_flag, fallback_flag, escalation_flag,
    containment_flag, sentiment, sentiment_score, ptp_flag, ptp_amount, payment_status, payment_amount
FROM insightal_staging.stg_calls
WHERE error_flag = 0;

USE insightal_staging;

-- Quarantine staging conversations with invalid FKs
UPDATE stg_conversations SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'NULL_CALL_KEY') WHERE call_key IS NULL;
UPDATE stg_conversations SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'INVALID_CALL_REFERENCE') WHERE call_key IS NOT NULL AND NOT EXISTS (SELECT 1 FROM insightal_analytics.fact_calls f WHERE f.call_key = stg_conversations.call_key);

UPDATE stg_conversations SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'INVALID_EXPECTED_INTENT_REFERENCE') WHERE expected_intent_key IS NOT NULL AND NOT EXISTS (SELECT 1 FROM insightal_analytics.dim_intent d WHERE d.intent_key = stg_conversations.expected_intent_key);
UPDATE stg_conversations SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'INVALID_DETECTED_INTENT_REFERENCE') WHERE detected_intent_key IS NOT NULL AND NOT EXISTS (SELECT 1 FROM insightal_analytics.dim_intent d WHERE d.intent_key = stg_conversations.detected_intent_key);

-- Quarantine staging conversations with missing required temporal fields
UPDATE stg_conversations SET error_flag = 1, error_reason = CONCAT_WS(', ', error_reason, 'NULL_CONVERSATION_TIMESTAMP') WHERE timestamp IS NULL;


USE insightal_analytics;

INSERT INTO fact_conversation (
    turn_key, turn_id, conversation_id, call_key, turn_number, speaker, timestamp,
    utterance, expected_intent_key, detected_intent_key, confidence_score, sentiment,
    sentiment_score, fallback_flag, escalation_trigger_flag
)
SELECT 
    turn_key, turn_id, conversation_id, call_key, turn_number, speaker, timestamp,
    utterance, expected_intent_key, detected_intent_key, confidence_score, sentiment,
    sentiment_score, fallback_flag, escalation_trigger_flag
FROM insightal_staging.stg_conversations
WHERE error_flag = 0;
