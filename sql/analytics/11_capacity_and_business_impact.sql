/*
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
