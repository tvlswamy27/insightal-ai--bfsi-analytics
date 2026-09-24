import pandas as pd
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
