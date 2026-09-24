/*
QUERY ID: TME-001
BUSINESS QUESTION: What is the trend of call volume and containment over time?
PURPOSE: Time-series trend analysis.
GRAIN: One row per day.
*/
USE insightal_analytics;

SELECT 
    d.date,
    COUNT(*) AS total_calls,
    SUM(CASE WHEN c.connection_status = 'Connected' THEN 1 ELSE 0 END) AS connected_calls,
    ROUND(SUM(c.containment_flag) / NULLIF(SUM(CASE WHEN c.connection_status = 'Connected' THEN 1 ELSE 0 END), 0), 4) AS daily_containment_rate,
    AVG(COUNT(*)) OVER (ORDER BY d.date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7d_avg_calls
FROM fact_calls c
JOIN dim_date d ON c.date_key = d.date_key
GROUP BY d.date
ORDER BY d.date;
