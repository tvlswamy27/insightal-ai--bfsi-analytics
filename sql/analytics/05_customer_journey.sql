/*
QUERY ID: JRN-001
BUSINESS QUESTION: Where do customers drop off in the journey?
PURPOSE: Funnel analysis.
GRAIN: Funnel stages (one row).
*/
USE insightal_analytics;

SELECT 
    COUNT(*) AS stage_1_calls_attempted,
    SUM(CASE WHEN connection_status = 'Connected' THEN 1 ELSE 0 END) AS stage_2_connected,
    SUM(identity_verified_flag) AS stage_3_identity_verified,
    SUM(task_started_flag) AS stage_4_task_started,
    SUM(task_completed_flag) AS stage_5_task_completed,
    SUM(resolution_flag) AS stage_6_resolved,
    ROUND(SUM(CASE WHEN connection_status = 'Connected' THEN 1 ELSE 0 END) / COUNT(*), 4) AS cvr_attempt_to_connect,
    ROUND(SUM(identity_verified_flag) / NULLIF(SUM(CASE WHEN connection_status = 'Connected' THEN 1 ELSE 0 END), 0), 4) AS cvr_connect_to_verify,
    ROUND(SUM(task_completed_flag) / NULLIF(SUM(task_started_flag), 0), 4) AS cvr_start_to_complete
FROM fact_calls;
