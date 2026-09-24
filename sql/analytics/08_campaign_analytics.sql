/*
QUERY ID: CMP-001
BUSINESS QUESTION: How do campaigns compare across volume and outcome metrics?
PURPOSE: Campaign effectiveness.
GRAIN: One row per campaign.
*/
USE insightal_analytics;

SELECT 
    cm.campaign_name,
    cm.campaign_type,
    COUNT(*) AS total_calls,
    SUM(CASE WHEN c.connection_status = 'Connected' THEN 1 ELSE 0 END) AS connected_calls,
    ROUND(SUM(CASE WHEN c.connection_status = 'Connected' THEN 1 ELSE 0 END) / COUNT(*), 4) AS connection_rate,
    ROUND(SUM(c.containment_flag) / NULLIF(SUM(CASE WHEN c.connection_status = 'Connected' THEN 1 ELSE 0 END), 0), 4) AS containment_rate,
    SUM(c.ptp_flag) AS total_ptps,
    SUM(c.payment_amount) AS total_collected
FROM fact_calls c
JOIN dim_campaign cm ON c.campaign_key = cm.campaign_key
GROUP BY cm.campaign_name, cm.campaign_type
ORDER BY total_calls DESC;
