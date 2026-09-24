import pandas as pd
import numpy as np
from src.data_generator.random_state import get_rng
from src.data_generator.config import config
from src.data_generator.utils.ids import generate_uuids

def generate_customers():
    rng = get_rng()
    num_customers = config.dataset.get('customers', 1000)
    
    geo_pool = [
        ('Maharashtra', 'Mumbai', 0.20),
        ('Karnataka', 'Bengaluru', 0.15),
        ('Delhi', 'Delhi', 0.15),
        ('Telangana', 'Hyderabad', 0.10),
        ('Tamil Nadu', 'Chennai', 0.10),
        ('Maharashtra', 'Pune', 0.08),
        ('Haryana', 'Gurugram', 0.05),
        ('Uttar Pradesh', 'Noida', 0.04),
        ('Gujarat', 'Ahmedabad', 0.04),
        ('West Bengal', 'Kolkata', 0.04),
        ('Rajasthan', 'Jaipur', 0.02),
        ('Kerala', 'Kochi', 0.01),
        ('Andhra Pradesh', 'Vijayawada', 0.01),
        ('Andhra Pradesh', 'Visakhapatnam', 0.01)
    ]
    
    states = [item[0] for item in geo_pool]
    cities = [item[1] for item in geo_pool]
    geo_weights = [item[2] for item in geo_pool]
    geo_weights = np.array(geo_weights) / sum(geo_weights)
    
    chosen_geo_idx = rng.choice(len(geo_pool), size=num_customers, p=geo_weights)
    ages = np.clip(rng.normal(loc=38, scale=12, size=num_customers).astype(int), 18, 80)
    genders = rng.choice(['M', 'F', 'O'], size=num_customers, p=[0.55, 0.44, 0.01])
    customer_types = rng.choice(['Retail', 'SME', 'Corporate'], size=num_customers, p=[0.85, 0.10, 0.05])
    customer_segments = rng.choice(['Mass', 'Premium', 'High Value', 'Wealth'], size=num_customers, p=[0.60, 0.25, 0.10, 0.05])
    loan_types = rng.choice(['Personal Loan', 'Credit Card', 'Home Loan', 'Auto Loan', 'None'], size=num_customers, p=[0.35, 0.40, 0.10, 0.10, 0.05])
    base_dates = pd.to_datetime('2026-01-01') - pd.to_timedelta(rng.integers(0, 2000, num_customers), unit='d')
    
    df = pd.DataFrame({
        'customer_id': generate_uuids(num_customers),
        'age': ages,
        'gender': genders,
        'state': np.array(states)[chosen_geo_idx],
        'city': np.array(cities)[chosen_geo_idx],
        'customer_type': customer_types,
        'customer_segment': customer_segments,
        'loan_type': loan_types,
        'customer_since_date': base_dates.date
    })
    
    df.insert(0, 'customer_key', range(1, num_customers + 1))
    
    def get_age_group(age):
        if age <= 25: return '18-25'
        if age <= 35: return '26-35'
        if age <= 45: return '36-45'
        if age <= 55: return '46-55'
        if age <= 65: return '56-65'
        return '65+'
    
    df['age_group'] = df['age'].apply(get_age_group)
    
    region_map = {
        'Maharashtra': 'West', 'Gujarat': 'West',
        'Karnataka': 'South', 'Telangana': 'South', 'Andhra Pradesh': 'South', 'Tamil Nadu': 'South', 'Kerala': 'South',
        'Delhi': 'North', 'Haryana': 'North', 'Uttar Pradesh': 'North', 'Rajasthan': 'North', 'Punjab': 'North',
        'West Bengal': 'East', 'Madhya Pradesh': 'Central'
    }
    df['region'] = df['state'].map(region_map)
    
    return df
