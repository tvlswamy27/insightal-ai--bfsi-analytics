import os
import pandas as pd
import numpy as np
from src.data_generator.config import config
from src.data_generator.random_state import get_rng, RandomState
from src.data_generator.generators.customers import generate_customers
from src.data_generator.generators.intents import generate_intents
from src.data_generator.generators.bots import generate_bots
from src.data_generator.generators.campaigns import generate_campaigns
from src.data_generator.generators.dates import generate_dates
from src.data_generator.generators.calls import generate_preliminary_calls
from src.data_generator.generators.conversations import generate_conversations
from src.data_generator.quality.anomaly_injector import process_raw_data
from src.data_generator.quality.validator import run_validation

def ensure_dirs():
    dirs = ['data/raw', 'data/clean', 'data/validation']
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def generate_dataset():
    ensure_dirs()
    print("Generating Dimensions...")
    dates_df = generate_dates()
    intents_df = generate_intents()
    bots_df = generate_bots()
    campaigns_df = generate_campaigns()
    customers_df = generate_customers()
    
    print("Generating Preliminary Calls...")
    calls_df = generate_preliminary_calls(customers_df, campaigns_df, bots_df, dates_df)
    
    print("Generating Conversations...")
    turns_df = generate_conversations(calls_df, intents_df, bots_df)
    
    print("Computing Point-in-Time Features and Escalation...")
    rng = get_rng()
    
    calls_df['fallback_flag'] = 0
    calls_df['confidence_score'] = np.nan
    calls_df['sentiment'] = None
    calls_df['sentiment_score'] = np.nan
    calls_df['escalation_flag'] = 0
    calls_df['call_duration_seconds'] = 0
    calls_df['call_end_time'] = calls_df['call_start_time']
    calls_df['task_started_flag'] = 0
    calls_df['task_completed_flag'] = 0
    calls_df['resolution_flag'] = 0
    calls_df['containment_flag'] = 0
    calls_df['ptp_flag'] = 0
    calls_df['ptp_amount'] = np.nan
    calls_df['payment_status'] = None
    calls_df['payment_amount'] = np.nan
    calls_df['hangup_reason'] = None
    calls_df['call_status'] = 'Failed'
    
    non_conn = calls_df['connection_status'] != 'Connected'
    calls_df.loc[non_conn, 'call_duration_seconds'] = rng.integers(0, 15, size=non_conn.sum())
    calls_df.loc[non_conn, 'call_end_time'] = calls_df.loc[non_conn, 'call_start_time'] + pd.to_timedelta(calls_df.loc[non_conn, 'call_duration_seconds'], unit='s')
    calls_df.loc[non_conn, 'hangup_reason'] = 'Network Drop'
    calls_df.loc[calls_df['connection_status'] == 'Voicemail', 'hangup_reason'] = 'Voicemail'
    
    if not turns_df.empty:
        cust_turns = turns_df[turns_df['speaker'] == 'Customer']
        
        fallback_counts = cust_turns.groupby('call_key')['fallback_flag'].sum()
        conf_avgs = cust_turns.groupby('call_key')['confidence_score'].mean()
        sent_avgs = cust_turns.groupby('call_key')['sentiment_score'].mean()
        turn_counts = turns_df.groupby('call_key')['turn_number'].max()
        last_turn_times = turns_df.groupby('call_key')['timestamp'].max()
        
        first_intent = cust_turns.dropna(subset=['expected_intent_key']).groupby('call_key')['expected_intent_key'].first()
        
        calls_df.set_index('call_key', inplace=True)
        calls_df['intent_key'] = first_intent.reindex(calls_df.index).astype('Int64')
        calls_df['fallback_flag'] = fallback_counts.reindex(calls_df.index).fillna(0).apply(lambda x: 1 if x > 0 else 0)
        calls_df['fallback_count_so_far'] = fallback_counts.reindex(calls_df.index).fillna(0)
        calls_df['confidence_score'] = conf_avgs.reindex(calls_df.index)
        calls_df['sentiment_score'] = sent_avgs.reindex(calls_df.index)
        
        def get_sent(s):
            if pd.isna(s): return None
            if s > 0.3: return 'Positive'
            if s < -0.3: return 'Negative'
            return 'Neutral'
            
        calls_df['sentiment'] = calls_df['sentiment_score'].apply(get_sent)
        
        logit = -3.0 \
                + calls_df['fallback_count_so_far'] * 1.5 \
                + (1.0 - calls_df['confidence_score'].fillna(1.0)) * 2.0 \
                - calls_df['sentiment_score'].fillna(0) * 2.0 \
                + (calls_df['attempt_number'] - 1) * 0.5 \
                + (calls_df['days_past_due_at_call'] / 100.0)
                
        esc_prob = sigmoid_safe(logit)
        esc_prob += rng.normal(0, 0.1, size=len(esc_prob))
        calls_df['escalation_flag'] = np.where((esc_prob > 0.5) & (calls_df['connection_status'] == 'Connected'), 1, 0)
        
        connected_idx = calls_df[calls_df['connection_status'] == 'Connected'].index
        
        calls_df.loc[connected_idx, 'task_started_flag'] = 1
        
        tc_logit = 1.0 - calls_df.loc[connected_idx, 'escalation_flag'] * 3.0 + (calls_df.loc[connected_idx, 'confidence_score'].fillna(0.5) - 0.5) * 2.0
        tc_prob = sigmoid_safe(tc_logit)
        calls_df.loc[connected_idx, 'task_completed_flag'] = (rng.random(len(tc_prob)) < tc_prob).astype(int)
        
        calls_df.loc[connected_idx, 'containment_flag'] = np.where(calls_df.loc[connected_idx, 'escalation_flag'] == 1, 0,
                                                                  calls_df.loc[connected_idx, 'task_completed_flag'])
        
        res_logit = -2.0 + calls_df.loc[connected_idx, 'containment_flag'] * 3.0 + calls_df.loc[connected_idx, 'task_completed_flag'] * 1.5 + calls_df.loc[connected_idx, 'sentiment_score'].fillna(0) * 1.0
        res_prob = sigmoid_safe(res_logit)
        calls_df.loc[connected_idx, 'resolution_flag'] = (rng.random(len(res_prob)) < res_prob).astype(int)
        
        calls_df['last_turn_time'] = last_turn_times.reindex(calls_df.index)
        calls_df.loc[connected_idx, 'call_end_time'] = calls_df.loc[connected_idx, 'last_turn_time'] + pd.to_timedelta(rng.integers(5, 30, size=len(connected_idx)), unit='s')
        calls_df['call_duration_seconds'] = (calls_df['call_end_time'] - calls_df['call_start_time']).dt.total_seconds().fillna(0).astype(int)
        
        coll_mask = (calls_df['campaign_key'].map(campaigns_df.set_index('campaign_key')['campaign_type']) == 'Loan Collections') & (calls_df['connection_status'] == 'Connected')
        
        ptp_logit = -1.0 - (calls_df.loc[coll_mask, 'days_past_due_at_call'] / 50.0) + calls_df.loc[coll_mask, 'task_completed_flag'] * 2.0
        ptp_prob = sigmoid_safe(ptp_logit)
        
        calls_df.loc[coll_mask, 'ptp_flag'] = (rng.random(len(ptp_prob)) < ptp_prob).astype(int)
        
        has_ptp = calls_df['ptp_flag'] == 1
        calls_df.loc[has_ptp, 'ptp_amount'] = (calls_df.loc[has_ptp, 'outstanding_amount_at_call'] * rng.uniform(0.1, 1.0, size=has_ptp.sum())).round(2).clip(lower=1.0)
        
        pay_logit = ptp_logit 
        pay_prob = sigmoid_safe(pay_logit)
        
        calls_df.loc[has_ptp, 'payment_status'] = np.where(rng.random(has_ptp.sum()) < pay_prob.reindex(calls_df[has_ptp].index), 'Success', 'Failed')
        succ_pay = calls_df['payment_status'] == 'Success'
        calls_df.loc[succ_pay, 'payment_amount'] = calls_df.loc[succ_pay, 'ptp_amount']
        
        calls_df.loc[connected_idx, 'hangup_reason'] = np.where(calls_df.loc[connected_idx, 'escalation_flag'] == 1, 'Transferred to Agent',
                                                       np.where(calls_df.loc[connected_idx, 'resolution_flag'] == 1, 'Customer Hung Up', 'System Error'))
                                                       
        calls_df.loc[connected_idx, 'call_status'] = np.where(calls_df.loc[connected_idx, 'resolution_flag'] == 1, 'Completed', 'Failed')
        
        calls_df['identity_verified_flag'] = np.where(calls_df['connection_status'] == 'Connected', 1, 0)
        
        calls_df.reset_index(inplace=True)
        
        esc_calls = calls_df[calls_df['escalation_flag'] == 1]['call_key']
        
        for ck in esc_calls:
            turn_idx = turns_df[turns_df['call_key'] == ck].index
            if not turn_idx.empty:
                last_idx = turn_idx[-1]
                turns_df.at[last_idx, 'escalation_trigger_flag'] = 1

    if 'fallback_count_so_far' in calls_df.columns:
        calls_df.drop(columns=['fallback_count_so_far', 'last_turn_time'], inplace=True)
        
    print("Saving Clean Data...")
    customers_df.to_csv('data/clean/customers.csv', index=False)
    calls_df.to_csv('data/clean/calls.csv', index=False)
    if not turns_df.empty:
        turns_df.to_csv('data/clean/conversations.csv', index=False)
        
    process_raw_data()
    run_validation()
    print("Phase 4 Pipeline Generation Complete.")
    
def sigmoid_safe(x):
    return 1 / (1 + np.exp(-x.astype(float)))

if __name__ == '__main__':
    generate_dataset()
