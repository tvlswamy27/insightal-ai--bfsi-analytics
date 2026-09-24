/*
QUERY ID: SEG-001
BUSINESS QUESTION: Which age groups engage the most with the AI?
PURPOSE: Demographic behavior analysis.
GRAIN: One row per age group.
*/
USE insightal_analytics;

SELECT 
    cu.age_group,
    COUNT(*) AS total_calls,
    ROUND(SUM(CASE WHEN c.connection_status = 'Connected' THEN 1 ELSE 0 END) / COUNT(*), 4) AS connection_rate,
    ROUND(SUM(c.resolution_flag) / NULLIF(SUM(CASE WHEN c.connection_status = 'Connected' THEN 1 ELSE 0 END), 0), 4) AS resolution_rate
FROM fact_calls c
JOIN dim_customer cu ON c.customer_key = cu.customer_key
GROUP BY cu.age_group
ORDER BY total_calls DESC;
