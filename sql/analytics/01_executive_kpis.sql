/*
QUERY ID: EXE-001
BUSINESS QUESTION: What are the top-level executive KPIs for the conversational AI platform?
PURPOSE: Executive KPI summary.
GRAIN: Entire reporting period (one row).
*/
USE insightal_analytics;

WITH CallBase AS (
    SELECT 
        COUNT(*) AS total_calls,
        SUM(CASE WHEN connection_status = 'Connected' THEN 1 ELSE 0 END) AS connected_calls,
        AVG(call_duration_seconds) AS avg_duration_seconds,
        SUM(containment_flag) AS total_contained,
        SUM(escalation_flag) AS total_escalated,
        SUM(resolution_flag) AS total_resolved,
        SUM(task_completed_flag) AS total_task_completed,
        SUM(ptp_flag) AS total_ptps,
        SUM(CASE WHEN payment_status = 'Success' THEN 1 ELSE 0 END) AS total_successful_payments,
        SUM(payment_amount) AS total_payment_amount,
        SUM(outstanding_amount_at_call) AS total_outstanding
    FROM fact_calls
),
IntentBase AS (
    SELECT 
        COUNT(*) AS total_intent_turns,
        SUM(CASE WHEN expected_intent_key = detected_intent_key THEN 1 ELSE 0 END) AS correct_intents,
        SUM(fallback_flag) AS total_fallbacks
    FROM fact_conversation
    WHERE expected_intent_key IS NOT NULL AND detected_intent_key IS NOT NULL AND speaker = 'Customer'
),
TurnBase AS (
    SELECT COUNT(*) AS total_turns, SUM(fallback_flag) AS total_fallbacks FROM fact_conversation
)
SELECT 
    c.total_calls,
    c.connected_calls,
    ROUND(c.connected_calls / NULLIF(c.total_calls, 0), 4) AS connection_rate,
    ROUND(c.avg_duration_seconds, 2) AS avg_call_duration_seconds,
    ROUND(c.total_contained / NULLIF(c.connected_calls, 0), 4) AS containment_rate,
    ROUND(c.total_escalated / NULLIF(c.connected_calls, 0), 4) AS escalation_rate,
    ROUND(c.total_resolved / NULLIF(c.connected_calls, 0), 4) AS resolution_rate,
    ROUND(c.total_task_completed / NULLIF(c.connected_calls, 0), 4) AS task_completion_rate,
    ROUND(t.total_fallbacks / NULLIF(t.total_turns, 0), 4) AS fallback_rate,
    ROUND(i.correct_intents / NULLIF(i.total_intent_turns, 0), 4) AS intent_recognition_accuracy,
    ROUND(c.total_ptps / NULLIF(c.connected_calls, 0), 4) AS ptp_rate,
    ROUND(c.total_successful_payments / NULLIF(c.total_ptps, 0), 4) AS successful_ptp_rate,
    ROUND(c.total_successful_payments / NULLIF(c.connected_calls, 0), 4) AS collection_conversion_rate,
    c.total_payment_amount AS successful_collection_amount,
    ROUND(c.total_payment_amount / NULLIF(c.total_outstanding, 0), 4) AS outstanding_collected_ratio
FROM CallBase c
CROSS JOIN IntentBase i
CROSS JOIN TurnBase t;
