import pandas as pd

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

    cols = [
        'average_confidence', 'fallback_count', 'average_sentiment_score',
        'call_duration_seconds', 'turn_count', 'attempt_number',
        'days_past_due_at_call', 'risk_segment_at_call', 'customer_segment',
        'campaign_name', 'bot_name', 'language'
    ]
    
    associations = {}
    for c in cols:
        if c not in df.columns: continue
        # Calculate rates by quantiles or categorical bins
        df_clean = df.dropna(subset=[c, 'escalation_flag']).copy()
        if len(df_clean) == 0: continue
        
        if df_clean[c].nunique() > 10 and pd.api.types.is_numeric_dtype(df_clean[c]):
            df_clean['q'] = pd.qcut(df_clean[c], 4, duplicates='drop')
            grp = df_clean.groupby('q', observed=True)['escalation_flag'].mean()
            # Convert interval index to string
            grp.index = grp.index.astype(str)
            associations[c] = grp.to_dict()
        else:
            associations[c] = df_clean.groupby(c)['escalation_flag'].mean().to_dict()

    return {
        "merged_count": len(df),
        "merged_unique": df['call_key'].nunique(),
        "associations": associations
    }
