import pandas as pd
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
