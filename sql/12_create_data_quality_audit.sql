USE insightal_staging;

CREATE TABLE IF NOT EXISTS data_quality_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    run_id VARCHAR(100) NOT NULL,
    run_timestamp DATETIME NOT NULL,
    check_id VARCHAR(100),
    check_name VARCHAR(255) NOT NULL,
    check_type VARCHAR(50) NOT NULL,
    dimension VARCHAR(50),
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    threshold DECIMAL(12, 4),
    observed_value DECIMAL(16, 4),
    affected_rows INT,
    message TEXT,
    execution_time_ms INT,
    baseline_value DECIMAL(16, 4),
    difference_value DECIMAL(16, 4),
    INDEX idx_run_id (run_id),
    INDEX idx_check_type (check_type)
) ENGINE=InnoDB;
