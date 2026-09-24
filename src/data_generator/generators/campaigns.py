import pandas as pd
from src.data_generator.random_state import get_rng
from src.data_generator.config import config

def generate_campaigns():
    campaigns = [
        {'campaign_name': 'Q1 Collections', 'campaign_type': 'Loan Collections', 'business_unit': 'Retail Banking', 'start_date': '2026-01-01', 'end_date': '2026-03-31', 'target_segment': 'DPD 31-90'},
        {'campaign_name': 'Q2 Collections', 'campaign_type': 'Loan Collections', 'business_unit': 'Retail Banking', 'start_date': '2026-04-01', 'end_date': '2026-06-30', 'target_segment': 'DPD 31-90'},
        {'campaign_name': 'Payment Reminder Auto', 'campaign_type': 'Payment Reminder', 'business_unit': 'Retail Banking', 'start_date': '2025-01-01', 'end_date': None, 'target_segment': 'DPD 0-30'},
        {'campaign_name': 'Spring Loan Promo', 'campaign_type': 'Loan Application', 'business_unit': 'Retail Banking', 'start_date': '2026-02-01', 'end_date': '2026-04-30', 'target_segment': 'Low Risk'},
        {'campaign_name': 'Auto Renewal Alerts', 'campaign_type': 'Insurance Renewal', 'business_unit': 'Insurance', 'start_date': '2025-01-01', 'end_date': None, 'target_segment': 'All'},
        {'campaign_name': 'General Support Inbound', 'campaign_type': 'Customer Support', 'business_unit': 'Customer Service', 'start_date': '2025-01-01', 'end_date': None, 'target_segment': 'All'},
        {'campaign_name': 'Credit Card Leads', 'campaign_type': 'Lead Qualification', 'business_unit': 'Sales', 'start_date': '2026-01-15', 'end_date': '2026-05-15', 'target_segment': 'High Value'}
    ]
    
    df = pd.DataFrame(campaigns)
    df.insert(0, 'campaign_key', range(1, len(df) + 1))
    df.insert(1, 'campaign_id', [f"CAMP_{str(i).zfill(3)}" for i in df['campaign_key']])
    df['start_date'] = pd.to_datetime(df['start_date']).dt.date
    df['end_date'] = pd.to_datetime(df['end_date']).dt.date
    return df
