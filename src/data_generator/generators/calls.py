import pandas as pd
import numpy as np
from src.data_generator.random_state import get_rng
from src.data_generator.config import config
from src.data_generator.utils.ids import generate_uuids

def generate_preliminary_calls(customers, campaigns, bots, dates):
    rng = get_rng()
    num_calls = config.dataset.get('calls', 100)
    
    customer_indices = rng.choice(len(customers), size=num_calls)
    chosen_customers = customers.iloc[customer_indices].copy().reset_index(drop=True)
    
    campaign_indices = rng.choice(len(campaigns), size=num_calls)
    chosen_campaigns = campaigns.iloc[campaign_indices].copy().reset_index(drop=True)
    
    bot_indices = rng.choice(len(bots), size=num_calls)
    chosen_bots = bots.iloc[bot_indices].copy().reset_index(drop=True)
    
    start_dt = pd.to_datetime(config.dataset.get('start_date', '2026-01-01'))
    end_dt = pd.to_datetime(config.dataset.get('end_date', '2026-06-30'))
    days_range = (end_dt - start_dt).days
    
    random_days = rng.integers(0, days_range + 1, size=num_calls)
    call_dates = start_dt + pd.to_timedelta(random_days, unit='d')
    
    random_seconds = rng.integers(8*3600, 20*3600, size=num_calls) 
    call_start_times = call_dates + pd.to_timedelta(random_seconds, unit='s')
    
    df = pd.DataFrame({
        'call_key': range(1, num_calls + 1),
        'call_id': generate_uuids(num_calls),
        'customer_key': chosen_customers['customer_key'],
        'campaign_key': chosen_campaigns['campaign_key'],
        'bot_key': chosen_bots['bot_key'],
        'call_start_time': call_start_times,
    })
    
    df['date_key'] = df['call_start_time'].dt.strftime('%Y%m%d').astype(int)
    
    df = df.sort_values(by=['customer_key', 'campaign_key', 'call_start_time']).reset_index(drop=True)
    
    df['attempt_number'] = df.groupby(['customer_key', 'campaign_key']).cumcount() + 1
    
    conn_probs = np.where(df['attempt_number'] == 1, 0.7, 
                   np.where(df['attempt_number'] == 2, 0.5, 0.3))
    
    rands = rng.random(size=num_calls)
    df['connection_status'] = np.where(rands < conn_probs, 'Connected', 'No Answer')
    
    voicemail_mask = (df['connection_status'] == 'No Answer') & (rng.random(size=num_calls) < 0.3)
    df.loc[voicemail_mask, 'connection_status'] = 'Voicemail'
    
    failed_mask = (df['connection_status'] == 'No Answer') & (rng.random(size=num_calls) < 0.1)
    df.loc[failed_mask, 'connection_status'] = 'Failed'
    
    df['days_past_due_at_call'] = np.where(rng.random(size=num_calls) < 0.4, 
                                           rng.integers(0, 120, size=num_calls), 0)
    
    def get_dpd_bucket(dpd):
        if dpd == 0: return '0'
        if dpd <= 30: return '1-30'
        if dpd <= 60: return '31-60'
        if dpd <= 90: return '61-90'
        return '90+'
        
    df['dpd_bucket_at_call'] = df['days_past_due_at_call'].apply(get_dpd_bucket)
    df['outstanding_amount_at_call'] = np.where(df['days_past_due_at_call'] > 0, 
                                                rng.normal(50000, 20000, size=num_calls).clip(min=1000), 0)
    
    df['risk_segment_at_call'] = np.where(df['days_past_due_at_call'] > 60, 'High',
                                 np.where(df['days_past_due_at_call'] > 30, 'Medium', 'Low'))
                                 
    return df
