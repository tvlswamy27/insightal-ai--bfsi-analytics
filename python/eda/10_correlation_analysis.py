import pandas as pd
from scipy.stats import spearmanr, pointbiserialr

def run_correlation(df_calls, df_conv):
    res = {}
    
    def interpret_r(r):
        v = abs(r)
        if v < 0.2: return "Negligible association"
        if v < 0.4: return "Weak association"
        if v < 0.6: return "Moderate association"
        return "Strong association"
    
    def calc_spearman(df, col1, col2, name):
        df_clean = df.dropna(subset=[col1, col2])
        if len(df_clean) > 0:
            r, p = spearmanr(df_clean[col1], df_clean[col2])
            res[name] = {
                "variables": f"{col1}, {col2}", "method": "Spearman", "n": len(df_clean),
                "coefficient": float(r), "p_value": float(p),
                "interpretation": interpret_r(r),
                "limitation": "Does not imply causality"
            }
            
    def calc_point_biserial(df, col1, col2_binary, name):
        df_clean = df.dropna(subset=[col1, col2_binary])
        if len(df_clean) > 0:
            r, p = pointbiserialr(df_clean[col2_binary], df_clean[col1])
            res[name] = {
                "variables": f"{col1}, {col2_binary}", "method": "Point-Biserial", "n": len(df_clean),
                "coefficient": float(r), "p_value": float(p),
                "interpretation": interpret_r(r),
                "limitation": "Does not imply causality"
            }
            
    calc_spearman(df_calls, 'call_duration_seconds', 'attempt_number', 'dur_vs_att')
    calc_spearman(df_conv, 'confidence_score', 'fallback_flag', 'conf_vs_fb')
    calc_spearman(df_conv, 'confidence_score', 'sentiment_score', 'conf_vs_sent')
    calc_spearman(df_calls, 'days_past_due_at_call', 'ptp_amount', 'dpd_vs_ptp_amt')
    calc_spearman(df_calls, 'outstanding_amount_at_call', 'payment_amount', 'outst_vs_pay')
    
    # Needs call level merge for escalation vs conversation aggregates
    agg = df_conv.groupby('call_key').agg(
        avg_sentiment=('sentiment_score', 'mean'),
        fallback_count=('fallback_flag', 'sum')
    ).reset_index()
    df_merged = df_calls[['call_key', 'escalation_flag']].merge(agg, on='call_key', how='inner')
    
    calc_point_biserial(df_merged, 'avg_sentiment', 'escalation_flag', 'sent_vs_esc')
    calc_point_biserial(df_merged, 'fallback_count', 'escalation_flag', 'fb_count_vs_esc')
    
    return res
