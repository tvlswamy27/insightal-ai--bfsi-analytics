import os

with open('sql/08_create_facts.sql', 'w') as f:
    f.write("""USE insightal_analytics;

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
""")

with open('sql/09_populate_facts.sql', 'w') as f:
    f.write("""USE insightal_staging;

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
""")

with open('sql/10_create_indexes.sql', 'w') as f:
    f.write("""USE insightal_analytics;

CREATE INDEX idx_calls_customer ON fact_calls(customer_key);
CREATE INDEX idx_calls_campaign ON fact_calls(campaign_key);
CREATE INDEX idx_calls_bot ON fact_calls(bot_key);
CREATE INDEX idx_calls_date ON fact_calls(date_key);
CREATE INDEX idx_calls_intent ON fact_calls(intent_key);
CREATE INDEX idx_calls_start ON fact_calls(call_start_time);

CREATE INDEX idx_conv_call ON fact_conversation(call_key);
CREATE INDEX idx_conv_expected ON fact_conversation(expected_intent_key);
CREATE INDEX idx_conv_detected ON fact_conversation(detected_intent_key);
CREATE INDEX idx_conv_timestamp ON fact_conversation(timestamp);
""")

with open('sql/11_validate_database.sql', 'w') as f:
    f.write("""USE insightal_analytics;

-- SECTION: A. Raw/staging/analytics row counts
SELECT 'A' as section, 'raw_customers' AS metric_name, COUNT(*) AS cnt FROM insightal_raw.raw_customers
UNION ALL SELECT 'A', 'raw_calls', COUNT(*) FROM insightal_raw.raw_calls
UNION ALL SELECT 'A', 'raw_conversations', COUNT(*) FROM insightal_raw.raw_conversations
UNION ALL SELECT 'A', 'stg_customers', COUNT(*) FROM insightal_staging.stg_customers
UNION ALL SELECT 'A', 'stg_calls', COUNT(*) FROM insightal_staging.stg_calls
UNION ALL SELECT 'A', 'stg_conversations', COUNT(*) FROM insightal_staging.stg_conversations
UNION ALL SELECT 'A', 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL SELECT 'A', 'dim_intent', COUNT(*) FROM dim_intent
UNION ALL SELECT 'A', 'dim_bot', COUNT(*) FROM dim_bot
UNION ALL SELECT 'A', 'dim_campaign', COUNT(*) FROM dim_campaign
UNION ALL SELECT 'A', 'dim_date', COUNT(*) FROM dim_date
UNION ALL SELECT 'A', 'fact_calls', COUNT(*) FROM fact_calls
UNION ALL SELECT 'A', 'fact_conversation', COUNT(*) FROM fact_conversation;

-- SECTION: B. Quarantine counts
SELECT 'B' as section, 'Quarantined stg_customers' AS metric_name, COUNT(*) AS cnt FROM insightal_staging.stg_customers WHERE error_flag = 1
UNION ALL SELECT 'B', 'Quarantined stg_calls', COUNT(*) FROM insightal_staging.stg_calls WHERE error_flag = 1
UNION ALL SELECT 'B', 'Quarantined stg_calls (Invalid Customer FK)', COUNT(*) FROM insightal_staging.stg_calls WHERE error_reason LIKE '%Invalid customer_key%'
UNION ALL SELECT 'B', 'Quarantined stg_calls (Invalid Campaign FK)', COUNT(*) FROM insightal_staging.stg_calls WHERE error_reason LIKE '%Invalid campaign_key%'
UNION ALL SELECT 'B', 'Quarantined stg_calls (Invalid Bot FK)', COUNT(*) FROM insightal_staging.stg_calls WHERE error_reason LIKE '%Invalid bot_key%'
UNION ALL SELECT 'B', 'Quarantined stg_calls (Invalid Date FK)', COUNT(*) FROM insightal_staging.stg_calls WHERE error_reason LIKE '%Invalid date_key%'
UNION ALL SELECT 'B', 'Quarantined stg_calls (Invalid Intent FK)', COUNT(*) FROM insightal_staging.stg_calls WHERE error_reason LIKE '%Invalid intent_key%'
UNION ALL SELECT 'B', 'Quarantined stg_conversations', COUNT(*) FROM insightal_staging.stg_conversations WHERE error_flag = 1
UNION ALL SELECT 'B', 'Quarantined stg_conversations (Invalid Call FK)', COUNT(*) FROM insightal_staging.stg_conversations WHERE error_reason LIKE '%Invalid call_key%'
UNION ALL SELECT 'B', 'Quarantined stg_conversations (Invalid Expected Intent FK)', COUNT(*) FROM insightal_staging.stg_conversations WHERE error_reason LIKE '%Invalid expected_intent_key%'
UNION ALL SELECT 'B', 'Quarantined stg_conversations (Invalid Detected Intent FK)', COUNT(*) FROM insightal_staging.stg_conversations WHERE error_reason LIKE '%Invalid detected_intent_key%';

-- SECTION: D. Physical FK constraints
SELECT 'D' as section, 
       CONCAT(TABLE_NAME, ' -> ', REFERENCED_TABLE_NAME) AS metric_name, 
       COUNT(*) AS cnt 
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'insightal_analytics'
  AND REFERENCED_TABLE_NAME IS NOT NULL
GROUP BY TABLE_NAME, REFERENCED_TABLE_NAME;

-- SECTION: E. Logical orphan checks
SELECT 'E' as section, 'CRITICAL: Orphan Calls vs Customer' AS metric_name, COUNT(*) AS cnt FROM fact_calls WHERE customer_key NOT IN (SELECT customer_key FROM dim_customer) OR customer_key IS NULL
UNION ALL SELECT 'E', 'CRITICAL: Orphan Calls vs Campaign', COUNT(*) FROM fact_calls WHERE campaign_key NOT IN (SELECT campaign_key FROM dim_campaign) OR campaign_key IS NULL
UNION ALL SELECT 'E', 'CRITICAL: Orphan Calls vs Bot', COUNT(*) FROM fact_calls WHERE bot_key NOT IN (SELECT bot_key FROM dim_bot) OR bot_key IS NULL
UNION ALL SELECT 'E', 'CRITICAL: Orphan Calls vs Date', COUNT(*) FROM fact_calls WHERE date_key NOT IN (SELECT date_key FROM dim_date) OR date_key IS NULL
UNION ALL SELECT 'E', 'CRITICAL: Orphan Calls vs Intent', COUNT(*) FROM fact_calls WHERE intent_key IS NOT NULL AND intent_key NOT IN (SELECT intent_key FROM dim_intent)
UNION ALL SELECT 'E', 'CRITICAL: Orphan Conversations vs Call', COUNT(*) FROM fact_conversation WHERE call_key NOT IN (SELECT call_key FROM fact_calls) OR call_key IS NULL
UNION ALL SELECT 'E', 'CRITICAL: Orphan Conversations vs Expected Intent', COUNT(*) FROM fact_conversation WHERE expected_intent_key IS NOT NULL AND expected_intent_key NOT IN (SELECT intent_key FROM dim_intent)
UNION ALL SELECT 'E', 'CRITICAL: Orphan Conversations vs Detected Intent', COUNT(*) FROM fact_conversation WHERE detected_intent_key IS NOT NULL AND detected_intent_key NOT IN (SELECT intent_key FROM dim_intent);


-- SECTION: F. Timestamp validation
SELECT 'F' as section, 'CRITICAL: Invalid Duration / End Time' AS metric_name, COUNT(*) AS cnt 
FROM fact_calls 
WHERE call_end_time < call_start_time 
   OR (TIMESTAMPDIFF(SECOND, call_start_time, call_end_time) != call_duration_seconds AND connection_status != 'Voicemail');

-- SECTION: G. Payment validation
SELECT 'G' as section, 'CRITICAL: Payment Success Rule Violations' AS metric_name, COUNT(*) AS cnt 
FROM fact_calls 
WHERE payment_status = 'Success' AND (payment_amount IS NULL OR payment_amount <= 0 OR ptp_flag = 0)
UNION ALL
SELECT 'G', 'CRITICAL: Payment Non-Success Violations', COUNT(*) 
FROM fact_calls 
WHERE (payment_status IS NULL OR payment_status != 'Success') AND (payment_amount > 0);

-- SECTION: H. PTP validation
SELECT 'H' as section, 'CRITICAL: Invalid PTP Amount' AS metric_name, COUNT(*) AS cnt
FROM fact_calls
WHERE ptp_flag = 0 AND ptp_amount > 0
UNION ALL
SELECT 'H', 'CRITICAL: PTP Amount Missing', COUNT(*)
FROM fact_calls
WHERE ptp_flag = 1 AND (ptp_amount IS NULL OR ptp_amount <= 0)
UNION ALL
SELECT 'H', 'CRITICAL: Payment exceeds PTP', COUNT(*)
FROM fact_calls
WHERE ptp_amount IS NOT NULL AND payment_amount IS NOT NULL AND payment_amount > ptp_amount;

-- SECTION: I. Intent/fallback validation
SELECT 'I' as section, 'CRITICAL: Intent Fallback Violations' AS metric_name, COUNT(*) AS cnt 
FROM fact_conversation 
WHERE fallback_flag = 1 AND detected_intent_key IS NOT NULL;

-- SECTION: J. Database engine validation
SELECT 'J' as section, TABLE_NAME AS metric_name, COUNT(*) AS cnt
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'insightal_analytics' AND ENGINE != 'InnoDB'
GROUP BY TABLE_NAME;
""")
