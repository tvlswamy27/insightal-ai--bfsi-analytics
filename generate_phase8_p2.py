"""
One-time scaffolding utility; not part of Phase 8 execution.
"""
def gen2():
    with open('python/eda/07_customer_behavior_analysis.py', 'w', encoding='utf-8') as f:
        f.write('''import pandas as pd
import matplotlib.pyplot as plt
def run_customer_behavior(df_cust):
    res = {}
    # 20. Calls per cust
    plt.figure()
    df_cust['total_calls'].value_counts().sort_index().plot(kind='bar')
    plt.title('Calls per Customer')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/cust_calls.png'); plt.close()
    
    res['distribution_calls'] = df_cust['total_calls'].value_counts().to_dict()
    res['distribution_attempts'] = df_cust['max_attempts'].value_counts().to_dict()
    res['distribution_escalation'] = df_cust['escalation_count'].value_counts().to_dict()
    res['distribution_fallback'] = df_cust['fallback_count'].value_counts().to_dict()
    res['ptp_total'] = df_cust['ptp_count'].sum()
    return res
''')

    with open('python/eda/08_temporal_analysis.py', 'w', encoding='utf-8') as f:
        f.write('''import pandas as pd
import matplotlib.pyplot as plt

def run_temporal(df_calls):
    df_calls['full_date'] = pd.to_datetime(df_calls['full_date'])
    daily = df_calls.groupby('full_date')
    
    metrics = {
        'volume': daily.size(),
        'connection_rate': daily['connection_status'].apply(lambda x: (x=='Connected').mean()),
        'containment_rate': daily['containment_flag'].mean(),
        'escalation_rate': daily['escalation_flag'].mean(),
        'resolution_rate': daily['resolution_flag'].mean(),
        'ptp_rate': daily['ptp_flag'].mean(),
        'payment_amount': daily['payment_amount'].sum()
    }
    
    # 21, 22, 23, 24, 25, 26, 27
    daily_stats = {}
    for name, s in metrics.items():
        daily_stats[name] = s.to_dict()
        plt.figure(figsize=(10,5))
        s.plot(label='Daily', alpha=0.5)
        s.rolling(7).mean().plot(label='7-Day Rolling', linewidth=2)
        plt.title(f'Daily {name}')
        plt.legend()
        plt.tight_layout(); plt.savefig(f'artifacts/eda/figures/time_{name}.png'); plt.close()

    weekly_vol = df_calls.groupby('week').size().to_dict()
    monthly_vol = df_calls.groupby('month').size().to_dict()
    
    return {"daily_stats": daily_stats, "weekly_volume": weekly_vol, "monthly_volume": monthly_vol}
''')

    with open('python/eda/09_escalation_analysis.py', 'w', encoding='utf-8') as f:
        f.write('''import pandas as pd
import matplotlib.pyplot as plt

def run_escalation(df_calls, df_conv):
    agg = df_conv.groupby('call_key').agg(
        average_confidence=('confidence_score', 'mean'),
        minimum_confidence=('confidence_score', 'min'),
        maximum_confidence=('confidence_score', 'max'),
        confidence_std=('confidence_score', 'std'),
        fallback_count=('fallback_flag', 'sum'),
        turn_count=('turn_id', 'count'),
        average_sentiment_score=('sentiment_score', 'mean'),
        minimum_sentiment_score=('sentiment_score', 'min'),
        maximum_sentiment_score=('sentiment_score', 'max')
    ).reset_index()

    df = df_calls.merge(agg, on='call_key', how='left')

    # Analyze associations - exactly 3 plots (28, 29, 30) -> Max 30 plots total!
    cols = ['average_confidence', 'fallback_count', 'average_sentiment_score']
            
    for c in cols:
        plt.figure()
        if df[c].nunique() > 10:
            df['q'] = pd.qcut(df[c], 4, duplicates='drop')
            df.groupby('q', observed=True)['escalation_flag'].mean().plot(kind='bar')
            df.drop('q', axis=1, inplace=True)
        else:
            df.groupby(c)['escalation_flag'].mean().plot(kind='bar')
        plt.title(f'Escalation Association: {c}')
        plt.tight_layout(); plt.savefig(f'artifacts/eda/figures/esc_assoc_{c}.png'); plt.close()

    return {"merged_count": len(df), "merged_unique": df['call_key'].nunique()}
''')

    with open('python/eda/10_correlation_analysis.py', 'w', encoding='utf-8') as f:
        f.write('''import pandas as pd
from scipy.stats import spearmanr
def run_correlation(df_calls, df_conv):
    res = {}
    
    def calc_corr(df, col1, col2, name):
        df_clean = df.dropna(subset=[col1, col2])
        if len(df_clean) > 0:
            r, p = spearmanr(df_clean[col1], df_clean[col2])
            res[name] = {
                "variables": f"{col1}, {col2}", "method": "Spearman", "n": len(df_clean),
                "coefficient": float(r), "p_value": float(p),
                "interpretation": "Weak association" if abs(r) < 0.3 else "Strong association",
                "limitation": "Does not imply causality"
            }
            
    calc_corr(df_calls, 'call_duration_seconds', 'attempt_number', 'dur_vs_att')
    calc_corr(df_conv, 'confidence_score', 'fallback_flag', 'conf_vs_fb')
    calc_corr(df_conv, 'confidence_score', 'sentiment_score', 'conf_vs_sent')
    calc_corr(df_calls, 'days_past_due_at_call', 'ptp_amount', 'dpd_vs_ptp_amt')
    calc_corr(df_calls, 'outstanding_amount_at_call', 'payment_amount', 'outst_vs_pay')
    
    return res
''')

    with open('python/eda/11_outlier_analysis.py', 'w', encoding='utf-8') as f:
        f.write('''import pandas as pd
def run_outliers(df_calls):
    cols = ['call_duration_seconds', 'attempt_number', 'outstanding_amount_at_call', 'days_past_due_at_call', 'ptp_amount', 'payment_amount']
    res = {}
    for c in cols:
        s = df_calls[c].dropna()
        if len(s) == 0: continue
        q1 = s.quantile(0.25); q3 = s.quantile(0.75)
        iqr = q3 - q1
        lb = q1 - 1.5 * iqr; ub = q3 + 1.5 * iqr
        out = s[(s < lb) | (s > ub)]
        res[c] = {
            "count": len(s), "Q1": float(q1), "Q3": float(q3), "IQR": float(iqr),
            "lower_bound": float(lb), "upper_bound": float(ub),
            "outlier_count": len(out), "outlier_percentage": float(len(out)/len(s)*100),
            "minimum_outlier": float(out.min()) if len(out)>0 else None,
            "maximum_outlier": float(out.max()) if len(out)>0 else None
        }
    return res
''')

    with open('python/eda/12_ml_readiness.py', 'w', encoding='utf-8') as f:
        f.write('''def run_ml_readiness():
    allowed = [
        {"feature_name": "detected_intent_key", "source_table": "fact_conversation", "data_type": "int", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": 20, "ml_allowed": True, "leakage_risk": False, "reason": "Available during call"},
        {"feature_name": "confidence_score", "source_table": "fact_conversation", "data_type": "float", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Available during inference"},
        {"feature_name": "sentiment", "source_table": "fact_conversation", "data_type": "str", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": 3, "ml_allowed": True, "leakage_risk": False, "reason": "Sequential calculation"},
        {"feature_name": "sentiment_score", "source_table": "fact_conversation", "data_type": "float", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Sequential calculation"},
        {"feature_name": "fallback_count_so_far", "source_table": "derived", "data_type": "int", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Accumulates incrementally"},
        {"feature_name": "turn_count_so_far", "source_table": "derived", "data_type": "int", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Accumulates incrementally"},
        {"feature_name": "call_duration_so_far", "source_table": "derived", "data_type": "int", "availability_timing": "CURRENT-CALL POINT-IN-TIME", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Accumulates incrementally"},
        {"feature_name": "bot_version", "source_table": "dim_bot", "data_type": "str", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": 5, "ml_allowed": True, "leakage_risk": False, "reason": "Pre-call config"},
        {"feature_name": "campaign_key", "source_table": "fact_calls", "data_type": "int", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": 10, "ml_allowed": True, "leakage_risk": False, "reason": "Pre-call config"},
        {"feature_name": "campaign_type", "source_table": "dim_campaign", "data_type": "str", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": 5, "ml_allowed": True, "leakage_risk": False, "reason": "Pre-call config"},
        {"feature_name": "language", "source_table": "dim_bot", "data_type": "str", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": 3, "ml_allowed": True, "leakage_risk": False, "reason": "Pre-call config"},
        {"feature_name": "dpd_bucket_at_call", "source_table": "fact_calls", "data_type": "str", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": 5, "ml_allowed": True, "leakage_risk": False, "reason": "Snapshot before call"},
        {"feature_name": "days_past_due_at_call", "source_table": "fact_calls", "data_type": "int", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Snapshot before call"},
        {"feature_name": "risk_segment_at_call", "source_table": "fact_calls", "data_type": "str", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": 3, "ml_allowed": True, "leakage_risk": False, "reason": "Snapshot before call"},
        {"feature_name": "outstanding_amount_at_call", "source_table": "fact_calls", "data_type": "float", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "Snapshot before call"},
        {"feature_name": "previous_call_count", "source_table": "derived", "data_type": "int", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "History"},
        {"feature_name": "previous_escalation_count", "source_table": "derived", "data_type": "int", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "History"},
        {"feature_name": "previous_fallback_count", "source_table": "derived", "data_type": "int", "availability_timing": "HISTORICAL PRE-CALL", "missing_percentage": 0, "cardinality": -1, "ml_allowed": True, "leakage_risk": False, "reason": "History"}
    ]
    prohibited = [
        {"feature_name": "expected_intent_key", "source_table": "fact_conversation", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "escalation_trigger_flag", "source_table": "fact_conversation", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "escalation_flag", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "escalation_target", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "resolution_flag", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "task_completed_flag", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "containment_flag", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "ptp_flag", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "payment_status", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "payment_amount", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"},
        {"feature_name": "hangup_reason", "source_table": "fact_calls", "ml_allowed": False, "leakage_risk": True, "reason": "POST-CALL / TARGET LEAKAGE"}
    ]
    return {"allowed": allowed, "prohibited": prohibited}
''')

if __name__ == '__main__':
    gen2()
