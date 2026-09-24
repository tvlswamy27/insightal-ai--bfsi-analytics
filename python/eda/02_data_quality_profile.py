def run_quality_profile(df_calls, df_conv, df_cust):
    return {
        'calls': {'row_count': len(df_calls), 'duplicate_rows': int(df_calls.duplicated().sum())},
        'conversations': {'row_count': len(df_conv), 'duplicate_rows': int(df_conv.duplicated().sum())},
        'customers': {'row_count': len(df_cust), 'duplicate_rows': int(df_cust.duplicated().sum())}
    }
