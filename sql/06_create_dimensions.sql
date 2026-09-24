USE insightal_analytics;

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
