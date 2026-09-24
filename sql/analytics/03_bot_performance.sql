/*
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
    WHERE v.expected_intent_key IS NOT NULL AND v.detected_intent_key IS NOT NULL AND v.speaker = 'Customer'
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
