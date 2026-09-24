import os

os.makedirs('sql', exist_ok=True)

with open('sql/01_create_databases.sql', 'w') as f:
    f.write("""DROP DATABASE IF EXISTS insightal_analytics;
DROP DATABASE IF EXISTS insightal_staging;
DROP DATABASE IF EXISTS insightal_raw;

CREATE DATABASE insightal_raw;
CREATE DATABASE insightal_staging;
CREATE DATABASE insightal_analytics;
""")

with open('sql/02_create_raw_tables.sql', 'w') as f:
    f.write("""USE insightal_raw;

DROP TABLE IF EXISTS raw_customers;
CREATE TABLE raw_customers (
    customer_key TEXT, customer_id TEXT, age TEXT, gender TEXT, state TEXT, city TEXT,
    customer_type TEXT, customer_segment TEXT, loan_type TEXT, customer_since_date TEXT,
    age_group TEXT, region TEXT
);

DROP TABLE IF EXISTS raw_calls;
CREATE TABLE raw_calls (
    call_key TEXT, call_id TEXT, customer_key TEXT, campaign_key TEXT, bot_key TEXT,
    call_start_time TEXT, date_key TEXT, attempt_number TEXT, connection_status TEXT,
    days_past_due_at_call TEXT, dpd_bucket_at_call TEXT, outstanding_amount_at_call TEXT,
    risk_segment_at_call TEXT, fallback_flag TEXT, confidence_score TEXT, sentiment TEXT,
    sentiment_score TEXT, escalation_flag TEXT, call_duration_seconds TEXT, call_end_time TEXT,
    task_started_flag TEXT, task_completed_flag TEXT, resolution_flag TEXT, containment_flag TEXT,
    ptp_flag TEXT, ptp_amount TEXT, payment_status TEXT, payment_amount TEXT, hangup_reason TEXT,
    call_status TEXT, intent_key TEXT, identity_verified_flag TEXT
);

DROP TABLE IF EXISTS raw_conversations;
CREATE TABLE raw_conversations (
    turn_key TEXT, turn_id TEXT, conversation_id TEXT, call_key TEXT, turn_number TEXT,
    speaker TEXT, timestamp TEXT, utterance TEXT, expected_intent_key TEXT, detected_intent_key TEXT,
    confidence_score TEXT, sentiment TEXT, sentiment_score TEXT, fallback_flag TEXT, escalation_trigger_flag TEXT
);
""")

with open('sql/03_load_raw_data.sql', 'w') as f:
    f.write("""-- This file intentionally left blank. 
-- As local_infile = OFF is strictly specified in the environment,
-- raw data ingestion is performed via Python batched inserts in run_etl.py.
""")

with open('sql/04_create_staging_tables.sql', 'w') as f:
    f.write("""USE insightal_staging;

DROP TABLE IF EXISTS stg_customers;
CREATE TABLE stg_customers (
    customer_key INT UNSIGNED, customer_id VARCHAR(255), age INT, gender VARCHAR(50),
    state VARCHAR(100), city VARCHAR(100), customer_type VARCHAR(100), customer_segment VARCHAR(100),
    loan_type VARCHAR(100), customer_since_date DATE, age_group VARCHAR(50), region VARCHAR(100),
    error_flag TINYINT(1) DEFAULT 0, error_reason TEXT
);

DROP TABLE IF EXISTS stg_calls;
CREATE TABLE stg_calls (
    call_key INT UNSIGNED, call_id VARCHAR(255), customer_key INT UNSIGNED, campaign_key INT UNSIGNED,
    bot_key INT UNSIGNED, call_start_time DATETIME, date_key INT UNSIGNED, attempt_number INT UNSIGNED,
    connection_status VARCHAR(50), days_past_due_at_call INT, dpd_bucket_at_call VARCHAR(50),
    outstanding_amount_at_call DECIMAL(12,2), risk_segment_at_call VARCHAR(50), fallback_flag TINYINT(1),
    confidence_score DECIMAL(5,4), sentiment VARCHAR(50), sentiment_score DECIMAL(5,4),
    escalation_flag TINYINT(1), call_duration_seconds INT, call_end_time DATETIME,
    task_started_flag TINYINT(1), task_completed_flag TINYINT(1), resolution_flag TINYINT(1),
    containment_flag TINYINT(1), ptp_flag TINYINT(1), ptp_amount DECIMAL(12,2), payment_status VARCHAR(50),
    payment_amount DECIMAL(12,2), hangup_reason VARCHAR(100), call_status VARCHAR(50),
    intent_key INT UNSIGNED, identity_verified_flag TINYINT(1), error_flag TINYINT(1) DEFAULT 0, error_reason TEXT
);

DROP TABLE IF EXISTS stg_conversations;
CREATE TABLE stg_conversations (
    turn_key BIGINT UNSIGNED, turn_id VARCHAR(255), conversation_id VARCHAR(255), call_key INT UNSIGNED,
    turn_number INT UNSIGNED, speaker VARCHAR(50), timestamp DATETIME, utterance TEXT,
    expected_intent_key INT UNSIGNED, detected_intent_key INT UNSIGNED, confidence_score DECIMAL(5,4),
    sentiment VARCHAR(50), sentiment_score DECIMAL(5,4), fallback_flag TINYINT(1),
    escalation_trigger_flag TINYINT(1), error_flag TINYINT(1) DEFAULT 0, error_reason TEXT
);
""")

