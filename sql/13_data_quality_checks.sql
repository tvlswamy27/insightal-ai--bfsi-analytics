USE insightal_analytics;

-- COMPLETENESS CHECKS
-- Will return table_name, column_name, total_rows, null_rows
SELECT 'dim_customer' as table_name, 'customer_id' as column_name, COUNT(*) as total_rows, SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_rows FROM dim_customer
UNION ALL SELECT 'dim_customer', 'age', COUNT(*), SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) FROM dim_customer
UNION ALL SELECT 'dim_customer', 'age_group', COUNT(*), SUM(CASE WHEN age_group IS NULL THEN 1 ELSE 0 END) FROM dim_customer
UNION ALL SELECT 'dim_customer', 'gender', COUNT(*), SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) FROM dim_customer
UNION ALL SELECT 'dim_customer', 'city', COUNT(*), SUM(CASE WHEN city IS NULL THEN 1 ELSE 0 END) FROM dim_customer
UNION ALL SELECT 'dim_customer', 'state', COUNT(*), SUM(CASE WHEN state IS NULL THEN 1 ELSE 0 END) FROM dim_customer
UNION ALL SELECT 'dim_customer', 'region', COUNT(*), SUM(CASE WHEN region IS NULL THEN 1 ELSE 0 END) FROM dim_customer
UNION ALL SELECT 'dim_customer', 'customer_type', COUNT(*), SUM(CASE WHEN customer_type IS NULL THEN 1 ELSE 0 END) FROM dim_customer
UNION ALL SELECT 'dim_customer', 'customer_segment', COUNT(*), SUM(CASE WHEN customer_segment IS NULL THEN 1 ELSE 0 END) FROM dim_customer
UNION ALL SELECT 'dim_customer', 'loan_type', COUNT(*), SUM(CASE WHEN loan_type IS NULL THEN 1 ELSE 0 END) FROM dim_customer
UNION ALL SELECT 'dim_customer', 'customer_since_date', COUNT(*), SUM(CASE WHEN customer_since_date IS NULL THEN 1 ELSE 0 END) FROM dim_customer
UNION ALL SELECT 'fact_calls', 'call_id', COUNT(*), SUM(CASE WHEN call_id IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'customer_key', COUNT(*), SUM(CASE WHEN customer_key IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'campaign_key', COUNT(*), SUM(CASE WHEN campaign_key IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'bot_key', COUNT(*), SUM(CASE WHEN bot_key IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'date_key', COUNT(*), SUM(CASE WHEN date_key IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'call_start_time', COUNT(*), SUM(CASE WHEN call_start_time IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'call_end_time', COUNT(*), SUM(CASE WHEN call_end_time IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'call_duration_seconds', COUNT(*), SUM(CASE WHEN call_duration_seconds IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'call_status', COUNT(*), SUM(CASE WHEN call_status IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'connection_status', COUNT(*), SUM(CASE WHEN connection_status IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'intent_key', COUNT(*), SUM(CASE WHEN intent_key IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'confidence_score', COUNT(*), SUM(CASE WHEN confidence_score IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'escalation_flag', COUNT(*), SUM(CASE WHEN escalation_flag IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'containment_flag', COUNT(*), SUM(CASE WHEN containment_flag IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_calls', 'resolution_flag', COUNT(*), SUM(CASE WHEN resolution_flag IS NULL THEN 1 ELSE 0 END) FROM fact_calls
UNION ALL SELECT 'fact_conversation', 'turn_id', COUNT(*), SUM(CASE WHEN turn_id IS NULL THEN 1 ELSE 0 END) FROM fact_conversation
UNION ALL SELECT 'fact_conversation', 'conversation_id', COUNT(*), SUM(CASE WHEN conversation_id IS NULL THEN 1 ELSE 0 END) FROM fact_conversation
UNION ALL SELECT 'fact_conversation', 'call_key', COUNT(*), SUM(CASE WHEN call_key IS NULL THEN 1 ELSE 0 END) FROM fact_conversation
UNION ALL SELECT 'fact_conversation', 'turn_number', COUNT(*), SUM(CASE WHEN turn_number IS NULL THEN 1 ELSE 0 END) FROM fact_conversation
UNION ALL SELECT 'fact_conversation', 'speaker', COUNT(*), SUM(CASE WHEN speaker IS NULL THEN 1 ELSE 0 END) FROM fact_conversation
UNION ALL SELECT 'fact_conversation', 'timestamp', COUNT(*), SUM(CASE WHEN timestamp IS NULL THEN 1 ELSE 0 END) FROM fact_conversation
UNION ALL SELECT 'fact_conversation', 'utterance', COUNT(*), SUM(CASE WHEN utterance IS NULL THEN 1 ELSE 0 END) FROM fact_conversation;
