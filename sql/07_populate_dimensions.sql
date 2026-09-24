USE insightal_analytics;

INSERT INTO dim_customer 
SELECT customer_key, customer_id, age, age_group, gender, city, state, region, 
       customer_type, customer_segment, loan_type, customer_since_date
FROM insightal_staging.stg_customers WHERE error_flag = 0;

-- Intents, Bots, Campaigns need to be generated or we can load them from the Python configurations if we saved them.
-- Wait, Phase 4 didn't save dimension CSVs for intents, bots, campaigns? Yes it did! Wait... did I save them in Phase 4?
-- Let me check if they exist in data/clean/

-- Populate dim_intent
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (1, 'INT_PAY_REMIND', 'Payment Reminder', 'Collections', 'Debt Recovery', 'Remind Payment');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (2, 'INT_PTP', 'Promise to Pay', 'Collections', 'Debt Recovery', 'Capture Date');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (3, 'INT_PAY_DIFF', 'Payment Difficulty', 'Collections', 'Debt Recovery', 'Offer Restructure');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (4, 'INT_OVERDUE', 'Overdue Payment', 'Collections', 'Debt Recovery', 'Collect Payment');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (5, 'INT_PAY_CONF', 'Payment Confirmation', 'Collections', 'Debt Recovery', 'Confirm Payment');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (6, 'INT_LOAN_APP', 'Loan Application', 'Loan', 'Retail Banking', 'Start Application');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (7, 'INT_LOAN_STAT', 'Loan Status', 'Loan', 'Retail Banking', 'Provide Status');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (8, 'INT_LOAN_ELIG', 'Loan Eligibility', 'Loan', 'Retail Banking', 'Check Eligibility');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (9, 'INT_EMI_QUERY', 'EMI Query', 'Loan', 'Retail Banking', 'Provide EMI Details');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (10, 'INT_OUTSTAND_AMT', 'Outstanding Amount', 'Loan', 'Retail Banking', 'Provide Balance');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (11, 'INT_PREM_QUERY', 'Premium Query', 'Insurance', 'Insurance', 'Provide Premium');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (12, 'INT_RENEWAL', 'Policy Renewal', 'Insurance', 'Insurance', 'Renew Policy');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (13, 'INT_CLAIM_STAT', 'Claim Status', 'Insurance', 'Insurance', 'Provide Status');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (14, 'INT_CLAIM_QUERY', 'Claim Query', 'Insurance', 'Insurance', 'Explain Claim');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (15, 'INT_PAY_FAIL', 'Payment Failure', 'Support', 'Customer Service', 'Resolve Failure');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (16, 'INT_ACCT_QUERY', 'Account Query', 'Support', 'Customer Service', 'Provide Info');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (17, 'INT_COMPLAINT', 'Complaint', 'Support', 'Customer Service', 'Log Complaint');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (18, 'INT_GEN_SUPPORT', 'General Support', 'Support', 'Customer Service', 'Provide Support');
INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES (19, 'INT_PROD_INT', 'Product Interest', 'Lead Qualification', 'Sales', 'Qualify Lead');

-- Populate dim_bot
INSERT INTO dim_bot (bot_key, bot_id, bot_name, bot_version, language, model_type, deployment_date) VALUES (1, 'BOT_V1_EN', 'Insightal Voice', 'v1.0', 'English', 'Generative', '2025-01-01');
INSERT INTO dim_bot (bot_key, bot_id, bot_name, bot_version, language, model_type, deployment_date) VALUES (2, 'BOT_V1_HI', 'Insightal Voice', 'v1.0', 'Hindi', 'Generative', '2025-01-01');
INSERT INTO dim_bot (bot_key, bot_id, bot_name, bot_version, language, model_type, deployment_date) VALUES (3, 'BOT_V1.1_EN', 'Insightal Voice', 'v1.1', 'English', 'Generative', '2026-03-01');
INSERT INTO dim_bot (bot_key, bot_id, bot_name, bot_version, language, model_type, deployment_date) VALUES (4, 'BOT_V2_EN', 'Insightal Voice Pro', 'v2.0', 'English', 'Generative', '2026-05-01');
INSERT INTO dim_bot (bot_key, bot_id, bot_name, bot_version, language, model_type, deployment_date) VALUES (5, 'BOT_V1_TE', 'Insightal Voice', 'v1.0', 'Telugu', 'Generative', '2025-06-01');
INSERT INTO dim_bot (bot_key, bot_id, bot_name, bot_version, language, model_type, deployment_date) VALUES (6, 'BOT_V1_TA', 'Insightal Voice', 'v1.0', 'Tamil', 'Generative', '2025-06-01');

