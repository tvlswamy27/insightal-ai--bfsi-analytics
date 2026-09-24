/*
QUERY ID: COL-001
BUSINESS QUESTION: How do collections campaigns perform by DPD bucket?
PURPOSE: Collections outcome analysis.
GRAIN: One row per DPD bucket.
*/
USE insightal_analytics;

SELECT 
    c.dpd_bucket_at_call,
    COUNT(*) AS connected_collections_calls,
    SUM(c.ptp_flag) AS total_ptps,
    ROUND(SUM(c.ptp_flag) / COUNT(*), 4) AS ptp_rate,
    SUM(CASE WHEN c.payment_status = 'Success' THEN 1 ELSE 0 END) AS successful_payments,
    ROUND(SUM(CASE WHEN c.payment_status = 'Success' THEN 1 ELSE 0 END) / COUNT(*), 4) AS collection_conversion_rate,
    SUM(c.outstanding_amount_at_call) AS total_outstanding,
    SUM(c.payment_amount) AS total_collected,
    ROUND(SUM(c.payment_amount) / NULLIF(SUM(c.outstanding_amount_at_call), 0), 4) AS collected_ratio
FROM fact_calls c
JOIN dim_campaign cm ON c.campaign_key = cm.campaign_key
WHERE c.connection_status = 'Connected' AND cm.campaign_type = 'Loan Collections'
GROUP BY c.dpd_bucket_at_call
ORDER BY ptp_rate DESC;
