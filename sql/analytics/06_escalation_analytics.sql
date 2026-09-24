/*
QUERY ID: ESC-001
BUSINESS QUESTION: What factors are associated with escalation?
PURPOSE: Escalation profiling.
GRAIN: One row per customer segment.
*/
USE insightal_analytics;

SELECT 
    cu.customer_segment,
    COUNT(*) AS total_connected_calls,
    SUM(c.escalation_flag) AS total_escalations,
    ROUND(SUM(c.escalation_flag) / COUNT(*), 4) AS escalation_rate,
    ROUND(AVG(c.sentiment_score), 4) AS avg_sentiment_score
FROM fact_calls c
JOIN dim_customer cu ON c.customer_key = cu.customer_key
WHERE c.connection_status = 'Connected'
GROUP BY cu.customer_segment
ORDER BY escalation_rate DESC;
