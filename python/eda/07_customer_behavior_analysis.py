import pandas as pd

def run_customer_behavior(df_cust):
    res = {}
    
    res['metrics_summary'] = {
        'total_calls': float(df_cust['total_calls'].sum()),
        'connected_calls': float(df_cust['connected_calls'].sum()),
        'average_duration': float(df_cust['average_duration'].mean()),
        'max_attempts': int(df_cust['max_attempts'].max()),
        'escalation_count': int(df_cust['escalation_count'].sum()),
        'fallback_count': int(df_cust['fallback_count'].sum()),
        'ptp_count': int(df_cust['ptp_count'].sum()),
        'payment_success_count': int(df_cust['payment_success_count'].sum()),
        'total_ptp_amount': float(df_cust['total_ptp_amount'].sum()),
        'total_payment_amount': float(df_cust['total_payment_amount'].sum()),
        'first_call_date': str(df_cust['first_call_date'].min()),
        'last_call_date': str(df_cust['last_call_date'].max())
    }
    
    res['distributions'] = {
        'calls_per_customer': df_cust['total_calls'].value_counts().to_dict(),
        'repeat_attempts': df_cust['max_attempts'].value_counts().to_dict(),
        'escalation_frequency': df_cust['escalation_count'].value_counts().to_dict(),
        'fallback_frequency': df_cust['fallback_count'].value_counts().to_dict(),
        'payment_success_frequency': df_cust['payment_success_count'].value_counts().to_dict(),
        'ptp_frequency': df_cust['ptp_count'].value_counts().to_dict()
    }
    
    return res
