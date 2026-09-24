import os
import pymysql
import pandas as pd
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

def get_connection():
    load_dotenv()
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database="insightal_analytics"
    )

def extract_call_level():
    query = """
    SELECT 
        c.call_key, c.call_id, c.customer_key, c.bot_key, c.campaign_key, c.date_key,
        c.intent_key, c.call_start_time, c.call_end_time, c.call_duration_seconds,
        c.call_status, c.connection_status, c.hangup_reason,
        c.attempt_number, c.confidence_score, c.outstanding_amount_at_call,
        c.days_past_due_at_call, c.dpd_bucket_at_call, c.risk_segment_at_call,
        c.identity_verified_flag, c.task_started_flag, c.task_completed_flag,
        c.resolution_flag, c.fallback_flag, c.escalation_flag, c.containment_flag,
        c.sentiment, c.sentiment_score, c.ptp_flag, c.ptp_amount,
        c.payment_status, c.payment_amount,
        cust.customer_segment, cust.customer_type, cust.loan_type, cust.state,
        b.bot_name, b.bot_version, b.language,
        cmp.campaign_name, cmp.campaign_type,
        d.date AS full_date, d.month, d.year, d.month_name, d.day_name, d.week
    FROM fact_calls c
    JOIN dim_customer cust ON c.customer_key = cust.customer_key
    JOIN dim_bot b ON c.bot_key = b.bot_key
    JOIN dim_campaign cmp ON c.campaign_key = cmp.campaign_key
    JOIN dim_date d ON c.date_key = d.date_key
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def extract_conversation_level():
    query = """
    SELECT 
        v.turn_id, v.call_key, v.conversation_id, v.turn_number, v.speaker, v.timestamp,
        v.expected_intent_key, v.detected_intent_key, v.confidence_score,
        v.sentiment, v.sentiment_score, v.fallback_flag, v.escalation_trigger_flag,
        i.intent_name AS expected_intent,
        i2.intent_name AS detected_intent
    FROM fact_conversation v
    LEFT JOIN dim_intent i ON v.expected_intent_key = i.intent_key
    LEFT JOIN dim_intent i2 ON v.detected_intent_key = i2.intent_key
    """
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def create_customer_dataset(df_calls, df_conv):
    cust_agg = df_calls.groupby('customer_key').agg(
        total_calls=('call_key', 'count'),
        connected_calls=('connection_status', lambda x: (x == 'Connected').sum()),
        average_duration=('call_duration_seconds', 'mean'),
        max_attempts=('attempt_number', 'max'),
        escalation_count=('escalation_flag', 'sum'),
        ptp_count=('ptp_flag', 'sum'),
        payment_success_count=('payment_status', lambda x: (x == 'Success').sum()),
        total_ptp_amount=('ptp_amount', 'sum'),
        total_payment_amount=('payment_amount', 'sum'),
        first_call_date=('call_start_time', 'min'),
        last_call_date=('call_start_time', 'max')
    ).reset_index()
    
    fb = df_conv.groupby('call_key')['fallback_flag'].sum().reset_index()
    calls_fb = df_calls[['call_key', 'customer_key']].merge(fb, on='call_key', how='left')
    calls_fb['fallback_flag'] = calls_fb['fallback_flag'].fillna(0)
    cust_fb = calls_fb.groupby('customer_key')['fallback_flag'].sum().rename('fallback_count').reset_index()
    
    cust_df = cust_agg.merge(cust_fb, on='customer_key', how='left')
    cust_df['fallback_count'] = cust_df['fallback_count'].fillna(0)
    return cust_df