with open('sql/05_transform_to_staging.sql', 'w') as f:
    f.write("""USE insightal_staging;

TRUNCATE TABLE stg_customers;
TRUNCATE TABLE stg_calls;
TRUNCATE TABLE stg_conversations;

INSERT INTO stg_customers (
    customer_key, customer_id, age, gender, state, city, customer_type, 
    customer_segment, loan_type, customer_since_date, age_group, region, error_flag, error_reason
)
SELECT DISTINCT
    CAST(customer_key AS UNSIGNED), customer_id, 
    CAST(age AS DECIMAL), 
    gender, state, city, customer_type, customer_segment, loan_type, 
    STR_TO_DATE(NULLIF(customer_since_date, 'NaT'), '%Y-%m-%d'),
    age_group, region,
    CASE WHEN age IS NULL OR age = 'nan' THEN 1 ELSE 0 END,
    CASE WHEN age IS NULL OR age = 'nan' THEN 'Invalid Age' ELSE NULL END
FROM insightal_raw.raw_customers;

INSERT INTO stg_calls (
    call_key, call_id, customer_key, campaign_key, bot_key, call_start_time, date_key, 
    attempt_number, connection_status, days_past_due_at_call, dpd_bucket_at_call, 
    outstanding_amount_at_call, risk_segment_at_call, fallback_flag, confidence_score, 
    sentiment, sentiment_score, escalation_flag, call_duration_seconds, call_end_time, 
    task_started_flag, task_completed_flag, resolution_flag, containment_flag, ptp_flag, 
    ptp_amount, payment_status, payment_amount, hangup_reason, call_status, intent_key, 
    identity_verified_flag, error_flag, error_reason
)
SELECT DISTINCT
    CAST(call_key AS UNSIGNED), call_id, CAST(customer_key AS UNSIGNED), 
    CAST(campaign_key AS UNSIGNED), CAST(bot_key AS UNSIGNED), 
    STR_TO_DATE(NULLIF(call_start_time, 'NaT'), '%Y-%m-%d %H:%i:%s'), 
    CAST(date_key AS UNSIGNED), CAST(attempt_number AS UNSIGNED), connection_status, 
    CAST(days_past_due_at_call AS SIGNED), dpd_bucket_at_call, 
    CAST(outstanding_amount_at_call AS DECIMAL(12,2)), risk_segment_at_call, 
    CAST(fallback_flag AS UNSIGNED), CAST(NULLIF(confidence_score, 'nan') AS DECIMAL(5,4)), sentiment, 
    CAST(NULLIF(sentiment_score, 'nan') AS DECIMAL(5,4)), CAST(escalation_flag AS UNSIGNED), 
    CAST(call_duration_seconds AS SIGNED), 
    STR_TO_DATE(NULLIF(call_end_time, 'NaT'), '%Y-%m-%d %H:%i:%s'), 
    CAST(task_started_flag AS UNSIGNED), CAST(task_completed_flag AS UNSIGNED), 
    CAST(resolution_flag AS UNSIGNED), CAST(containment_flag AS UNSIGNED), 
    CAST(ptp_flag AS UNSIGNED), CAST(NULLIF(ptp_amount, 'nan') AS DECIMAL(12,2)), payment_status, 
    CAST(NULLIF(payment_amount, 'nan') AS DECIMAL(12,2)), hangup_reason, call_status, 
    CAST(NULLIF(NULLIF(intent_key, 'nan'), '') AS UNSIGNED), CAST(identity_verified_flag AS UNSIGNED),
    CASE WHEN CAST(call_duration_seconds AS SIGNED) < 0 OR call_start_time = 'NaT' THEN 1 ELSE 0 END,
    CASE WHEN CAST(call_duration_seconds AS SIGNED) < 0 THEN 'Negative Duration' 
         WHEN call_start_time = 'NaT' THEN 'Invalid Date' ELSE NULL END
FROM insightal_raw.raw_calls;

INSERT INTO stg_conversations (
    turn_key, turn_id, conversation_id, call_key, turn_number, speaker, timestamp, 
    utterance, expected_intent_key, detected_intent_key, confidence_score, sentiment, 
    sentiment_score, fallback_flag, escalation_trigger_flag, error_flag, error_reason
)
SELECT DISTINCT
    CAST(turn_key AS UNSIGNED), turn_id, conversation_id, CAST(call_key AS UNSIGNED), 
    CAST(turn_number AS UNSIGNED), speaker, 
    STR_TO_DATE(NULLIF(timestamp, 'NaT'), '%Y-%m-%d %H:%i:%s'), 
    utterance, 
    CAST(NULLIF(NULLIF(expected_intent_key, 'nan'), '') AS UNSIGNED), 
    CAST(NULLIF(NULLIF(detected_intent_key, 'nan'), '') AS UNSIGNED), 
    CAST(NULLIF(confidence_score, 'nan') AS DECIMAL(5,4)), sentiment, 
    CAST(NULLIF(sentiment_score, 'nan') AS DECIMAL(5,4)), CAST(fallback_flag AS UNSIGNED), 
    CAST(escalation_trigger_flag AS UNSIGNED),
    CASE WHEN timestamp = 'NaT' THEN 1 ELSE 0 END,
    CASE WHEN timestamp = 'NaT' THEN 'Invalid Timestamp' ELSE NULL END
FROM insightal_raw.raw_conversations;
""")

