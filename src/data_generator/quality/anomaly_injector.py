import pandas as pd
import numpy as np
from src.data_generator.random_state import get_rng
from src.data_generator.config import config
import os

def inject_anomalies(df, table_name, columns_to_corrupt=None):
    rng = get_rng()
    anomaly_rate = config.quality.get('anomaly_rate', 0.02)
    dist = config.quality.get('anomaly_distribution', {})
    
    num_rows = len(df)
    num_anomalies = int(num_rows * anomaly_rate)
    
    if num_anomalies == 0:
        return df, []
        
    df_raw = df.copy()
    manifest_entries = []
    
    types = list(dist.keys())
    probs = list(dist.values())
    probs = np.array(probs) / sum(probs)
    
    chosen_types = rng.choice(types, size=num_anomalies, p=probs)
    chosen_indices = rng.choice(df_raw.index, size=num_anomalies, replace=False)
    
    for i, idx in enumerate(chosen_indices):
        atype = chosen_types[i]
        col = rng.choice(columns_to_corrupt) if columns_to_corrupt else df_raw.columns[0]
        orig_val = df_raw.at[idx, col]
        corrupted_val = orig_val
        
        if atype == 'missing_value':
            df_raw.at[idx, col] = np.nan
            corrupted_val = np.nan
        elif atype == 'duplicate':
            dup_row = df_raw.loc[[idx]].copy()
            df_raw = pd.concat([df_raw, dup_row], ignore_index=True)
            corrupted_val = "ROW_DUPLICATED"
        elif atype == 'invalid_numeric' and pd.api.types.is_numeric_dtype(df_raw[col]):
            corrupted_val = orig_val * -1 if orig_val != 0 else -999
            df_raw.at[idx, col] = corrupted_val
        elif atype == 'invalid_timestamp':
            df_raw.at[idx, col] = pd.NaT 
            corrupted_val = "NaT"
        elif atype == 'invalid_foreign_key':
            corrupted_val = orig_val + 999999 if pd.api.types.is_numeric_dtype(df_raw[col]) else f"{orig_val}_BAD"
            df_raw.at[idx, col] = corrupted_val
            
        manifest_entries.append({
            'table': table_name,
            'row_identifier': idx,
            'anomaly_type': atype,
            'column': col,
            'original_value': str(orig_val),
            'corrupted_value': str(corrupted_val),
            'random_seed': config.dataset.get('random_seed', 42)
        })
        
    return df_raw, manifest_entries

def process_raw_data():
    ensure_dirs = ['data/raw', 'data/validation']
    for d in ensure_dirs:
        os.makedirs(d, exist_ok=True)
        
    print("Injecting Anomalies...")
    cust = pd.read_csv('data/clean/customers.csv')
    calls = pd.read_csv('data/clean/calls.csv')
    conv = pd.read_csv('data/clean/conversations.csv')
    
    cust_raw, man1 = inject_anomalies(cust, 'raw_customers', ['age', 'customer_type', 'city'])
    calls_raw, man2 = inject_anomalies(calls, 'raw_calls', ['call_duration_seconds', 'customer_key', 'call_start_time', 'days_past_due_at_call'])
    conv_raw, man3 = inject_anomalies(conv, 'raw_conversations', ['call_key', 'confidence_score', 'timestamp'])
    
    cust_raw.to_csv('data/raw/raw_customers.csv', index=False)
    calls_raw.to_csv('data/raw/raw_calls.csv', index=False)
    conv_raw.to_csv('data/raw/raw_conversations.csv', index=False)
    
    manifest = pd.DataFrame(man1 + man2 + man3)
    manifest.to_csv('data/validation/anomaly_manifest.csv', index=False)
    print("Raw Data and Manifest Saved.")
