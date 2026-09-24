/*
QUERY ID: INT-001
BUSINESS QUESTION: Which intents are recognized with the highest/lowest accuracy?
PURPOSE: Intent recognition confusion and accuracy.
GRAIN: One row per expected intent.
*/
USE insightal_analytics;

SELECT 
    i.intent_name AS expected_intent,
    COUNT(*) AS total_attempts,
    SUM(CASE WHEN v.expected_intent_key = v.detected_intent_key THEN 1 ELSE 0 END) AS successful_recognitions,
    ROUND(SUM(CASE WHEN v.expected_intent_key = v.detected_intent_key THEN 1 ELSE 0 END) / COUNT(*), 4) AS recognition_accuracy,
    SUM(v.fallback_flag) AS total_fallbacks,
    AVG(v.confidence_score) AS avg_confidence
FROM fact_conversation v
JOIN dim_intent i ON v.expected_intent_key = i.intent_key
WHERE v.expected_intent_key IS NOT NULL AND v.detected_intent_key IS NOT NULL AND v.speaker = 'Customer'
GROUP BY i.intent_name
ORDER BY recognition_accuracy ASC;
