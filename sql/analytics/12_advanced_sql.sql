/*
QUERY ID: ADV-001
BUSINESS QUESTION: Which customers called multiple times and what was their escalation trajectory?
PURPOSE: Repeat interaction and sequence analysis using window functions.
GRAIN: One row per call.
*/
USE insightal_analytics;

WITH CustomerCalls AS (
    SELECT 
        customer_key,
        call_key,
        call_start_time,
        connection_status,
        escalation_flag,
        ROW_NUMBER() OVER(PARTITION BY customer_key ORDER BY call_start_time ASC) AS call_sequence,
        LEAD(escalation_flag) OVER(PARTITION BY customer_key ORDER BY call_start_time ASC) AS next_call_escalated
    FROM fact_calls
    WHERE customer_key IS NOT NULL
)
SELECT 
    customer_key,
    call_sequence,
    connection_status,
    escalation_flag,
    next_call_escalated
FROM CustomerCalls
WHERE call_sequence <= 3
LIMIT 100;