with open('sql/06_create_dimensions.sql', 'w') as f:
    f.write("""USE insightal_analytics;

DROP TABLE IF EXISTS dim_customer;
CREATE TABLE dim_customer (
    customer_key INT UNSIGNED PRIMARY KEY,
    customer_id VARCHAR(100) UNIQUE,
    age INT,
    age_group VARCHAR(50),
    gender VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(100),
    region VARCHAR(100),
    customer_type VARCHAR(100),
    customer_segment VARCHAR(100),
    loan_type VARCHAR(100),
    customer_since_date DATE
) ENGINE=InnoDB;

DROP TABLE IF EXISTS dim_intent;
CREATE TABLE dim_intent (
    intent_key INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    intent_id VARCHAR(100) UNIQUE,
    intent_name VARCHAR(255),
    intent_category VARCHAR(100),
    business_function VARCHAR(100),
    expected_task VARCHAR(255)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS dim_bot;
CREATE TABLE dim_bot (
    bot_key INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    bot_id VARCHAR(100) UNIQUE,
    bot_name VARCHAR(100),
    bot_version VARCHAR(50),
    language VARCHAR(50),
    model_type VARCHAR(50),
    deployment_date DATE
) ENGINE=InnoDB;

DROP TABLE IF EXISTS dim_campaign;
CREATE TABLE dim_campaign (
    campaign_key INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    campaign_id VARCHAR(100) UNIQUE,
    campaign_name VARCHAR(255),
    campaign_type VARCHAR(100),
    business_unit VARCHAR(100),
    start_date DATE,
    end_date DATE,
    target_segment VARCHAR(100)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date (
    date_key INT UNSIGNED PRIMARY KEY,
    date DATE,
    day INT,
    day_name VARCHAR(50),
    week INT,
    month INT,
    month_name VARCHAR(50),
    month_number INT,
    quarter INT,
    year INT,
    financial_year VARCHAR(50),
    is_weekend TINYINT(1)
) ENGINE=InnoDB;
""")

with open('sql/07_populate_dimensions.sql', 'w') as f:
    f.write("""USE insightal_analytics;

INSERT INTO dim_customer 
SELECT customer_key, customer_id, age, age_group, gender, city, state, region, 
       customer_type, customer_segment, loan_type, customer_since_date
FROM insightal_staging.stg_customers WHERE error_flag = 0;

-- Intents, Bots, Campaigns need to be generated or we can load them from the Python configurations if we saved them.
-- Wait, Phase 4 didn't save dimension CSVs for intents, bots, campaigns? Yes it did! Wait... did I save them in Phase 4?
-- Let me check if they exist in data/clean/
""")
