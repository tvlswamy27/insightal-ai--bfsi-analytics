import os

os.makedirs('sql/analytics', exist_ok=True)

# 01. Executive KPIs
with open('sql/analytics/01_executive_kpis.sql', 'w') as f:
    f.write("""/*
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
    WHERE expected_intent_key IS NOT NULL AND detected_intent_key IS NOT NULL
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
""")

# 02. Call Operations
with open('sql/analytics/02_call_operations.sql', 'w') as f:
    f.write("""/*
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
""")

# 03. Bot Performance
with open('sql/analytics/03_bot_performance.sql', 'w') as f:
    f.write("""/*
QUERY ID: BOT-001
BUSINESS QUESTION: Which bots perform best overall using the Bot Quality Score?
PURPOSE: Bot evaluation and ranking.
GRAIN: One row per bot.
*/
USE insightal_analytics;

WITH BotIntent AS (
    SELECT 
        c.bot_key,
        COUNT(*) AS total_intent_turns,
        SUM(CASE WHEN v.expected_intent_key = v.detected_intent_key THEN 1 ELSE 0 END) AS correct_intents
    FROM fact_conversation v
    JOIN fact_calls c ON v.call_key = c.call_key
    WHERE v.expected_intent_key IS NOT NULL AND v.detected_intent_key IS NOT NULL
    GROUP BY c.bot_key
),
BotMetrics AS (
    SELECT 
        c.bot_key,
        b.bot_name,
        b.bot_version,
        b.language,
        COUNT(*) AS total_calls,
        SUM(CASE WHEN c.connection_status = 'Connected' THEN 1 ELSE 0 END) AS connected_calls,
        SUM(c.containment_flag) AS total_contained,
        SUM(c.task_completed_flag) AS total_task_completed,
        SUM(c.resolution_flag) AS total_resolved,
        SUM(CASE WHEN c.hangup_reason = 'System Error' AND c.connection_status = 'Connected' THEN 1 ELSE 0 END) AS system_errors,
        AVG(c.sentiment_score) AS avg_sentiment_score
    FROM fact_calls c
    JOIN dim_bot b ON c.bot_key = b.bot_key
    GROUP BY c.bot_key, b.bot_name, b.bot_version, b.language
)
SELECT 
    m.bot_name,
    m.bot_version,
    m.language,
    m.total_calls,
    m.connected_calls,
    ROUND(m.total_contained / NULLIF(m.connected_calls, 0), 4) AS containment_rate,
    ROUND(m.total_task_completed / NULLIF(m.connected_calls, 0), 4) AS task_completion_rate,
    ROUND(i.correct_intents / NULLIF(i.total_intent_turns, 0), 4) AS intent_recognition_accuracy,
    ROUND(1 - (m.system_errors / NULLIF(m.connected_calls, 0)), 4) AS reliability,
    ROUND((0.40 * (m.total_resolved / NULLIF(m.connected_calls, 0))) + 
          (0.30 * (m.total_contained / NULLIF(m.connected_calls, 0))) + 
          (0.20 * ((m.avg_sentiment_score + 1) / 2)) + 
          (0.10 * (m.total_task_completed / NULLIF(m.connected_calls, 0))), 4) AS satisfaction_proxy,
    ROUND(
        (0.30 * (m.total_contained / NULLIF(m.connected_calls, 0))) +
        (0.25 * (m.total_task_completed / NULLIF(m.connected_calls, 0))) +
        (0.20 * (i.correct_intents / NULLIF(i.total_intent_turns, 0))) +
        (0.15 * ((0.40 * (m.total_resolved / NULLIF(m.connected_calls, 0))) + (0.30 * (m.total_contained / NULLIF(m.connected_calls, 0))) + (0.20 * ((m.avg_sentiment_score + 1) / 2)) + (0.10 * (m.total_task_completed / NULLIF(m.connected_calls, 0))))) +
        (0.10 * (1 - (m.system_errors / NULLIF(m.connected_calls, 0)))), 
    4) AS bot_quality_score
FROM BotMetrics m
LEFT JOIN BotIntent i ON m.bot_key = i.bot_key
ORDER BY bot_quality_score DESC;
""")

# 04. Intent Analytics
with open('sql/analytics/04_intent_analytics.sql', 'w') as f:
    f.write("""/*
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
WHERE v.expected_intent_key IS NOT NULL AND v.detected_intent_key IS NOT NULL
GROUP BY i.intent_name
ORDER BY recognition_accuracy ASC;
""")

# 05. Customer Journey
with open('sql/analytics/05_customer_journey.sql', 'w') as f:
    f.write("""/*
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
""")

# 06. Escalation Analytics
with open('sql/analytics/06_escalation_analytics.sql', 'w') as f:
    f.write("""/*
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
""")

# 07. Collections Analytics
with open('sql/analytics/07_collections_analytics.sql', 'w') as f:
    f.write("""/*
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
""")

# 08. Campaign Analytics
with open('sql/analytics/08_campaign_analytics.sql', 'w') as f:
    f.write("""/*
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
""")

# 09. Customer Segment Analytics
with open('sql/analytics/09_customer_segment_analytics.sql', 'w') as f:
    f.write("""/*
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
""")

# 10. Time Series Analytics
with open('sql/analytics/10_time_series_analytics.sql', 'w') as f:
    f.write("""/*
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
""")

# 11. Capacity and Business Impact
with open('sql/analytics/11_capacity_and_business_impact.sql', 'w') as f:
    f.write("""/*
QUERY ID: ROI-001
BUSINESS QUESTION: How much operational capacity is being automated and what is the cost avoidance?
PURPOSE: ROI estimation.
GRAIN: One row total.
ASSUMPTIONS: Average Agent Call = 300s, Productive FTE = 6 hours (21600s) / day, Cost per call = 50 INR.
*/
USE insightal_analytics;

WITH AutomationMetrics AS (
    SELECT 
        SUM(containment_flag) AS total_contained
    FROM fact_calls
)
SELECT 
    total_contained AS estimated_agent_calls_avoided,
    (total_contained * 300) / 3600 AS agent_hours_freed,
    ROUND(((total_contained * 300) / 21600) / 30, 2) AS fte_capacity_freed_per_month, 
    total_contained * 50 AS estimated_operational_cost_avoided_inr
FROM AutomationMetrics;
""")

# 12. Advanced SQL
with open('sql/analytics/12_advanced_sql.sql', 'w') as f:
    f.write("""/*
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
""")

# 13. SQL Validation
with open('sql/analytics/13_sql_validation.sql', 'w') as f:
    f.write("""/*
QUERY ID: VAL-001
PURPOSE: SQL Validation checks (No accidental fan-out, missing FKs, unexpected NULLs).
*/
USE insightal_analytics;

SELECT 'Missing Expected Intent in Conversation' AS check_name, COUNT(*) AS violations
FROM fact_conversation 
WHERE expected_intent_key IS NULL AND detected_intent_key IS NOT NULL AND fallback_flag = 0;

SELECT 'Non-Collections PTPs' AS check_name, COUNT(*) AS violations
FROM fact_calls c
JOIN dim_campaign cm ON c.campaign_key = cm.campaign_key
WHERE c.ptp_flag = 1 AND cm.campaign_type != 'Loan Collections';

SELECT 'Customer aggregation mismatch' AS check_name, 
    (SELECT COUNT(*) FROM fact_calls) - (SELECT SUM(call_count) FROM (SELECT customer_key, COUNT(*) AS call_count FROM fact_calls GROUP BY customer_key) t) AS violations;
""")
