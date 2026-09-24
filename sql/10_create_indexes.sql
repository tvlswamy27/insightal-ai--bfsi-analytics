USE insightal_analytics;

CREATE INDEX idx_calls_customer ON fact_calls(customer_key);
CREATE INDEX idx_calls_campaign ON fact_calls(campaign_key);
CREATE INDEX idx_calls_bot ON fact_calls(bot_key);
CREATE INDEX idx_calls_date ON fact_calls(date_key);
CREATE INDEX idx_calls_intent ON fact_calls(intent_key);
CREATE INDEX idx_calls_start ON fact_calls(call_start_time);

CREATE INDEX idx_conv_call ON fact_conversation(call_key);
CREATE INDEX idx_conv_expected ON fact_conversation(expected_intent_key);
CREATE INDEX idx_conv_detected ON fact_conversation(detected_intent_key);
CREATE INDEX idx_conv_timestamp ON fact_conversation(timestamp);
