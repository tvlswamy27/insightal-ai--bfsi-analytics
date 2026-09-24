import pandas as pd
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
