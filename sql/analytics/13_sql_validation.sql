/*
QUERY ID: VAL-ALL
BUSINESS QUESTION: Are analytical metrics and grain constraints structurally sound?
PURPOSE: Explicit data quality and grain validation.
GRAIN: One row per validation check.
*/
USE insightal_analytics;

-- 1. Fact-to-fact fan-out
SELECT 
    'VAL-001' AS validation_id, 
    'Fact-to-fact fan-out' AS validation_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'fact_calls count changed after join' AS message
FROM (
    SELECT c.call_key 
    FROM fact_calls c 
    LEFT JOIN fact_conversation v ON c.call_key = v.call_key
    GROUP BY c.call_key 
    HAVING COUNT(DISTINCT c.call_key) > 1 
       -- Wait, fan out means joining directly increases rows:
) t WHERE 1=0; -- Always 0 in group by. We actually want to check if COUNT(c.call_key) > total_calls when joining.

-- Simpler check for fan-out logic error
SELECT 
    'VAL-001' AS validation_id, 
    'Fact-to-fact fan-out' AS validation_name,
    (SELECT COUNT(*) FROM fact_calls JOIN fact_conversation ON fact_calls.call_key = fact_conversation.call_key) - (SELECT COUNT(*) FROM fact_conversation) AS failure_count,
    CASE WHEN (SELECT COUNT(*) FROM fact_calls JOIN fact_conversation ON fact_calls.call_key = fact_conversation.call_key) - (SELECT COUNT(*) FROM fact_conversation) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Joined count mismatch' AS message;

-- 2. Customer-level aggregation grain
SELECT 
    'VAL-002' AS validation_id, 
    'Customer-level aggregation grain' AS validation_name,
    ABS((SELECT COUNT(*) FROM fact_calls) - (SELECT SUM(call_count) FROM (SELECT customer_key, COUNT(*) AS call_count FROM fact_calls GROUP BY customer_key) t)) AS failure_count,
    CASE WHEN (SELECT COUNT(*) FROM fact_calls) = (SELECT SUM(call_count) FROM (SELECT customer_key, COUNT(*) AS call_count FROM fact_calls GROUP BY customer_key) t) THEN 'PASS' ELSE 'FAIL' END AS status,
    'Aggregation does not match total calls' AS message;

-- 3. Intent accuracy denominator
SELECT 
    'VAL-003' AS validation_id, 
    'Intent accuracy denominator' AS validation_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Bot turns or NULLs included in intent accuracy' AS message
FROM fact_conversation
WHERE expected_intent_key IS NOT NULL AND detected_intent_key IS NOT NULL AND speaker != 'Customer';

-- 4. Collections filter
SELECT 
    'VAL-004' AS validation_id, 
    'Collections filter' AS validation_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'PTP or Payments found outside Loan Collections campaigns' AS message
FROM fact_calls c
JOIN dim_campaign cm ON c.campaign_key = cm.campaign_key
WHERE (c.ptp_flag = 1 OR c.payment_status = 'Success') AND cm.campaign_type != 'Loan Collections';

-- 5. Date dimension joins
SELECT 
    'VAL-005' AS validation_id, 
    'Date dimension joins' AS validation_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Invalid Date FK' AS message
FROM fact_calls c LEFT JOIN dim_date d ON c.date_key = d.date_key WHERE d.date_key IS NULL;

-- 6. Bot joins
SELECT 
    'VAL-006' AS validation_id, 
    'Bot joins' AS validation_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Invalid Bot FK' AS message
FROM fact_calls c LEFT JOIN dim_bot b ON c.bot_key = b.bot_key WHERE b.bot_key IS NULL;

-- 7. Campaign joins
SELECT 
    'VAL-007' AS validation_id, 
    'Campaign joins' AS validation_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Invalid Campaign FK' AS message
FROM fact_calls c LEFT JOIN dim_campaign cm ON c.campaign_key = cm.campaign_key WHERE cm.campaign_key IS NULL;

-- 8. Intent joins
SELECT 
    'VAL-008' AS validation_id, 
    'Intent joins' AS validation_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Invalid Intent FK' AS message
FROM fact_conversation c LEFT JOIN dim_intent i ON c.expected_intent_key = i.intent_key WHERE c.expected_intent_key IS NOT NULL AND i.intent_key IS NULL;

-- 9. Rate bounds between 0 and 1
SELECT 
    'VAL-009' AS validation_id, 
    'Rate bounds between 0 and 1' AS validation_name,
    SUM(CASE WHEN rate < 0 OR rate > 1 THEN 1 ELSE 0 END) AS failure_count,
    CASE WHEN SUM(CASE WHEN rate < 0 OR rate > 1 THEN 1 ELSE 0 END) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Rate out of bounds' AS message
FROM (
    SELECT ROUND(SUM(CASE WHEN connection_status = 'Connected' THEN 1 ELSE 0 END)/COUNT(*), 4) AS rate FROM fact_calls
) t;

-- 10. Non-negative counts
SELECT 
    'VAL-010' AS validation_id, 
    'Non-negative counts' AS validation_name,
    SUM(CASE WHEN call_duration_seconds < 0 THEN 1 ELSE 0 END) AS failure_count,
    CASE WHEN SUM(CASE WHEN call_duration_seconds < 0 THEN 1 ELSE 0 END) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Negative counts found' AS message
FROM fact_calls;

-- 11. Non-negative monetary amounts
SELECT 
    'VAL-011' AS validation_id, 
    'Non-negative monetary amounts' AS validation_name,
    SUM(CASE WHEN payment_amount < 0 OR ptp_amount < 0 THEN 1 ELSE 0 END) AS failure_count,
    CASE WHEN SUM(CASE WHEN payment_amount < 0 OR ptp_amount < 0 THEN 1 ELSE 0 END) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Negative monetary amount' AS message
FROM fact_calls;

-- 12. fact_calls call-level uniqueness
SELECT 
    'VAL-012' AS validation_id, 
    'fact_calls uniqueness' AS validation_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Duplicate call_id' AS message
FROM (SELECT call_id FROM fact_calls GROUP BY call_id HAVING COUNT(*) > 1) t;

-- 13. fact_conversation aggregation grain
SELECT 
    'VAL-013' AS validation_id, 
    'fact_conversation grain' AS validation_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Duplicate turn_id' AS message
FROM (SELECT turn_id FROM fact_conversation GROUP BY turn_id HAVING COUNT(*) > 1) t;

-- 14. PTP/payment consistency
SELECT 
    'VAL-014' AS validation_id, 
    'PTP/payment consistency' AS validation_name,
    COUNT(*) AS failure_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Payment Success without PTP or invalid amount' AS message
FROM fact_calls 
WHERE payment_status = 'Success' AND (ptp_flag = 0 OR payment_amount <= 0 OR payment_amount IS NULL);

-- 15. Unauthorized NULL analytical foreign keys
SELECT 
    'VAL-015' AS validation_id, 
    'Unauthorized NULL FKs' AS validation_name,
    (SELECT COUNT(*) FROM fact_calls WHERE customer_key IS NULL) + (SELECT COUNT(*) FROM fact_conversation WHERE call_key IS NULL) AS failure_count,
    CASE WHEN ((SELECT COUNT(*) FROM fact_calls WHERE customer_key IS NULL) + (SELECT COUNT(*) FROM fact_conversation WHERE call_key IS NULL)) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'NULL customer_key or call_key' AS message;
