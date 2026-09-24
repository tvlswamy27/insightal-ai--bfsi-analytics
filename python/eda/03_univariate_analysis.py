import pandas as pd
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
