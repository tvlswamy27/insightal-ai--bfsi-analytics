/*
QUERY ID: OPS-001
BUSINESS QUESTION: How do connection statuses and hangup reasons distribute?
PURPOSE: Call operations analysis.
GRAIN: One row per connection_status and hangup_reason combination.
*/
USE insightal_analytics;

SELECT 
    connection_status,
    hangup_reason,
    COUNT(*) AS call_count,
    ROUND(COUNT(*) / SUM(COUNT(*)) OVER(), 4) AS pct_of_total,
    ROUND(AVG(call_duration_seconds), 2) AS avg_duration_seconds
FROM fact_calls
GROUP BY 
    connection_status,
    hangup_reason
ORDER BY 
    call_count DESC;

/*
QUERY ID: OPS-002
BUSINESS QUESTION: What is the distribution of outreach attempts?
PURPOSE: Attempt distribution.
GRAIN: One row per attempt_number.
*/
SELECT 
    attempt_number,
    COUNT(*) AS call_count,
    ROUND(SUM(CASE WHEN connection_status = 'Connected' THEN 1 ELSE 0 END) / COUNT(*), 4) AS connection_rate
FROM fact_calls
GROUP BY attempt_number
ORDER BY attempt_number;
