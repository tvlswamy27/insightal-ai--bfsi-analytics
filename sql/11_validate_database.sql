USE insightal_analytics;

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