-- Populate dim_campaign
INSERT INTO dim_campaign (campaign_key, campaign_id, campaign_name, campaign_type, business_unit, start_date, end_date, target_segment) VALUES (1, 'CAMP_001', 'Q1 Collections', 'Loan Collections', 'Retail Banking', '2026-01-01', '2026-03-31', 'DPD 31-90');
INSERT INTO dim_campaign (campaign_key, campaign_id, campaign_name, campaign_type, business_unit, start_date, end_date, target_segment) VALUES (2, 'CAMP_002', 'Q2 Collections', 'Loan Collections', 'Retail Banking', '2026-04-01', '2026-06-30', 'DPD 31-90');
INSERT INTO dim_campaign (campaign_key, campaign_id, campaign_name, campaign_type, business_unit, start_date, end_date, target_segment) VALUES (3, 'CAMP_003', 'Payment Reminder Auto', 'Payment Reminder', 'Retail Banking', '2025-01-01', 'NaT', 'DPD 0-30');
INSERT INTO dim_campaign (campaign_key, campaign_id, campaign_name, campaign_type, business_unit, start_date, end_date, target_segment) VALUES (4, 'CAMP_004', 'Spring Loan Promo', 'Loan Application', 'Retail Banking', '2026-02-01', '2026-04-30', 'Low Risk');
INSERT INTO dim_campaign (campaign_key, campaign_id, campaign_name, campaign_type, business_unit, start_date, end_date, target_segment) VALUES (5, 'CAMP_005', 'Auto Renewal Alerts', 'Insurance Renewal', 'Insurance', '2025-01-01', 'NaT', 'All');
INSERT INTO dim_campaign (campaign_key, campaign_id, campaign_name, campaign_type, business_unit, start_date, end_date, target_segment) VALUES (6, 'CAMP_006', 'General Support Inbound', 'Customer Support', 'Customer Service', '2025-01-01', 'NaT', 'All');
INSERT INTO dim_campaign (campaign_key, campaign_id, campaign_name, campaign_type, business_unit, start_date, end_date, target_segment) VALUES (7, 'CAMP_007', 'Credit Card Leads', 'Lead Qualification', 'Sales', '2026-01-15', '2026-05-15', 'High Value');

-- Populate dim_date using a recursive CTE (MySQL 8.0+)
SET SESSION cte_max_recursion_depth = 2000;
INSERT INTO dim_date
WITH RECURSIVE date_range AS (
    SELECT '2025-01-01' AS d
    UNION ALL
    SELECT DATE_ADD(d, INTERVAL 1 DAY)
    FROM date_range
    WHERE d < '2027-12-31'
)
SELECT 
    CAST(DATE_FORMAT(d, '%Y%m%d') AS UNSIGNED) as date_key,
    d as date,
    DAY(d) as day,
    DAYNAME(d) as day_name,
    WEEK(d, 1) as week,
    MONTH(d) as month,
    MONTHNAME(d) as month_name,
    MONTH(d) as month_number,
    QUARTER(d) as quarter,
    YEAR(d) as year,
    CASE 
        WHEN MONTH(d) >= 4 THEN CONCAT('FY', SUBSTRING(YEAR(d), 3, 2), '-', SUBSTRING(YEAR(d)+1, 3, 2))
        ELSE CONCAT('FY', SUBSTRING(YEAR(d)-1, 3, 2), '-', SUBSTRING(YEAR(d), 3, 2))
    END as financial_year,
    CASE WHEN DAYOFWEEK(d) IN (1, 7) THEN 1 ELSE 0 END as is_weekend
FROM date_range;
