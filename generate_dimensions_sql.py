import pandas as pd
from src.data_generator.generators.intents import generate_intents
from src.data_generator.generators.bots import generate_bots
from src.data_generator.generators.campaigns import generate_campaigns

intents = generate_intents()
bots = generate_bots()
campaigns = generate_campaigns()

with open('sql/07_populate_dimensions.sql', 'a') as f:
    f.write("\n-- Populate dim_intent\n")
    for _, row in intents.iterrows():
        f.write(f"INSERT INTO dim_intent (intent_key, intent_id, intent_name, intent_category, business_function, expected_task) VALUES ({row['intent_key']}, '{row['intent_id']}', '{row['intent_name']}', '{row['intent_category']}', '{row['business_function']}', '{row['expected_task']}');\n")
        
    f.write("\n-- Populate dim_bot\n")
    for _, row in bots.iterrows():
        f.write(f"INSERT INTO dim_bot (bot_key, bot_id, bot_name, bot_version, language, model_type, deployment_date) VALUES ({row['bot_key']}, '{row['bot_id']}', '{row['bot_name']}', '{row['bot_version']}', '{row['language']}', '{row['model_type']}', '{row['deployment_date']}');\n")
        
    f.write("\n-- Populate dim_campaign\n")
    for _, row in campaigns.iterrows():
        f.write(f"INSERT INTO dim_campaign (campaign_key, campaign_id, campaign_name, campaign_type, business_unit, start_date, end_date, target_segment) VALUES ({row['campaign_key']}, '{row['campaign_id']}', '{row['campaign_name']}', '{row['campaign_type']}', '{row['business_unit']}', '{row['start_date']}', '{row['end_date']}', '{row['target_segment']}');\n")

    f.write("""
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
""")
