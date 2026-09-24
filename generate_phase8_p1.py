"""
One-time scaffolding utility; not part of Phase 8 execution.
"""
import os
def gen1():
    os.makedirs('python/eda', exist_ok=True)
    os.makedirs('artifacts/eda/figures', exist_ok=True)
    os.makedirs('artifacts/eda/tables', exist_ok=True)
    os.makedirs('artifacts/eda/exports', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    os.makedirs('notebooks', exist_ok=True)

    with open('python/eda/01_data_extraction.py', 'w', encoding='utf-8') as f:
        f.write('''import os
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
''')

    with open('python/eda/02_data_quality_profile.py', 'w', encoding='utf-8') as f:
        f.write('''def run_quality_profile(df_calls, df_conv, df_cust):
    return {
        'calls': {'row_count': len(df_calls), 'duplicate_rows': int(df_calls.duplicated().sum())},
        'conversations': {'row_count': len(df_conv), 'duplicate_rows': int(df_conv.duplicated().sum())},
        'customers': {'row_count': len(df_cust), 'duplicate_rows': int(df_cust.duplicated().sum())}
    }
''')

    with open('python/eda/03_univariate_analysis.py', 'w', encoding='utf-8') as f:
        f.write('''import pandas as pd
def run_univariate(df_calls, df_conv):
    res = {}
    cols_num = ['call_duration_seconds', 'attempt_number', 'confidence_score', 'outstanding_amount_at_call', 'days_past_due_at_call', 'ptp_amount', 'payment_amount']
    num_summary = {}
    for c in cols_num:
        if c in df_calls.columns:
            s = df_calls[c].dropna()
            num_summary[c] = {
                'count': len(s), 'missing': df_calls[c].isnull().sum(),
                'mean': float(s.mean()) if len(s)>0 else None,
                'median': float(s.median()) if len(s)>0 else None,
                'std': float(s.std()) if len(s)>0 else None,
                'min': float(s.min()) if len(s)>0 else None,
                'Q1': float(s.quantile(0.25)) if len(s)>0 else None,
                'Q3': float(s.quantile(0.75)) if len(s)>0 else None,
                'max': float(s.max()) if len(s)>0 else None
            }
    res['numerical_summary'] = num_summary
    cols_cat = ['connection_status', 'call_status', 'sentiment', 'risk_segment_at_call', 'dpd_bucket_at_call', 'customer_segment', 'loan_type', 'language', 'campaign_type', 'bot_version']
    res['categorical_summary'] = {c: df_calls[c].value_counts(dropna=False).to_dict() for c in cols_cat if c in df_calls.columns}
    return res
''')

    with open('python/eda/04_bivariate_analysis.py', 'w', encoding='utf-8') as f:
        f.write('''import pandas as pd
import matplotlib.pyplot as plt
def run_bivariate(df_calls, df_conv):
    res = {}
    
    # 1. Conf -> fallback
    if 'confidence_score' in df_conv.columns and 'fallback_flag' in df_conv.columns:
        df_conv['conf_q'] = pd.qcut(df_conv['confidence_score'], 4, duplicates='drop')
        res['confidence_vs_fallback'] = df_conv.groupby('conf_q', observed=True)['fallback_flag'].mean().to_dict()
    
    # 2. Conf -> escalation (call-level)
    call_conf = df_conv.groupby('call_key')['confidence_score'].mean().reset_index()
    call_conf = call_conf.merge(df_calls[['call_key', 'escalation_flag']], on='call_key', how='inner')
    call_conf['conf_q'] = pd.qcut(call_conf['confidence_score'], 4, duplicates='drop')
    res['confidence_vs_escalation'] = call_conf.groupby('conf_q', observed=True)['escalation_flag'].mean().to_dict()

    # 3. Sentiment -> escalation (call-level)
    call_sent = df_conv.groupby('call_key')['sentiment_score'].mean().reset_index()
    call_sent = call_sent.merge(df_calls[['call_key', 'escalation_flag']], on='call_key', how='inner')
    call_sent['sent_q'] = pd.qcut(call_sent['sentiment_score'], 3, duplicates='drop')
    res['sentiment_vs_escalation'] = call_sent.groupby('sent_q', observed=True)['escalation_flag'].mean().to_dict()

    # 4. DPD -> PTP
    df_col = df_calls[df_calls['campaign_type']=='Loan Collections']
    if 'days_past_due_at_call' in df_col.columns:
        df_col['dpd_q'] = pd.qcut(df_col['days_past_due_at_call'], 4, duplicates='drop')
        res['dpd_vs_ptp'] = df_col.groupby('dpd_q', observed=True)['ptp_flag'].mean().to_dict()

    # 5. Risk -> PTP
    res['risk_vs_ptp'] = df_col.groupby('risk_segment_at_call')['ptp_flag'].mean().to_dict()

    # 6. Task started -> Task completed
    ts = df_calls[df_calls['task_started_flag']==1]
    res['task_started_to_completed'] = ts['task_completed_flag'].mean()

    # 7. Task completed -> Resolution
    tc = df_calls[df_calls['task_completed_flag']==1]
    res['task_completed_to_resolution'] = tc['resolution_flag'].mean()

    # 8. Containment -> Resolution
    cnt = df_calls[df_calls['containment_flag']==1]
    res['containment_to_resolution'] = cnt['resolution_flag'].mean()

    # 9. Call duration -> Escalation
    df_calls['dur_q'] = pd.qcut(df_calls['call_duration_seconds'], 4, duplicates='drop')
    res['duration_vs_escalation'] = df_calls.groupby('dur_q', observed=True)['escalation_flag'].mean().to_dict()

    # 10. Attempts -> Escalation
    res['attempts_vs_escalation'] = df_calls.groupby('attempt_number')['escalation_flag'].mean().to_dict()

    return res
''')

    with open('python/eda/05_conversational_ai_analysis.py', 'w', encoding='utf-8') as f:
        f.write('''import pandas as pd
import matplotlib.pyplot as plt

def run_conversational_ai(df_calls, df_conv):
    res = {}
    
    # 1. Confidence dist
    plt.figure()
    df_conv['confidence_score'].dropna().plot(kind='hist', bins=30)
    plt.title('Confidence Distribution')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_conf_dist.png'); plt.close()
    
    conv_aug = df_conv.merge(df_calls[['call_key', 'bot_name', 'language', 'campaign_name', 'escalation_flag']], on='call_key', how='left')
    
    # 2. Conf by intent
    if conv_aug['expected_intent'].notnull().any():
        plt.figure()
        conv_aug.groupby('expected_intent')['confidence_score'].mean().sort_values().plot(kind='barh')
        plt.title('Confidence by Intent')
        plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_conf_intent.png'); plt.close()
        
    # 3. Conf by bot
    plt.figure()
    conv_aug.groupby('bot_name')['confidence_score'].mean().plot(kind='bar')
    plt.title('Confidence by Bot')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_conf_bot.png'); plt.close()

    # 4. Conf by language
    plt.figure()
    conv_aug.groupby('language')['confidence_score'].mean().plot(kind='bar')
    plt.title('Confidence by Language')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_conf_lang.png'); plt.close()
    
    # 5. Conf by campaign
    plt.figure()
    conv_aug.groupby('campaign_name')['confidence_score'].mean().plot(kind='bar')
    plt.title('Confidence by Campaign')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_conf_camp.png'); plt.close()
    
    # 6. Fallback by conf q
    plt.figure()
    conv_aug['conf_q'] = pd.qcut(conv_aug['confidence_score'], 4, duplicates='drop')
    conv_aug.groupby('conf_q', observed=True)['fallback_flag'].mean().plot(kind='bar')
    plt.title('Fallback by Confidence Quartile')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_conf_fallback.png'); plt.close()

    # Intent accuracy base
    cust_intents = conv_aug[(conv_aug['speaker'] == 'Customer') & (conv_aug['expected_intent_key'].notnull()) & (conv_aug['detected_intent_key'].notnull())].copy()
    cust_intents['is_accurate'] = (cust_intents['expected_intent_key'] == cust_intents['detected_intent_key']).astype(int)
    
    res['intent_denominator'] = len(cust_intents)
    if len(cust_intents) > 0:
        res['intent_accuracy_overall'] = cust_intents['is_accurate'].mean()
        # 7. Accuracy by intent
        plt.figure(figsize=(8,6))
        cust_intents.groupby('expected_intent')['is_accurate'].mean().sort_values().plot(kind='barh')
        plt.title('Accuracy by Intent')
        plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_acc_intent.png'); plt.close()
        
        # 8. Accuracy by bot
        plt.figure()
        cust_intents.groupby('bot_name')['is_accurate'].mean().plot(kind='bar')
        plt.title('Accuracy by Bot')
        plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_acc_bot.png'); plt.close()

        # 9. Accuracy by lang
        plt.figure()
        cust_intents.groupby('language')['is_accurate'].mean().plot(kind='bar')
        plt.title('Accuracy by Language')
        plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_acc_lang.png'); plt.close()

        # 10. Accuracy by campaign
        plt.figure()
        cust_intents.groupby('campaign_name')['is_accurate'].mean().plot(kind='bar')
        plt.title('Accuracy by Campaign')
        plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_acc_camp.png'); plt.close()

    # 11. Fallback by intent
    if conv_aug['expected_intent'].notnull().any():
        plt.figure()
        conv_aug.groupby('expected_intent')['fallback_flag'].mean().sort_values().plot(kind='barh')
        plt.title('Fallback by Intent')
        plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_fb_intent.png'); plt.close()

    # 12. Fallback by bot
    plt.figure()
    conv_aug.groupby('bot_name')['fallback_flag'].mean().plot(kind='bar')
    plt.title('Fallback by Bot')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_fb_bot.png'); plt.close()

    # 13. Sentiment dist
    plt.figure()
    conv_aug['sentiment'].value_counts().plot(kind='bar')
    plt.title('Sentiment Distribution')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_sent_dist.png'); plt.close()

    return res
''')

    with open('python/eda/06_collections_analysis.py', 'w', encoding='utf-8') as f:
        f.write('''import pandas as pd
import matplotlib.pyplot as plt

def run_collections(df_calls):
    df_col = df_calls[df_calls['campaign_type'] == 'Loan Collections'].copy()
    
    collection_rows = len(df_col)
    collection_campaign_types = sorted(df_col['campaign_type'].unique().tolist())
    invalid_collection_rows = len(df_col[df_col['campaign_type'] != 'Loan Collections'])
    
    if collection_rows == 0: 
        return {"collection_rows": 0, "collection_campaign_types": [], "invalid_collection_rows": 0}
    
    # 14, 15, 16, 17, 18, 19
    cols = ['dpd_bucket_at_call', 'risk_segment_at_call', 'customer_segment', 'loan_type', 'campaign_name', 'state']
    for c in cols:
        plt.figure()
        df_col.groupby(c)['ptp_flag'].mean().plot(kind='bar')
        plt.title(f'PTP Rate by {c}')
        plt.tight_layout(); plt.savefig(f'artifacts/eda/figures/col_ptp_{c}.png'); plt.close()

    metrics = {
        'ptp_rate': df_col['ptp_flag'].mean(),
        'successful_ptp_rate': df_col[df_col['ptp_flag']==1]['payment_status'].apply(lambda x: x=='Success').mean(),
        'collection_conversion_rate': df_col['payment_status'].apply(lambda x: x=='Success').mean(),
        'ptp_amount_mean': df_col['ptp_amount'].mean(),
        'payment_amount_mean': df_col['payment_amount'].mean(),
        'outstanding_amount_mean': df_col['outstanding_amount_at_call'].mean()
    }
    return {
        "collection_rows": collection_rows,
        "collection_campaign_types": collection_campaign_types,
        "invalid_collection_rows": invalid_collection_rows,
        "metrics": metrics
    }
''')

if __name__ == '__main__':
    gen1()
